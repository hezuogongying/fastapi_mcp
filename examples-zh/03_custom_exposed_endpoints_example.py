"""
本示例展示了如何通过筛选 operation ID 和标签自定义暴露的接口。
筛选说明：
- 不能同时使用 `include_operations` 和 `exclude_operations`
- 不能同时使用 `include_tags` 和 `exclude_tags`
- 可以将操作筛选与标签筛选结合使用（例如，`include_operations` 与 `include_tags` 一起用）
- 当组合筛选时，将采用贪婪模式。匹配任一条件的接口都会被包含
"""
from demo.apps.apis import app  # FastAPI 应用
from demo.core.setup import setup_logging

from fastapi_mcp import FastApiMCP

setup_logging()

# 演示如何通过 operation ID 和标签筛选 MCP 工具

# 仅包含指定 operation ID 的接口
include_operations_mcp = FastApiMCP(
    app,
    name="物品 API MCP - 包含指定操作",
    include_operations=["get_item", "list_items"],
)

# 排除指定 operation ID 的接口
exclude_operations_mcp = FastApiMCP(
    app,
    name="物品 API MCP - 排除指定操作",
    exclude_operations=["create_item", "update_item", "delete_item"],
)

# 仅包含指定标签的接口
include_tags_mcp = FastApiMCP(
    app,
    name="物品 API MCP - 包含指定标签",
    include_tags=["items"],
)

# 排除指定标签的接口
exclude_tags_mcp = FastApiMCP(
    app,
    name="物品 API MCP - 排除指定标签",
    exclude_tags=["search"],
)

# 组合操作 ID 和标签（包含模式）
combined_include_mcp = FastApiMCP(
    app,
    name="物品 API MCP - 组合包含",
    include_operations=["delete_item"],
    include_tags=["search"],
)

# 挂载所有 MCP 服务器到不同路径
include_operations_mcp.mount(mount_path="/include-operations-mcp")
exclude_operations_mcp.mount(mount_path="/exclude-operations-mcp")
include_tags_mcp.mount(mount_path="/include-tags-mcp")
exclude_tags_mcp.mount(mount_path="/exclude-tags-mcp")
combined_include_mcp.mount(mount_path="/combined-include-mcp")

if __name__ == "__main__":
    import uvicorn

    print("服务器已运行，包含多个 MCP 端点：")
    print(" - /include-operations-mcp: 仅包含 get_item 和 list_items 操作")
    print(" - /exclude-operations-mcp: 除 create_item、update_item、delete_item 外的所有操作")
    print(" - /include-tags-mcp: 仅包含 'items' 标签的操作")
    print(" - /exclude-tags-mcp: 排除 'search' 标签的所有操作")
    print(" - /combined-include-mcp: 包含 'search' 标签或 delete_item 操作")
    uvicorn.run(app, host="0.0.0.0", port=8000)
