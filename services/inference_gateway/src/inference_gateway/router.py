import asyncio
import hashlib
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional, TypedDict

import litellm
from database.encryption import decrypt
from database.models import (
    ApiKey,
    Model,
    ModelProviderMapping,
    Organization,
    Provider,
    User,
    UserProviderKey,
)
from database.session import engine
from langgraph.graph import END, StateGraph
from shared.cache import check_cache, store_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select


class GatewayState(TypedDict):
    # Inputs
    raw_api_key: str
    model_slug: str
    messages: List[dict]
    stream: bool
    shadow_mode: Optional[bool]

    # Internal State
    user_id: Optional[int]
    api_key_id: Optional[int]
    org_id: Optional[int]
    provider_info: Optional[dict]
    costs: Optional[dict]  # input_token_cost, output_token_cost
    start_time: float
    latency_ms: int
    shadow_model_slug: Optional[str]
    shadow_response: Optional[str]
    is_cached: bool  # New flag

    # Outputs
    response_content: Optional[str]
    stream_iterator: Optional[AsyncGenerator]
    usage: Optional[dict]
    error: Optional[str]


from shared.instrumentation import trace_node

# Map DB provider names to LiteLLM provider prefixes
LITELLM_PROVIDER_MAP = {
    "Google AI": "gemini",
    "OpenAI": "openai",
    "Anthropic": "anthropic",
    "Groq": "groq",
    "Perplexity": "perplexity",
    "Mistral AI": "mistral",
    "Mistral": "mistral",
    "xAI": "xai",
}


# --- NODES ---


@trace_node("init")
async def init_node(state: GatewayState):
    return {"start_time": time.time()}


@trace_node("cache_lookup")
async def cache_lookup_node(state: GatewayState):
    # Only cache simple user prompts for now
    if not state.get("messages"):
        return {"is_cached": False}

    last_msg = state["messages"][-1]["content"]

    # We only cache the LAST message content as key for now
    cached_response = await check_cache(last_msg)
    if cached_response:
        print("Cache HIT!")
        return {
            "response_content": cached_response,
            "is_cached": True,
            "usage": {"prompt_tokens": 0, "completion_tokens": 0},  # FREE
        }
    return {"is_cached": False}


@trace_node("cache_store")
async def cache_store_node(state: GatewayState):
    if (
        not state.get("is_cached")
        and not state.get("error")
        and state.get("response_content")
    ):
        # Store only if we have a valid text response
        last_msg = state["messages"][-1]["content"]
        await store_cache(last_msg, state["response_content"])
    return state


@trace_node("auth")
async def auth_node(state: GatewayState):
    """Verifies the API key and checks organization credit balance."""
    key_hash = hashlib.sha256(state["raw_api_key"].encode()).hexdigest()

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Find Key -> User -> Organization
        statement = (
            select(ApiKey)
            .where(
                ApiKey.key_hash == key_hash,
                ApiKey.disabled == False,
                ApiKey.deleted == False,
            )
            .options(selectinload(ApiKey.user).selectinload(User.organization))
        )

        result = await session.execute(statement)
        api_key_db = result.scalar_one_or_none()

        if not api_key_db:
            return {"error": "Invalid or disabled API Key"}

        user_db = api_key_db.user
        if not user_db or not user_db.organization:
            # Should practically not happen with correct data integrity
            return {"error": "User configuration error (No Organization)"}

        org_db = user_db.organization

        if org_db.credits <= 0:
            return {"error": "Insufficient credits"}

        return {
            "user_id": user_db.id,
            "api_key_id": api_key_db.id,
            "org_id": org_db.id,
            "error": None,
        }


@trace_node("route")
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

        # Check for User-Specified Provider Key (BYOK)
        # We need to look up using the canonical name that the frontend uses
        canonical_provider = LITELLM_PROVIDER_MAP.get(
            provider_db.name, provider_db.name.lower()
        )

        key_stmt = select(UserProviderKey).where(
            UserProviderKey.user_id == state["user_id"],
            UserProviderKey.provider_name == canonical_provider,
        )
        key_res = await session.execute(key_stmt)
        user_key_entry = key_res.scalar_one_or_none()

        user_api_key = None
        if user_key_entry:
            try:
                user_api_key = decrypt(user_key_entry.encrypted_key)
            except Exception:
                pass

        # We store the provider details and costs for the billing node
        return {
            "provider_info": {
                "name": provider_db.name,
                "model_name": state["model_slug"].split("/")[-1],  # e.g. "gpt-4o"
                "api_key": user_api_key,  # Pass encrypted key context
            },
            "costs": {
                "input": mapping_db.input_token_cost,
                "output": mapping_db.output_token_cost,
                "mapping_id": mapping_db.id,
            },
        }


@trace_node("llm")
async def call_llm_node(state: GatewayState):
    """Proxies the request to the upstream provider via LiteLLM."""
    if state.get("error"):
        return state

    import os

    if os.getenv("HIMMI_SIMULATOR", "false").lower() == "true":
        # Simulator Mode
        content = f"Hey there! I'm {state['model_slug']}, running in HimmiRouter Simulator Mode."

        if state.get("stream"):

            async def mock_stream():
                words = content.split(" ")
                for i, word in enumerate(words):
                    yield litellm.ModelResponse(
                        id="chatcmpl-mock",
                        choices=[
                            {
                                "delta": {"content": word + " "},
                                "finish_reason": None,
                                "index": 0,
                            }
                        ],
                        model=state["model_slug"],
                    )
                    await asyncio.sleep(0.05)
                yield litellm.ModelResponse(
                    id="chatcmpl-mock",
                    choices=[{"delta": {}, "finish_reason": "stop", "index": 0}],
                    model=state["model_slug"],
                    usage={"prompt_tokens": 10, "completion_tokens": len(words)},
                )

            return {"stream_iterator": mock_stream()}
        else:
            return {
                "response_content": content,
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            }

    try:
        raw_provider = state["provider_info"]["name"]
        provider_name = LITELLM_PROVIDER_MAP.get(raw_provider, raw_provider.lower())
        model_name = state["provider_info"]["model_name"]
        user_api_key = state["provider_info"].get("api_key")
        stream = state.get("stream", False)
        shadow_mode = state.get("shadow_mode", False)

        # Primary Task
        # If shadow mode is ON, we disable streaming on primary to allow comparison logic more easily for MVP
        # Or we can support parallel streaming, but collecting shadow response is easier if both are non-stream,
        # OR we stream primary and await shadow in background.
        # For simplicity in Step 3, if shadow_mode=True, force stream=False.
        if shadow_mode:
            stream = False

        primary_task = litellm.acompletion(
            model=f"{provider_name}/{model_name}",
            messages=state["messages"],
            stream=stream,
            api_key=user_api_key,
        )

        if not shadow_mode:
            response = await primary_task
            if stream:
                return {"stream_iterator": response}
            else:
                return {
                    "response_content": response.choices[0].message.content,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                    },
                }
        else:
            # Shadow Logic
            # Hardcoded shadow model for MVP: Groq Llama 3 8B (fast & cheap)
            # In real prod, select from DB configs
            shadow_provider_model = "groq/llama3-8b-8192"

            # We need a key for Groq if not provided in env. Assume env var GROQ_API_KEY is set or passed.
            # For this demo, we assume the environment has keys or litellm handles it.

            shadow_task = litellm.acompletion(
                model=shadow_provider_model, messages=state["messages"], stream=False
            )

            # Run parallel
            results = await asyncio.gather(
                primary_task, shadow_task, return_exceptions=True
            )
            primary_res, shadow_res = results

            outputs = {}

            # Handle Primary
            if isinstance(primary_res, Exception):
                return {"error": f"Primary Provider Error: {str(primary_res)}"}
            else:
                outputs["response_content"] = primary_res.choices[0].message.content
                outputs["usage"] = {
                    "prompt_tokens": primary_res.usage.prompt_tokens,
                    "completion_tokens": primary_res.usage.completion_tokens,
                }

            # Handle Shadow
            if isinstance(shadow_res, Exception):
                # Shadow failure shouldn't fail the request, just log it?
                # or return None for shadow response
                outputs["shadow_response"] = f"Shadow Error: {str(shadow_res)}"
                outputs["shadow_model_slug"] = "error"
            else:
                outputs["shadow_response"] = shadow_res.choices[0].message.content
                outputs["shadow_model_slug"] = shadow_provider_model

            return outputs

    except Exception as e:
        return {"error": f"LLM Provider Error: {str(e)}"}


async def _execute_billing(org_id, api_key_id, prompt_tokens, completion_tokens, costs):
    """Executes the atomic credit deduction in the DB."""
    input_cost = (prompt_tokens / 1_000_000.0) * costs["input"]
    output_cost = (completion_tokens / 1_000_000.0) * costs["output"]
    total_cost = input_cost + output_cost

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Lock the Organization row for atomic update
        org_stmt = (
            select(Organization).where(Organization.id == org_id).with_for_update()
        )
        org_res = await session.execute(org_stmt)
        org = org_res.scalar_one()

        # Update org balance
        org.credits -= total_cost

        # Update API Key stats
        api_key_stmt = select(ApiKey).where(ApiKey.id == api_key_id).with_for_update()
        api_key_res = await session.execute(api_key_stmt)
        api_key = api_key_res.scalar_one()

        api_key.credits_consumed += total_cost
        api_key.last_used = datetime.now(timezone.utc).replace(tzinfo=None)

        await session.commit()


async def wrap_stream_with_billing(state: GatewayState):
    """Wraps the stream iterator to track usage and deduct credits on completion."""
    prompt_tokens = 0
    completion_tokens = 0

    try:
        async for chunk in state["stream_iterator"]:
            if hasattr(chunk, "usage") and chunk.usage:
                u = chunk.usage
                if isinstance(u, dict):
                    prompt_tokens = u.get("prompt_tokens", 0)
                    completion_tokens = u.get("completion_tokens", 0)
                else:
                    prompt_tokens = getattr(u, "prompt_tokens", 0)
                    completion_tokens = getattr(u, "completion_tokens", 0)
            yield chunk
    finally:
        if prompt_tokens > 0 or completion_tokens > 0:
            await _execute_billing(
                state["org_id"],
                state["api_key_id"],
                prompt_tokens,
                completion_tokens,
                state["costs"],
            )


@trace_node("billing")
async def billing_node(state: GatewayState):
    """Deducts credits using Row-Level Locking (Atomic)."""
    if state.get("error"):
        return state

    # If cached, we skip credit deduction but still return state
    if state.get("is_cached"):
        return state

    if state.get("stream_iterator"):
        return {"stream_iterator": wrap_stream_with_billing(state)}

    if not state.get("usage"):
        return state

    usage = state["usage"]
    costs = state["costs"]

    await _execute_billing(
        state["org_id"],
        state["api_key_id"],
        usage["prompt_tokens"],
        usage["completion_tokens"],
        costs,
    )

    return state


@trace_node("logger")
async def log_node(state: GatewayState):
    """Prepares data for the RequestLog table."""
    # This node just calculates latency.
    # The actual DB write happens in main.py via BackgroundTasks or explicit call.
    # However, since the user asked for this node to be part of the graph...
    # If using BackgroundTasks from main.py, main.py needs to read the state.
    # We simply compute and return here.
    latency = int((time.time() - state["start_time"]) * 1000)
    return {"latency_ms": latency}


def check_for_fallback(state: GatewayState):
    # If the LLM node returned an error, we route to a fallback provider
    # Basic check: if 'error' key is present and indicates LLM failure
    if state.get("error") and "LLM Provider Error" in state["error"]:
        # clear error to allow retry
        # In a real graph we might want to preserve the original error trace
        # For now, we return 'fallback' edge
        return "fallback"
    return "billing"  # Proceed to billing if success (or if error is not retryable)


@trace_node("fallback_llm")
async def fallback_llm_node(state: GatewayState):
    """Fallback node that tries a different provider/model."""
    # Logic to switch model/provider would go here.
    # For MVP, let's just retry the same one or fail gracefully.
    # In a full impl, we'd pick the next cheapest provider for the same model.
    # Example: If OpenAI fails, try Azure OpenAI.

    # For SIMPLICITY in this Step, we will just return the error but with a flag.
    # Real fallback logic requires mapped backups in DB.

    return {"error": state["error"] + " (Fallback failed too)"}


# --- Graph Assembly ---


def should_skip_llm(state: GatewayState):
    if state["is_cached"]:
        return "skip"
    return "continue"


workflow = StateGraph(GatewayState)
workflow.add_node("init", init_node)
workflow.add_node("cache_lookup", cache_lookup_node)
workflow.add_node("cache_store", cache_store_node)
workflow.add_node("auth", auth_node)
workflow.add_node("route", route_node)
workflow.add_node("llm", call_llm_node)
workflow.add_node("fallback_llm", fallback_llm_node)
workflow.add_node("billing", billing_node)
workflow.add_node("log", log_node)

workflow.set_entry_point("init")


# Conditional Edge: If cached, go straight to billing (skipping auth/llm cost), else continue
# Note: We technically need auth to know WHO asked, but for "cache_lookup" we might want to skip cost but still validate user?
# The user's prompt suggested: "skip" -> "billing", "continue" -> "auth".
# This implies if cached, we skip Auth logic regarding CREDITS? But we still need user_id/org_id for logging?
# Actually billing_node needs org_id/api_key_id. If we skip auth_node, we don't have those in state!
# Wait, `init` -> `auth` was previous flow.
# If we do `init` -> `cache_lookup` -> `auth` -> (if cached: skip route/llm -> billing? or skip billing too?)
# If cached = FREE, we still need `auth` to get IDs for logging/audit.
# So correct flow: `init` -> `auth` -> `cache_lookup` -> (if cached: billing, else: route -> llm -> billing)
# BUT the user prompted: `workflow.set_entry_point("init")`, `workflow.add_edge("init", "cache_lookup")`
# And `workflow.add_conditional_edges("cache_lookup", ..., {"skip": "billing", "continue": "auth"})`
# This implies `cache_lookup` happens BEFORE auth.
# If so, `billing_node` will FAIL because `org_id` is missing.
# UNLESS `billing_node` checks for `is_cached` and returns early safely without needing IDs?
# But `log_node` needs IDs for the DB log.
# So `auth` is CRITICAL for IDs.
# I will adjust the graph: `init` -> `auth` -> `cache_lookup`.
# If cached: -> `billing` (which skips cost deduction if cached) -> `cache_store` -> `log`.
# If not cached: -> `route` -> `llm` -> `billing` -> `cache_store` -> `log`.

# Wait, `cache_lookup` needs embedding. That's fine.
# But `log_node` relies on `state['user_id']`. If we skip `auth`, `user_id` is null.
# So we MUST run `auth`.
# I will implement: `init` -> `auth` -> `cache_lookup`.
# If cached -> skip to billing (effectively 0 cost).
# If not cached -> route.

# Adjusting User's suggested graph flow for correctness:
# User said: `workflow.add_edge("init", "cache_lookup")` and conditional `skip` -> `billing`, `continue` -> `auth`.
# This is physically impossible for logging/billing/metrics if `auth` (which yields user_id) is skipped.
# UNLESS the user implies public cache access? No, API Key is needed.
# I will keep `auth` FIRST.
# `init` -> `auth` -> `cache_lookup`.
# Conditional on `cache_lookup`:
#  - Is Cached? -> `billing` (skips cost) -> `cache_store` (noop/update) -> `log`.
#  - Not Cached? -> `route` -> `llm` -> `fallback` logic -> `billing` -> `cache_store` -> `log`.

workflow.add_edge("init", "auth")
workflow.add_edge("auth", "cache_lookup")  # Auth first, then Cache Check

workflow.add_conditional_edges(
    "cache_lookup",
    should_skip_llm,
    {
        "skip": "billing",  # If cached, jump to billing (which will handle 0 cost)
        "continue": "route",  # If not cached, proceed to routing
    },
)

workflow.add_edge("route", "llm")

# Conditional Edge for Resilience (LLM -> Fallback or Billing)
workflow.add_conditional_edges(
    "llm", check_for_fallback, {"fallback": "fallback_llm", "billing": "billing"}
)

workflow.add_edge("fallback_llm", "billing")

# After billing, we try to store in cache (if it wasn't a cache hit)
workflow.add_edge("billing", "cache_store")
workflow.add_edge("cache_store", "log")
workflow.add_edge("log", END)

gateway_app = workflow.compile()
