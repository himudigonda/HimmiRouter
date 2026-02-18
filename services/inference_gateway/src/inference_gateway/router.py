from typing import TypedDict

import litellm
from langgraph.graph import END, StateGraph


class GatewayState(TypedDict):
    api_key: str
    user_id: int
    model_slug: str
    prompt: str
    provider_mapping: dict
    usage: dict
    response: str


async def auth_node(state: GatewayState):
    # Logic: Verify key_hash in DB, check credits
    return {"user_id": 1}


async def route_node(state: GatewayState):
    # Logic: Find best ModelProviderMapping in DB
    return {"provider_mapping": {"provider": "openai", "cost": 10}}


async def call_llm_node(state: GatewayState):
    # Logic: LiteLLM proxy call
    response = await litellm.acompletion(
        model=state["provider_mapping"]["model_name"],
        messages=[{"role": "user", "content": state["prompt"]}],
    )
    return {"response": response.choices[0].message.content, "usage": response.usage}


async def billing_node(state: GatewayState):
    # Logic: SELECT FOR UPDATE user credits, deduct (usage * cost)
    return state


# Graph Construction
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
