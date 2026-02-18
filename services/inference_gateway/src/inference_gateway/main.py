import json
from typing import List, Optional

from database.models import RequestLog
from database.session import engine
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from inference_gateway.mcp_server import mcp
from inference_gateway.router import gateway_app
from pydantic import BaseModel
from shared.instrumentation import instrument_app
from sqlmodel.ext.asyncio.session import AsyncSession

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


async def log_request_task(result: dict):
    """Background task to save request logs."""
    # If error occurred, result might be partial.
    if result.get("error"):
        # We can still log errors if we have user_id
        return

    try:
        user_id = result.get("user_id")
        api_key_id = result.get("api_key_id")

        if not user_id or not api_key_id:
            return

        usage = result.get("usage") or {"prompt_tokens": 0, "completion_tokens": 0}
        costs = result.get("costs") or {"input": 0.0, "output": 0.0}

        input_cost = (usage["prompt_tokens"] / 1_000_000.0) * costs["input"]
        output_cost = (usage["completion_tokens"] / 1_000_000.0) * costs["output"]
        total_cost = input_cost + output_cost

        # For streaming, usage might be 0 here because stream hasn't finished.
        # Ideally, we'd log *after* stream, but that requires more complex architecture.
        # For Phase 8/10 MVP, logging start/latency is key.

        log_entry = RequestLog(
            user_id=user_id,
            api_key_id=api_key_id,
            model_slug=result.get("model_slug", "unknown"),
            provider_name=result.get("provider_info", {}).get("name", "unknown"),
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            cost=total_cost,
            latency_ms=result.get("latency_ms", 0),
            status_code=200,
            is_cached=False,  # Placeholder for generic caching
        )

        async with AsyncSession(engine, expire_on_commit=False) as session:
            session.add(log_entry)
            await session.commit()

    except Exception as e:
        print(f"Logging Failed: {e}")


async def sse_generator(stream_iterator):
    """Formats chunks into SSE events."""
    try:
        async for chunk in stream_iterator:
            if hasattr(chunk, "model_dump"):
                data = chunk.model_dump()
            elif hasattr(chunk, "dict"):
                data = chunk.dict()
            else:
                data = chunk
            yield f"data: {json.dumps(data, default=str)}\n\n"
    except Exception as e:
        print(f"Streaming Error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )

    api_key = authorization.replace("Bearer ", "")

    inputs = {
        "raw_api_key": api_key,
        "model_slug": request.model,
        "messages": [m.model_dump() for m in request.messages],
        "stream": request.stream,
    }

    result = await gateway_app.ainvoke(inputs)

    if result.get("error"):
        raise HTTPException(status_code=403, detail=result["error"])

    # Trigger logging in background
    # Note: For streaming requests, this logs *initial* state (latency to first token).
    # Token usage will be 0. Real usage is updated in DB by billing_node logic.
    # We accept this dual-write/incomplete log for streams for now.
    background_tasks.add_task(log_request_task, result)

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
