import json
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from inference_gateway.mcp_server import mcp
from inference_gateway.router import gateway_app
from pydantic import BaseModel
from shared.instrumentation import instrument_app

app = FastAPI(title="OpenRouter Inference Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

instrument_app(app, "inference-gateway")
app.mount("/mcp", mcp.sse_app())


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False


@app.get("/health")
async def health():
    return {"status": "healthy"}


async def sse_generator(stream_iterator):
    """Formats chunks into SSE events."""
    async for chunk in stream_iterator:
        # LiteLLM chunk transformation to OpenAI-style SSE
        # In a real app we'd format this systematically
        yield f"data: {json.dumps(chunk.model_dump())}\n\n"
    yield "data: [DONE]\n\n"


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
        "stream": request.stream,
    }

    result = await gateway_app.ainvoke(inputs)

    if result.get("error"):
        raise HTTPException(status_code=403, detail=result["error"])

    if request.stream and result.get("stream_iterator"):
        return StreamingResponse(
            sse_generator(result["stream_iterator"]), media_type="text/event-stream"
        )

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
