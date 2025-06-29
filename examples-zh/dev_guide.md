# FastAPI 与 FastApiMCP 开发指南

本指南旨在详细说明 FastAPI 应用实例 (`app`)、`FastAPI` 类以及 `FastApiMCP` 类的初始化参数和常用装饰器参数，帮助开发者更好地理解和使用这些组件。

## 1. `FastAPI` 类初始化参数

`FastAPI` 是 FastAPI 框架的核心类，用于创建一个 FastAPI 应用实例。在初始化时，可以传入多个参数来配置应用的行为和元数据。

```python
from fastapi import FastAPI

app = FastAPI(
    title="我的应用",
    description="这是一个非常棒的应用，提供了很多有用的功能。",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

**常用参数说明：**

*   `title` (str, 可选): API 的标题。默认值: `"FastAPI"`。
*   `description` (str, 可选): API 的描述，支持 Markdown。默认值: `None`。
*   `version` (str, 可选): API 的版本号。默认值: `"0.1.0"`。
*   `openapi_url` (str, 可选): OpenAPI 规范 (JSON Schema) 的访问路径。设置为 `None` 可以禁用 OpenAPI schema 生成。默认值: `"/openapi.json"`。
*   `docs_url` (str, 可选): Swagger UI API 文档的访问路径。设置为 `None` 可以禁用 Swagger UI。默认值: `"/docs"`。
*   `redoc_url` (str, 可选): ReDoc API 文档的访问路径。设置为 `None` 可以禁用 ReDoc。默认值: `"/redoc"`。
*   `default_response_class` (Type[Response], 可选): 默认的响应类。例如，可以设置为 `ORJSONResponse` 以获得更快的 JSON 处理。默认值: `JSONResponse`。
*   `dependencies` (Sequence[Depends], 可选): 应用于所有路径操作的全局依赖项列表。
*   `middleware` (Sequence[Middleware], 可选): 应用于整个应用的中间件列表。
*   `exception_handlers` (Dict[Union[int, Type[Exception]], Callable], 可选): 自定义异常处理器。
*   `on_startup` (Sequence[Callable], 可选): 应用启动时执行的函数列表。
*   `on_shutdown` (Sequence[Callable], 可选): 应用关闭时执行的函数列表。

## 2. `app` 路由装饰器参数

FastAPI 应用实例 (`app`) 提供了多种 HTTP 方法装饰器（如 `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()` 等）来定义 API 路由和处理函数。这些装饰器接受多种参数来配置路由的行为和文档。

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

@app.get(
    "/items/{item_id}",
    response_model=Item,
    status_code=200,
    tags=["物品"],
    summary="获取单个物品信息",
    description="通过物品 ID 获取该物品的详细信息。",
    operation_id="read_single_item"
)
async def read_item(item_id: int):
    # 实际应用中会从数据库查询
    return {"id": item_id, "name": "示例物品"}

@app.post(
    "/items/",
    response_model=Item,
    status_code=201,  # 201 Created
    tags=["物品"],
    summary="创建新物品"
)
async def create_item(item: Item):
    # 实际应用中会将物品存入数据库
    return item
```

**常用参数说明 (以 `@app.get` 为例，其他 HTTP 方法装饰器类似)：**

*   `path` (str): 路由的 URL 路径。路径参数可以使用花括号 `{}` 定义，例如 `"/items/{item_id}"`。
*   `response_model` (Type[BaseModel], 可选): 用于响应数据校验和文档生成的 Pydantic 模型。FastAPI 会确保响应体符合此模型的结构。
*   `status_code` (int, 可选): 成功响应时的 HTTP 状态码。默认值: `200` (对于 POST 通常是 `201`)。
*   `tags` (List[str], 可选): 用于在 API 文档中对路径操作进行分组的标签列表。
*   `summary` (str, 可选): 对路径操作的简短摘要，会显示在 API 文档中。
*   `description` (str, 可选): 对路径操作的详细描述，支持 Markdown，会显示在 API 文档中。
*   `response_description` (str, 可选): 对响应的描述。默认值: `"Successful Response"`。
*   `deprecated` (bool, 可选): 如果设置为 `True`，则在 API 文档中将此路径操作标记为已弃用。默认值: `False`。
*   `operation_id` (str, 可选): 路径操作的唯一标识符。通常由 FastAPI 根据函数名自动生成，但可以自定义以提高客户端代码生成的可控性。
*   `include_in_schema` (bool, 可选): 是否在 OpenAPI schema (API 文档) 中包含此路径操作。默认值: `True`。
*   `dependencies` (Sequence[Depends], 可选): 此特定路径操作的依赖项列表。
*   `name` (str, 可选): 路径操作的名称，可用于 URL 反向解析 (`url_path_for`)。
*   `responses` (Dict[Union[int, str], Dict[str, Any]], 可选): 额外的响应模型和描述，用于在 API 文档中声明可能的其他响应 (例如错误响应)。

## 3. `FastApiMCP` 类初始化参数

`FastApiMCP` 类用于将一个 FastAPI 应用转换为 MCP (Model Context Protocol) 服务器，使其能够暴露 API 端点作为 MCP 工具。

```python
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP, AuthConfig # 假设 AuthConfig 已定义
import httpx # 用于 http_client 示例

app = FastAPI(title="我的FastAPI应用", description="这是一个示例应用")

# 示例 AuthConfig (实际使用时需要根据认证需求配置)
# auth_config = AuthConfig(...)

mcp_server = FastApiMCP(
    fastapi=app,
    name="我的MCP服务",
    description="将我的FastAPI应用接口暴露为MCP工具",
    describe_all_responses=False,
    describe_full_response_schema=False,
    # http_client=httpx.AsyncClient(), # 可选：自定义 HTTP 客户端
    # include_operations=["read_single_item"], # 可选：仅包含指定 operation_id 的工具
    # exclude_operations=[], # 可选：排除指定 operation_id 的工具
    # include_tags=["物品"], # 可选：仅包含指定标签的工具
    # exclude_tags=[], # 可选：排除指定标签的工具
    # auth_config=auth_config # 可选：MCP 认证配置
)
```

**参数说明 (基于 `fastapi_mcp/server.py` 中的 `FastApiMCP.__init__` 方法)：**

*   `fastapi` (FastAPI): **必需参数**。要从中创建 MCP 服务器的 FastAPI 应用实例。
*   `name` (Optional[str], 可选): MCP 服务器的名称。如果未提供，则默认为 `fastapi.title` (FastAPI 应用的标题)，如果 `fastapi.title` 也未设置，则默认为 `"FastAPI MCP"`。
*   `description` (Optional[str], 可选): MCP 服务器的描述。如果未提供，则默认为 `fastapi.description` (FastAPI 应用的描述)。
*   `describe_all_responses` (bool, 可选): 是否在 MCP 工具描述中包含所有可能的响应模式。默认值: `False`。
    *   如果为 `True`，工具描述会更详尽，列出 API 定义的各种响应状态码及其模式。
*   `describe_full_response_schema` (bool, 可选): 是否在 MCP 工具描述中包含完整的 JSON Schema 以描述响应。默认值: `False`。
    *   如果为 `True`，响应描述会包含详细的 JSON Schema 结构。
*   `http_client` (Optional[httpx.AsyncClient], 可选): 用于向 FastAPI 应用发起 API 调用的自定义 HTTP 客户端。必须是 `httpx.AsyncClient` 的实例。如果未提供，`FastApiMCP` 会自动创建一个基于 `httpx.ASGITransport` 的客户端来直接与传入的 FastAPI 应用通信。默认值: `None` (自动创建)。
*   `include_operations` (Optional[List[str]], 可选): 一个操作 ID (operation ID) 列表，只有这些操作 ID 对应的 API 端点才会被转换为 MCP 工具。不能与 `exclude_operations` 同时使用。默认值: `None` (不按操作 ID 包含过滤)。
*   `exclude_operations` (Optional[List[str]], 可选): 一个操作 ID 列表，这些操作 ID 对应的 API 端点将不会被转换为 MCP 工具。不能与 `include_operations` 同时使用。默认值: `None` (不按操作 ID 排除过滤)。
*   `include_tags` (Optional[List[str]], 可选): 一个标签 (tag) 列表，只有包含了这些标签中至少一个的 API 端点才会被转换为 MCP 工具。不能与 `exclude_tags` 同时使用。默认值: `None` (不按标签包含过滤)。
*   `exclude_tags` (Optional[List[str]], 可选): 一个标签列表，包含了这些标签中至少一个的 API 端点将不会被转换为 MCP 工具。不能与 `include_tags` 同时使用。默认值: `None` (不按标签排除过滤)。
*   `auth_config` (Optional[AuthConfig], 可选): MCP 认证配置对象。用于为 MCP 服务器设置认证和授权机制。具体结构和用法取决于 `AuthConfig` 类的定义。默认值: `None` (无特定 MCP 认证配置)。

**内部逻辑和默认行为:**

*   **操作和标签过滤**: 如果同时提供了 `include_operations` 和 `exclude_operations`，或者同时提供了 `include_tags` 和 `exclude_tags`，`FastApiMCP` 在初始化时会抛出 `ValueError`。
*   **HTTP 客户端**: 如果不提供 `http_client`，`FastApiMCP` 会创建一个 `httpx.AsyncClient`，使用 `httpx.ASGITransport(app=self.fastapi, raise_app_exceptions=False)` 作为其传输方式。这意味着 MCP 服务器内部调用 FastAPI 端点时，请求不会经过网络层，而是直接在 ASGI 应用层面进行，效率较高。`base_url` 默认为 `"http://apiserver"`，超时默认为 `10.0` 秒。
*   **OpenAPI Schema 解析**: `FastApiMCP` 会获取 FastAPI 应用的 OpenAPI schema，并将其转换为 MCP 工具列表。
*   **服务器设置**: `setup_server()` 方法负责解析 OpenAPI schema，转换并过滤工具，然后设置底层的 `LowlevelMCPServer` 来处理 MCP 请求 (如 `ListToolsRequest` 和 `CallToolRequest`)。

## 4. 总结

理解 `FastAPI`、`app` 装饰器以及 `FastApiMCP` 的各项参数对于构建功能强大且易于维护的 API 和 MCP 服务至关重要。本指南提供了常用参数的中文说明和示例，希望能帮助您更有效地利用这些工具。

建议参考 FastAPI 和 FastApiMCP 的官方文档以获取最全面和最新的信息。

## 5. `AuthConfig` 类 (MCP 认证配置)

`AuthConfig` 类 (定义于 `fastapi_mcp.types`) 用于在创建 `FastApiMCP` 服务器时配置认证和授权机制。它允许您指定如何保护 MCP 工具，以及客户端应如何进行身份验证。

**使用示例 (参考 `examples-zh/08_auth_example_token_passthrough.py`):**

```python
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from fastapi_mcp import FastApiMCP, AuthConfig

app = FastAPI()
token_auth_scheme = HTTPBearer() # 定义一个 HTTP Bearer Token 认证方案

# 一个受保护的 FastAPI 路由示例
@app.get("/private")
async def private_route(token: str = Depends(token_auth_scheme)):
    return {"token": token.credentials}

# 初始化 FastApiMCP 时传入 AuthConfig
mcp_server = FastApiMCP(
    app,
    name="受保护的 MCP 服务",
    auth_config=AuthConfig(
        dependencies=[Depends(token_auth_scheme)], # 关键：传递 FastAPI 依赖项
        # 其他 AuthConfig 参数可根据需要配置
    )
)

mcp_server.mount() # 挂载 MCP 服务
```

在上面的示例中，`AuthConfig` 的 `dependencies` 参数被用来传递一个 FastAPI 依赖项 (`Depends(token_auth_scheme)`)。这意味着当 MCP 客户端尝试调用通过此 `mcp_server` 暴露的任何工具时，FastAPI 的依赖注入系统会首先执行 `token_auth_scheme`。如果认证失败（例如，没有提供有效的 Bearer Token），依赖项会引发 HTTP 401 或 403 错误，从而阻止工具的执行，并向 MCP 客户端指示需要认证。

**`AuthConfig` 主要参数说明:**

*   `version` (Literal["2025-03-26"], 可选): 用于设置授权的 MCP 规范版本。目前仅支持 `"2025-03-26"`。默认值: `"2025-03-26"`。
*   `dependencies` (Optional[Sequence[params.Depends]], 可选): FastAPI 依赖项列表 (使用 `Depends()`)。这些依赖项用于检查认证或授权，并在请求未经认证或授权时引发 401 或 403 错误。这是触发客户端启动 OAuth 流程或传递认证信息的关键机制。
    *   如示例所示，您可以传递一个或多个 FastAPI 依赖项，这些依赖项将应用于所有通过此 `FastApiMCP` 实例暴露的 MCP 工具。
*   `issuer` (Optional[str], 可选): OAuth 2.0 服务器的颁发者 (issuer)。如果不提供 `custom_oauth_metadata`，则此项为必需。通常是应用的根 URL 或 OAuth 提供商的 URL (例如 Auth0 的 `https://your-tenant.auth0.com`)。
*   `oauth_metadata_url` (Optional[StrHttpUrl], 可选): OAuth 提供商元数据端点的完整 URL。如果未提供，FastAPI-MCP 会尝试基于 `issuer` 和 `metadata_path` (内部默认路径) 进行猜测。仅当 `setup_proxies` 为 `True` 时相关。
*   `authorize_url` (Optional[StrHttpUrl], 可选): OAuth 提供商授权端点的 URL (例如 `https://app.example.com/oauth/authorize`)。
*   `audience` (Optional[str], 可选): 默认的受众 (audience)。用于某些 MCP 客户端可能不指定受众的情况，作为请求 OAuth 提供商时的默认值。
*   `default_scope` (str, 可选): 默认的作用域 (scope)。用于某些 MCP 客户端可能不指定作用域的情况。默认值: `"openid profile email"`。
*   `client_id` (Optional[str], 可选): 默认的客户端 ID。如果客户端未指定客户端 ID，则在向 OAuth 提供商发起请求时使用此值。仅当 `setup_proxies` 为 `True` 时强制要求。
*   `client_secret` (Optional[str], 可选): `client_id` 对应的客户端密钥。仅当 `setup_proxies` 和 `setup_fake_dynamic_registration` 均为 `True` 时强制要求。
*   `custom_oauth_metadata` (Optional[OAuthMetadataDict], 可选): 自定义的 OAuth 元数据。如果您的 OAuth 流程与 MCP 开箱即用兼容，可以使用此选项提供元数据。否则，应将 `setup_proxies` 设置为 `True` 以自动设置 MCP 兼容的代理。
*   `setup_proxies` (bool, 可选): 是否自动在原始 OAuth 提供商的端点周围设置 MCP 兼容的代理。默认值: `False`。
    *   如果为 `True`，FastAPI-MCP 会尝试代理 OAuth 流程中的关键端点 (如元数据、授权端点)，使其更符合 MCP 规范。
*   `metadata_path` (str, 可选): OAuth 元数据端点的路径。默认值: `"/.well-known/oauth-authorization-server"`。
*   `authorize_path` (str, 可选): 授权端点代理的路径。默认值: `"/oauth/authorize"`。
*   `register_path` (Optional[str], 可选): 动态客户端注册端点代理的路径。默认值: `"/oauth/register"`。
*   `setup_fake_dynamic_registration` (bool, 可选): 是否设置一个伪造的动态客户端注册端点。默认值: `False`。

**验证逻辑:**
`AuthConfig` 包含一个模型验证器 (`validate_required_fields`)，确保在特定条件下提供了必需的字段：
*   必须提供 `issuer`、`custom_oauth_metadata` 或 `dependencies` 中的至少一个。
*   如果 `setup_proxies` 为 `True`，则必须提供 `client_id`。
*   如果 `setup_proxies` 和 `setup_fake_dynamic_registration` 均为 `True`，则必须提供 `client_secret`。

选择合适的 `AuthConfig` 参数组合取决于您的具体认证需求和 OAuth 提供商的配置。对于简单的 Token 直通 (如 Bearer Token)，通常仅配置 `dependencies` 就足够了，如 `08_auth_example_token_passthrough.py` 所示。对于更复杂的 OAuth 2.0 流程，可能需要配置 `issuer`, `client_id`, `setup_proxies` 等参数。
