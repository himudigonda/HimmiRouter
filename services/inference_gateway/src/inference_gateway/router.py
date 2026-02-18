import asyncio
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, TypedDict

import litellm
from database.models import ApiKey, Model, ModelProviderMapping, Provider, User
from database.session import engine
from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


class GatewayState(TypedDict):
    # Inputs
    raw_api_key: str
    model_slug: str
    messages: List[dict]

    # Internal State
    user_id: Optional[int]
    api_key_id: Optional[int]
    provider_info: Optional[dict]
    costs: Optional[dict]  # input_token_cost, output_token_cost

    # Outputs
    response_content: Optional[str]
    usage: Optional[dict]
    error: Optional[str]


# --- NODES ---


async def auth_node(state: GatewayState):
    """Verifies the API key and checks user credit balance."""
    key_hash = hashlib.sha256(state["raw_api_key"].encode()).hexdigest()

    # Use expire_on_commit=False to avoid MissingGreenlet when accessing attributes later
    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Find Key and User
        statement = select(ApiKey, User).where(
            ApiKey.key_hash == key_hash,
            ApiKey.disabled == False,
            ApiKey.deleted == False,
            ApiKey.user_id == User.id,
        )
        result = await session.execute(statement)
        pair = result.first()

        if not pair:
            return {"error": "Invalid or disabled API Key"}

        api_key_db, user_db = pair

        if user_db.credits <= 0:
            return {"error": "Insufficient credits"}

        return {"user_id": user_db.id, "api_key_id": api_key_db.id, "error": None}


async def route_node(state: GatewayState):
    """Finds the model costs and the specific provider to use."""
    if state.get("error"):
        return state

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Find Model and its first available mapping
        statement = select(Model, ModelProviderMapping, Provider).where(
            Model.slug == state["model_slug"],
            ModelProviderMapping.model_id == Model.id,
            ModelProviderMapping.provider_id == Provider.id,
        )
        result = await session.execute(statement)
        row = result.first()

        if not row:
            return {"error": "Model not supported or mapping missing"}

        model_db, mapping_db, provider_db = row

        # We store the provider details and costs for the billing node
        return {
            "provider_info": {
                "name": provider_db.name,
                "model_name": state["model_slug"].split("/")[-1],  # e.g. "gpt-4o"
            },
            "costs": {
                "input": mapping_db.input_token_cost,
                "output": mapping_db.output_token_cost,
                "mapping_id": mapping_db.id,
            },
        }


async def call_llm_node(state: GatewayState):
    """Proxies the request to the upstream provider via LiteLLM."""
    if state.get("error"):
        return state

    try:
        # LiteLLM handles the standardized call
        provider_name = state["provider_info"]["name"].lower()
        model_name = state["provider_info"]["model_name"]

        response = await litellm.acompletion(
            model=f"{provider_name}/{model_name}", messages=state["messages"]
        )

        return {
            "response_content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        }
    except Exception as e:
        return {"error": f"LLM Provider Error: {str(e)}"}


async def billing_node(state: GatewayState):
    """Deducts credits using Row-Level Locking (Atomic)."""
    if state.get("error") or not state.get("usage"):
        return state

    usage = state["usage"]
    costs = state["costs"]

    # Calculate total cost (units)
    total_cost = (
        (usage["prompt_tokens"] * costs["input"])
        + (usage["completion_tokens"] * costs["output"])
    ) // 10

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Lock the user row for atomic update
        user_stmt = select(User).where(User.id == state["user_id"]).with_for_update()
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one()

        # Update user balance
        user.credits -= total_cost

        # Update API Key stats
        api_key_stmt = (
            select(ApiKey).where(ApiKey.id == state["api_key_id"]).with_for_update()
        )
        api_key_res = await session.execute(api_key_stmt)
        api_key = api_key_res.scalar_one()

        api_key.credits_consumed += total_cost
        api_key.last_used = datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()

    return state


# --- Graph Assembly ---
workflow = StateGraph(GatewayState)
workflow.add_node("auth", auth_node)
workflow.add_node("route", route_node)
workflow.add_node("llm", call_llm_node)
workflow.add_node("billing", billing_node)

workflow.set_entry_point("auth")

workflow.add_edge("auth", "route")
workflow.add_edge("route", "llm")
workflow.add_edge("llm", "billing")
workflow.add_edge("billing", END)

gateway_app = workflow.compile()
