import streamlit as st
import httpx
import json
from openai import OpenAI
import os
import logging

# --- 配置 ---
# 设置日志
logging.basicConfig(level=logging.INFO)

# 设置页面标题和图标
st.set_page_config(page_title="MCP-LLM 交互演示", page_icon="🤖")

# 从 Streamlit secrets 或环境变量获取 OpenAI 配置
# 在本地运行时，可以设置环境变量：
# $env:OPENAI_API_KEY="your_key"
# $env:OPENAI_API_BASE="http://127.0.0.1:8080/v1" (如果你使用本地LLM)
api_key = st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", "none"))
base_url = st.secrets.get("OPENAI_API_BASE", os.environ.get("OPENAI_API_BASE"))

# FastAPI 服务器的地址
FASTAPI_BASE_URL = "http://127.0.0.1:8000"
OPENAPI_URL = f"{FASTAPI_BASE_URL}/openapi.json"

# --- 核心函数 ---

@st.cache_data(ttl=300) # 缓存 OpenAPI schema 5分钟
def get_api_tools_from_schema():
    """从 FastAPI 服务器获取并格式化 MCP 工具列表"""
    try:
        logging.info(f"正在从 {OPENAPI_URL} 获取 OpenAPI schema...")
        response = httpx.get(OPENAPI_URL)
        response.raise_for_status()
        schema = response.json()
        logging.info("成功获取并解析 OpenAPI schema。")
        
        tools = []
        tool_mappings = {}

        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if "tags" in operation and "mcp-tools" in operation["tags"]:
                    # 确保函数名对于LLM是有效的
                    function_name = operation.get("operationId").replace("-", "_")
                    description = operation.get("description") or operation.get("summary", "")
                    
                    parameters = {"type": "object", "properties": {}, "required": []}
                    
                    # 处理URL路径参数和查询参数
                    if "parameters" in operation:
                        for param in operation["parameters"]:
                            param_name = param["name"]
                            param_schema = param.get("schema", {})
                            parameters["properties"][param_name] = {
                                "type": param_schema.get("type"),
                                "description": param.get("description", "")
                            }
                            if param.get("required", False):
                                parameters["required"].append(param_name)
                    
                    # 处理POST/PUT请求的请求体
                    if "requestBody" in operation:
                        content = operation["requestBody"].get("content", {})
                        if "application/json" in content:
                            request_schema = content["application/json"].get("schema", {})
                            # 将请求体作为一个名为 'data' 的参数
                            parameters["properties"]["data"] = request_schema
                            if operation["requestBody"].get("required", False):
                                parameters["required"].append("data")

                    tools.append({
                        "type": "function",
                        "function": {
                            "name": function_name,
                            "description": description,
                            "parameters": parameters
                        }
                    })
                    tool_mappings[function_name] = {
                        "method": method.upper(),
                        "path": path
                    }
        logging.info(f"成功转换 {len(tools)} 个工具。")
        return tools, tool_mappings
    except httpx.RequestError as e:
        st.error(f"无法连接到 FastAPI 服务器: {e}。请确保 [02_full_schema_description_example.py](cci:7://file:///d:/project/python/fastapi_mcp/examples-zh/02_full_schema_description_example.py:0:0-0:0) 正在运行。")
        return None, None
    except Exception as e:
        st.error(f"解析 OpenAPI schema 失败: {e}")
        logging.error(f"解析 OpenAPI schema 失败: {e}", exc_info=True)
        return None, None

def execute_api_tool(tool_call, tool_mappings):
    """执行 LLM 请求的 API 工具调用"""
    function_name = tool_call.function.name
    try:
        arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        return f"错误: 无效的参数格式: {tool_call.function.arguments}"
        
    mapping = tool_mappings.get(function_name)
    if not mapping:
        return f"错误: 未知的工具 '{function_name}'"
        
    method = mapping["method"]
    path_template = mapping["path"]
    
    # 分离路径参数和查询/请求体参数
    path_params = {}
    other_params = {}
    for key, value in arguments.items():
        if f"{{{key}}}" in path_template:
            path_params[key] = value
        else:
            other_params[key] = value
            
    url = f"{FASTAPI_BASE_URL}{path_template.format(**path_params)}"
    
    try:
        logging.info(f"正在执行工具: {method} {url} with params {other_params}")
        with httpx.Client() as client:
            response = None
            if method == "GET":
                response = client.get(url, params=other_params)
            elif method == "POST":
                response = client.post(url, json=other_params.get("data"))
            elif method == "PUT":
                 response = client.put(url, json=other_params.get("data"))
            elif method == "DELETE":
                response = client.delete(url)
            else:
                return f"错误: 不支持的 HTTP 方法 '{method}'"

            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"API 调用失败: {e.response.status_code} - {e.response.text}")
        return f"API 调用失败: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        logging.error(f"执行 API 调用时出错: {e}", exc_info=True)
        return f"执行 API 调用时出错: {e}"

# --- Streamlit UI ---

st.title("🤖 MCP-LLM 交互演示")
st.caption("一个使用 LLM 与 FastApiMCP 工具交互的 Streamlit 聊天机器人")

# 初始化
if "client" not in st.session_state:
    if not api_key or api_key == "none":
        st.warning("请在环境变量或 Streamlit secrets 中设置 `OPENAI_API_KEY`。")
        st.stop()
    st.session_state.client = OpenAI(api_key=api_key, base_url=base_url)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好！我可以帮你查询、添加、修改或删除物品。请问有什么可以帮您？"}]

# 获取工具
tools, tool_mappings = get_api_tools_from_schema()
if not tools:
    st.stop()

# 显示聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
if prompt := st.chat_input("例如: '帮我找找价格低于10元的锤子'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用 LLM
    try:
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = st.session_state.client.chat.completions.create(
                    model="gpt-4-turbo", # 或您使用的模型
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    tools=tools,
                    tool_choice="auto",
                )
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

            if tool_calls:
                st.session_state.messages.append(response_message)
                for tool_call in tool_calls:
                    st.info(f"正在调用工具: `{tool_call.function.name}`...")
                    function_response = execute_api_tool(tool_call, tool_mappings)
                    st.session_state.messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": json.dumps(function_response, ensure_ascii=False),
                    })
                
                with st.spinner("处理工具结果..."):
                    second_response = st.session_state.client.chat.completions.create(
                        model="gpt-4-turbo",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    )
                    final_response = second_response.choices[0].message.content
                    st.markdown(final_response)
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
            else:
                final_response = response_message.content
                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})

    except Exception as e:
        st.error(f"与 LLM 通信时出错: {e}")
        logging.error(f"LLM 调用出错: {e}", exc_info=True)