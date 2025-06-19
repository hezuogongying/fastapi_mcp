"""
本示例展示了如何拒绝任何未携带有效 Authorization 头部 token 的请求。

要配置认证头部，MCP 服务器的配置文件应如下所示：
```json
{
  "mcpServers": {
    "remote-example": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://localhost:8000/mcp",
        "--header",
        "Authorization:${AUTH_HEADER}"
      ]
    },
    "env": {
      "AUTH_HEADER": "Bearer <your-token>"
    }
  }
}
```
"""
from demo.apps.apis import app   # FastAPI 应用
from demo.core.setup import setup_logging

from fastapi import Depends
from fastapi.security import HTTPBearer

from fastapi_mcp import FastApiMCP, AuthConfig

setup_logging()

# Authorization 头部的认证方案
token_auth_scheme = HTTPBearer()

# 创建一个私有接口


@app.get("/private")
async def private(token=Depends(token_auth_scheme)):
    return token.credentials

# 使用 token 认证方案创建 MCP 服务器
mcp = FastApiMCP(
    app,
    name="受保护的 MCP",
    auth_config=AuthConfig(
        dependencies=[Depends(token_auth_scheme)],
    ),
)

# 挂载 MCP 服务器
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
