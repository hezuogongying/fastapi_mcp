"""
本示例展示了如何将 MCP 服务器挂载到指定 APIRouter，并自定义挂载路径。
"""
from demo.apps.apis import app  # FastAPI 应用
from demo.core.setup import setup_logging

from fastapi import APIRouter
from fastapi_mcp import FastApiMCP

setup_logging()

other_router = APIRouter(prefix="/other/route")
app.include_router(other_router)

mcp = FastApiMCP(app)

# 将 MCP 服务器挂载到指定的 router。
# 现在只会在 `/other/route/mcp` 路径下可用
mcp.mount(other_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
