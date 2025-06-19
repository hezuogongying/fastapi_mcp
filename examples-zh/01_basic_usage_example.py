# 从 examples.shared.apps.items 导入 FastAPI 应用
from demo.apps.apis import app  # FastAPI 应用
from demo.core.setup import setup_logging

from fastapi_mcp import FastApiMCP

setup_logging()

# 将 MCP 服务器添加到 FastAPI 应用
mcp = FastApiMCP(app)

# 挂载 MCP 服务器到 FastAPI 应用
mcp.mount()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
