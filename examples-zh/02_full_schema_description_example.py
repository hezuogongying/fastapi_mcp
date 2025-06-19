"""
本示例展示了如何描述完整的响应 schema，而不仅仅是一个响应示例。
"""
from demo.apps.apis import app  # FastAPI 应用
from demo.core.setup import setup_logging

from fastapi_mcp import FastApiMCP

setup_logging()

# 将 MCP 服务器添加到 FastAPI 应用
mcp = FastApiMCP(
    app,
    name="物品 API MCP",
    description="物品 API 的 MCP 服务器",
    describe_full_response_schema=True,   # 描述完整的响应 JSON-schema，而不仅仅是一个响应示例
    describe_all_responses=True,   # 描述所有可能的响应，而不仅仅是成功（2XX）响应
)

mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
