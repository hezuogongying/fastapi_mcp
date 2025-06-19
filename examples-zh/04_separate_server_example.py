"""
本示例展示了如何将 MCP 服务器和 FastAPI 应用分开运行。
你可以从一个 FastAPI 应用创建 MCP 服务器，并将其挂载到另一个应用。
"""
from fastapi import FastAPI

from demo.apps.apis import app
from demo.core.setup import setup_logging

from fastapi_mcp import FastApiMCP

setup_logging()

MCP_SERVER_HOST = "localhost"
MCP_SERVER_PORT = 8000
ITEMS_API_HOST = "localhost"
ITEMS_API_PORT = 8001

# 仅将 FastAPI 应用作为 MCP 服务器生成的来源
mcp = FastApiMCP(app)

# 将 MCP 服务器挂载到单独的 FastAPI 应用
mcp_app = FastAPI()
mcp.mount(mcp_app)

# 分别运行 MCP 服务器和原始 FastAPI 应用。
# 依然可以正常工作 🚀
# 原始 API 不会直接暴露，只能通过 MCP 服务器访问。
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(mcp_app, host="0.0.0.0", port=8000)
