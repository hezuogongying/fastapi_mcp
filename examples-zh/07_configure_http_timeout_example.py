"""
本示例展示了如何为 MCP 服务器配置 HTTP 客户端超时时间。
当你的 API 接口响应时间超过 5 秒时，可以增加超时时间。
"""
from demo.apps.apis import app  # FastAPI 应用
from demo.core.setup import setup_logging

import httpx

from fastapi_mcp import FastApiMCP

setup_logging()

mcp = FastApiMCP(
    app,
    http_client=httpx.AsyncClient(timeout=20)
)
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
