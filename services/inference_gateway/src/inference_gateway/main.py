from typing import List

from fastapi import FastAPI, Header, HTTPException
from inference_gateway.router import gateway_app
from pydantic import BaseModel
from shared.instrumentation import instrument_app

app = FastAPI(title="OpenRouter Inference Gateway")

instrument_app(app, "inference-gateway")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )

    api_key = authorization.replace("Bearer ", "")

    # Invoke the LangGraph
    inputs = {
        "raw_api_key": api_key,
        "model_slug": request.model,
        "messages": [m.model_dump() for m in request.messages],
    }

    result = await gateway_app.ainvoke(inputs)

    if result.get("error"):
        raise HTTPException(status_code=403, detail=result["error"])

    return {
        "id": "chatcmpl-" + str(result.get("user_id", "unknown")),
        "object": "chat.completion",
        "model": result["model_slug"],
        "choices": [
            {
                "message": {"role": "assistant", "content": result["response_content"]},
                "finish_reason": "stop",
                "index": 0,
            }
        ],
        "usage": result["usage"],
    }
