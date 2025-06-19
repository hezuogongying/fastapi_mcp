import requests
import subprocess
import os
from typing import Dict, Any, Optional
import time
import sys
import sseclient
import requests


def start_mcp_server(server_setting: Dict[str, Any], cwd: Optional[str] = None, port: int = 8000) -> subprocess.Popen:
    """
    通用函数：根据mcp server配置参数（如command/args/env），用subprocess启动node类mcp server。
    自动判断平台，win用cmd /c npx ...，非win用npx ...。
    :param server_setting: 形如 {"command":..., "args":..., "env":...}
    :param cwd: 工作目录（可选）
    :return: Popen对象
    """
    env = os.environ.copy()
    env.update(server_setting.get("env", {}))
    if sys.platform.startswith("win"):
        args = server_setting.get("args", ["/c", "npx", "-y", "@playwright/mcp@latest", "--headless", "--port", str(port)])
    else:
        args = server_setting.get("args", ["-y", "@playwright/mcp@latest", "--headless", "--port", str(port)])

    command = server_setting.get("command", "cmd")
    cmdline = [command] + args
    proc = subprocess.Popen(
        cmdline,
        env=env,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        encoding="utf-8"
    )
    # 实时打印 MCP server 的 stdout/stderr
    for line in iter(proc.stdout.readline, ""):
        print(line.strip())
    return proc

def get_mcp_tools_count_from_openapi(mcp_url: str) -> int:
    # 兼容 server 末尾是否有斜杠
    url = mcp_url.rstrip("/") + "/openapi.json"
    try:
        resp = requests.get(url, timeout=5)
        print("openapi.json 返回：", resp.text)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise ValueError(f"Failed to get MCP openapi.json: {e}")
    # 优先 windsuf/mcp 扩展字段
    if "x-windsurf-tools" in data:
        return len(data["x-windsurf-tools"])
    elif "paths" in data:
        return len(data["paths"])
    else:
        raise ValueError("Unrecognized MCP openapi.json format")

def get_mcp_tools_count(mcp_url: str) -> int:
    """
    获取 MCP Server 上注册的工具数量
    :param mcp_url: MCP Server 根地址（如 http://127.0.0.1:8000/mcp）
    :return: 工具数量
    """
    # 兼容 server 末尾是否有斜杠
    url = mcp_url.rstrip("/") + "/tools"
    try:
        resp = requests.get(url, timeout=5)
        print("tools接口返回：", resp.text)  # 调试用
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise ValueError(f"Failed to get MCP tools count: {e}")
    if isinstance(data, dict) and "tools" in data:
        return len(data["tools"])
    elif isinstance(data, list):
        return len(data)
    else:
        raise ValueError("Unrecognized MCP tools response format")

import json

def get_tools_from_sse(mcp_base_url: str, timeout: int = 15) -> int:
    """
    连接 Playwright MCP SSE，监听工具定义事件，返回工具数量。
    :param mcp_base_url: MCP server 基础地址，如 http://127.0.0.1:8000/mcp
    :param timeout: 最长等待秒数
    :return: 工具数量
    """
    # 1. 获取 SSE endpoint
    # 访问 /mcp，获取 data 字段，形如 /sse?sessionId=xxx
    entry_resp = requests.get(mcp_base_url, timeout=5)
    if entry_resp.status_code != 200:
        raise RuntimeError(f"访问 {mcp_base_url} 失败: {entry_resp.status_code}")
    # 解析 SSE endpoint
    for line in entry_resp.text.splitlines():
        if line.startswith("data:"):
            sse_path = line.split("data:",1)[1].strip()
            break
    else:
        raise RuntimeError("未找到 SSE endpoint")
    # 拼接完整 SSE URL
    if sse_path.startswith("/"):
        base = mcp_base_url.split("/mcp")[0]
        sse_url = base + sse_path
    else:
        sse_url = mcp_base_url.rstrip("/") + "/" + sse_path
    print(f"连接 SSE: {sse_url}")
    # 2. 监听 SSE 事件
    resp = requests.get(sse_url, stream=True, timeout=timeout)
    client = sseclient.SSEClient(resp)
    start_time = time.time()
    for event in client.events():
        # 生产环境要注释掉
        print(f"event: {event.event}\ndata: {event.data}")
        try:
            data = json.loads(event.data)
        except Exception:
            continue
        # Playwright MCP 的工具定义通常在 tool/tool_list/tools 字段
        # 兼容多种可能格式
        if isinstance(data, dict):
            if "tools" in data and isinstance(data["tools"], list):
                print(f"收到 tools 事件: {data['tools']}")
                return len(data["tools"])
            elif "tool_list" in data and isinstance(data["tool_list"], list):
                print(f"收到 tool_list 事件: {data['tool_list']}")
                return len(data["tool_list"])
            elif "tool" in data:
                # 单个工具事件，累加
                print(f"收到 tool 事件: {data['tool']}")
                return 1
        # 超时保护
        if time.time() - start_time > timeout:
            raise TimeoutError("等待工具事件超时")
    raise RuntimeError("未收到工具定义事件")


if __name__ == "__main__":
    mcpserver_setting = {
        "playwright": {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@playwright/mcp@latest",
                "--headless"
            ],
            "env": {}
        }
    }
    mcp_port = 8000
    proc = start_mcp_server(mcpserver_setting, port=mcp_port)   # 启动 MCP 进程
    time.sleep(5)   # 等待 MCP 进程启动
    print(f"MCP Server 启动成功，地址：http://127.0.0.1:{mcp_port}/mcp")
    count = get_tools_from_sse(f"http://127.0.0.1:{mcp_port}/mcp")
    print(f"MCP 工具数量: {count}")
    proc.terminate()    # 终止 MCP 进程
    proc.wait()   # 等待 MCP 进程结束
