"""
本示例展示了如果在创建 MCP 服务器后新增接口，如何重新注册工具。
"""
from demo.apps.apis import app  # FastAPI 应用
from demo.core.setup import setup_logging
import json # 用于美化打印 OpenAPI schema

from fastapi_mcp import FastApiMCP

setup_logging()

print("--- 调试：FastAPI 应用初始 OpenAPI Schema (部分) ---")
try:
    initial_schema = app.openapi()
    print(json.dumps({"paths": initial_schema.get("paths", {})}, indent=2, ensure_ascii=False))
    print(f"--- 调试：初始 Schema 中路径数量: {len(initial_schema.get('paths', {}))} ---")
except Exception as e:
    print(f"获取初始 schema 失败: {e}")


mcp = FastApiMCP(app)  # 将 MCP 服务器添加到 FastAPI 应用
print("--- 调试：FastApiMCP 实例已创建 ---")

mcp.mount()  # 挂载 MCP 服务器
print(f"--- 调试：mcp.mount() 调用后，mcp.tools 长度: {len(mcp.tools)} ---")
# print(f"--- 调试：mcp.mount() 调用后，mcp.tools 内容: {mcp.tools} ---") # 如果工具很多，这行可以注释掉

# 由于该接口是在 MCP 实例创建后添加的，因此不会被注册为工具
@app.get("/new/endpoint/", operation_id="new_endpoint", response_model=dict[str, str])
async def new_endpoint():
    return {"message": "你好，世界！"}

print("--- 调试：new_endpoint 已添加到 app ---")
print("--- 调试：调用第二次 mcp.setup_server() 之前，FastAPI 应用 OpenAPI Schema (部分) ---")
try:
    schema_before_second_setup = app.openapi() # 重新获取 schema
    # 保存为文件
    schema_json= json.dumps({"paths": schema_before_second_setup.get("paths", {})}, indent=2, ensure_ascii=False)
    with open("schema_before_second_setup.json", "w", encoding="utf-8") as f:
        f.write(schema_json)
    print(schema_json)
    print(f"--- 调试：第二次 setup 前 Schema 中路径数量: {len(schema_before_second_setup.get('paths', {}))} ---")
except Exception as e:
    print(f"获取第二次 setup 前的 schema 失败: {e}")


# 但如果重新运行 setup，新增接口就会被暴露出来
mcp.setup_server()
print(f"--- 调试：第二次 mcp.setup_server() 调用后，mcp.tools 长度: {len(mcp.tools)} ---")
# print(f"--- 调试：第二次 mcp.setup_server() 调用后，mcp.tools 内容: {mcp.tools} ---") # 如果工具很多，这行可以注释掉


# 强制 FastAPI 在启动前清除缓存的 OpenAPI schema，以确保提供最新的版本
app.openapi_schema = None

if __name__ == "__main__":
    import uvicorn
    print("--- 启动 Uvicorn 服务器 ---")
    uvicorn.run(app, host="127.0.0.1", port=8000)
