"""
call_mcp.py: FastAPI app with dynamic nested MCP calls and MCP server mounting.

- 每个端点动态调用/转发到另一个 MCP。
- 直接挂载 MCP 服务器到本 FastAPI。
- 支持通过 HTTP 动态选择/调用不同的 MCP。
- 用完即销毁，突破 tools 数量限制。
"""
import asyncio
import json
import subprocess
from fastapi import FastAPI, Request, Body, HTTPException
from fastapi.responses import JSONResponse
from fastapi_mcp import FastApiMCP
from typing import Dict, Any, Optional
import httpx
import os

# MCP 配置文件路径
MCP_CONFIG_PATH = os.path.expanduser(r"~/.codeium/windsurf/mcp_config.json")
MAX_TOOLS = 50

# 全局 registry: {server_name: {'type': 'python'|'external', 'tools': int, 'proc': Popen, ...}}
mcp_registry = {}

# 读取 MCP config
with open(MCP_CONFIG_PATH, encoding="utf-8") as f:
    MCP_CONFIG = json.load(f)["mcpServers"]

app = FastAPI(title="Cascade动态MCP网关")

async def get_tools_count():
    """统计所有 MCP 的 tools 数量"""
    total = 0
    for entry in mcp_registry.values():
        total += entry.get('tools', 0)
    return total

async def fetch_tools_from_http(server_url: str) -> int:
    """通过 HTTP 获取 MCP server 的 tools 数量"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(f"{server_url}/list_tools")
            resp.raise_for_status()
            tools = resp.json()
            return len(tools)
        except Exception:
            return 0

@app.post("/call_mcp/{mcp_name}")
async def call_mcp_endpoint(
    mcp_name: str,
    payload: Dict[str, Any] = Body(...),
    server: Optional[str] = None,
):
    """
    支持多 MCP server 动态调用，自动判断 tools 总数是否超限。
    server: 指定 mcp server 名称，如 'playwright'。
    """
    global mcp_registry
    # 判断是否超限
    total_tools = await get_tools_count()
    if total_tools >= MAX_TOOLS:
        raise HTTPException(status_code=429, detail=f"MCP tools 总数已达上限: {MAX_TOOLS}")

    # 1. 外部 MCP（如 npx）
    if server and server in MCP_CONFIG:
        cfg = MCP_CONFIG[server]
        # 启动 MCP 进程
        proc = subprocess.Popen(
            [cfg["command"]] + cfg["args"],
            env=cfg.get("env", os.environ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # 假设外部 MCP 监听 127.0.0.1:9000
        mcp_url = "http://127.0.0.1:9000/mcp"
        try:
            # 获取 tools 数量
            tools_num = await fetch_tools_from_http(mcp_url)
            mcp_registry[server] = {'type': 'external', 'tools': tools_num, 'proc': proc}
            # 动态调用目标 MCP
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{mcp_url}/call_tool", json=payload)
                result = resp.json()
            return JSONResponse(content={"result": result, "server": server})
        finally:
            proc.terminate()
            proc.wait()
            mcp_registry.pop(server, None)
    # 2. 本地 Python MCP
    else:
        temp_app = FastAPI(title=f"动态 MCP-{mcp_name}")
        mcp_server = FastApiMCP(temp_app, name=mcp_name)
        mcp_server.mount(temp_app, mount_path="/mcp", transport="sse")
        # 获取 tools 数量（假设 tools 都已注册）
        tools_num = len(mcp_server.tools) if hasattr(mcp_server, 'tools') else 0
        mcp_registry[mcp_name] = {'type': 'python', 'tools': tools_num}
        # 实际调用（此处简化为回显）
        result = {"mcp": mcp_name, "payload": payload}
        del temp_app
        del mcp_server
        mcp_registry.pop(mcp_name, None)
        return JSONResponse(content={"result": result, "server": mcp_name})

# 3. 直接将 MCP 服务器挂载到本 FastAPI 应用
main_mcp = FastApiMCP(app, name="main-mcp")
main_mcp.mount(app, mount_path="/mcp", transport="sse")

# 4. 健康检查端点
@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
    