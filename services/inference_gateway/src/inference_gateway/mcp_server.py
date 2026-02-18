
from inference_gateway.router import gateway_app
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
# This allows external agents (Claude, Cursor) to use HimmiRouter tools
mcp = FastMCP("HimmiRouter")


@mcp.tool()
async def chat_with_model(api_key: str, model: str, prompt: str) -> str:
    """
    Access any LLM via HimmiRouter gateway.

    Args:
        api_key: Your HimmiRouter sk-or-v1 API Key.
        model: The model slug to use (e.g., 'openai/gpt-4o', 'anthropic/claude-3-5-sonnet').
        prompt: The message content to send to the model.
    """
    inputs = {
        "raw_api_key": api_key,
        "model_slug": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }

    # We use our compiled LangGraph for the heavy lifting
    result = await gateway_app.ainvoke(inputs)

    if result.get("error"):
        return f"Error: {result['error']}"

    return result["response_content"]
