# -*- coding: utf-8 -*-
"""
FastAPI-MCP 应用示例：物品管理 API

本文件演示了如何使用 FastAPI 和 Pydantic 构建一个简单的物品管理 API。
它包括了对物品的 CRUD (创建、读取、更新、删除) 操作以及搜索功能。
同时，这也是一个展示 FastAPI-MCP 如何将 MCP 服务集成到 FastAPI 应用中的简单示例。
"""

from fastapi import FastAPI, HTTPException, Query  # 导入 FastAPI 框架的核心组件、HTTP异常处理和查询参数定义
from typing import List, Optional  # 导入类型提示，用于定义列表和可选类型
from .models import Item   # 导入 Pydantic 用于数据校验和模型定义
from .database import items_db  # 导入数据库

app = FastAPI()  # 创建 FastAPI 应用实例


@app.get("/items/", response_model=List[Item], tags=["items"], operation_id="list_items")
async def list_items(skip: int = 0, limit: int = 10):
    """
    列出数据库中的所有物品。

    支持分页功能。
    :param skip: int, 可选, 默认为 0。跳过的物品数量，用于分页。
    :param limit: int, 可选, 默认为 10。返回的物品最大数量，用于分页。
    :return: List[Item], 包含物品对象的列表。
    """
    # 将字典中的所有物品对象转换为列表，并根据 skip 和 limit 进行切片，实现分页
    return list(items_db.values())[skip : skip + limit]


@app.get("/items/{item_id}", response_model=Item, tags=["items"], operation_id="get_item")
async def read_item(item_id: int):
    """
    根据物品 ID 获取特定物品的详细信息。

    如果物品不存在，则引发 404 HTTP 错误。
    :param item_id: int, 必需。要检索的物品的 ID。
    :return: Item, 找到的物品对象。
    :raises HTTPException: 如果具有指定 ID 的物品未找到，则状态码为 404。
    """
    if item_id not in items_db:
        # 如果物品ID不在数据库中，则抛出 HTTP 404 异常
        raise HTTPException(status_code=404, detail="物品未找到")
    return items_db[item_id]  # 返回找到的物品对象


@app.post("/items/", response_model=Item, tags=["items"], operation_id="create_item")
async def create_item(item: Item):
    """
    在数据库中创建一个新的物品。

    返回创建的物品及其分配的 ID。
    :param item: Item, 必需。要创建的物品对象，包含物品的详细信息。
    :return: Item, 创建成功的物品对象。
    """
    # 假设 item.id 是由客户端提供的，或者在实际应用中可能需要在此处生成
    items_db[item.id] = item  # 将新物品添加到数据库
    return item  # 返回创建的物品


@app.put("/items/{item_id}", response_model=Item, tags=["items"], operation_id="update_item")
async def update_item(item_id: int, item: Item):
    """
    更新一个已存在的物品。

    如果物品不存在，则引发 404 HTTP 错误。
    :param item_id: int, 必需。要更新的物品的 ID。
    :param item: Item, 必需。包含物品更新后信息的对象。
    :return: Item, 更新后的物品对象。
    :raises HTTPException: 如果具有指定 ID 的物品未找到，则状态码为 404。
    """
    if item_id not in items_db:
        # 如果物品ID不在数据库中，则抛出 HTTP 404 异常
        raise HTTPException(status_code=404, detail="物品未找到")

    item.id = item_id  # 确保更新的物品ID与路径参数一致
    items_db[item_id] = item  # 更新数据库中的物品信息
    return item  # 返回更新后的物品


@app.delete("/items/{item_id}", tags=["items"], operation_id="delete_item")
async def delete_item(item_id: int):
    """
    从数据库中删除一个物品。

    如果物品不存在，则引发 404 HTTP 错误。
    :param item_id: int, 必需。要删除的物品的 ID。
    :return: dict, 包含删除成功消息的字典。
    :raises HTTPException: 如果具有指定 ID 的物品未找到，则状态码为 404。
    """
    if item_id not in items_db:
        # 如果物品ID不在数据库中，则抛出 HTTP 404 异常
        raise HTTPException(status_code=404, detail="物品未找到")

    del items_db[item_id]  # 从数据库中删除物品
    return {"message": "物品删除成功"}


@app.get("/items/search/", response_model=List[Item], tags=["search"], operation_id="search_items")
async def search_items(
    q: Optional[str] = Query(None, description="搜索查询字符串，匹配物品名称或描述"),  # 查询参数：搜索关键字
    min_price: Optional[float] = Query(None, description="最低价格筛选"),  # 查询参数：最低价格
    max_price: Optional[float] = Query(None, description="最高价格筛选"),  # 查询参数：最高价格
    tags: List[str] = Query([], description="根据标签列表进行筛选，物品需包含所有指定标签"),  # 查询参数：标签列表
):
    """
    根据多种筛选条件搜索物品。

    返回匹配搜索条件的物品列表。
    :param q: str, 可选。搜索查询字符串，用于匹配物品名称或描述。
    :param min_price: float, 可选。筛选条件：物品的最低价格。
    :param max_price: float, 可选。筛选条件：物品的最高价格。
    :param tags: List[str], 可选。筛选条件：物品必须包含的标签列表。
    :return: List[Item], 匹配所有筛选条件的物品列表。
    """
    results = list(items_db.values())  # 获取所有物品作为初始结果集

    # 根据查询字符串 q 进行筛选
    if q:
        q_lower = q.lower()  # 将查询字符串转换为小写，进行不区分大小写的搜索
        results = [
            item for item in results 
            if q_lower in item.name.lower() or \
               (item.description and q_lower in item.description.lower())
        ] # 筛选名称或描述中包含查询字符串的物品

    # 根据最低价格筛选
    if min_price is not None:
        results = [item for item in results if item.price >= min_price] # 筛选价格大于等于最低价格的物品

    # 根据最高价格筛选
    if max_price is not None:
        results = [item for item in results if item.price <= max_price] # 筛选价格小于等于最高价格的物品

    # 根据标签列表筛选
    if tags:
        # 筛选包含所有指定标签的物品
        results = [item for item in results if all(tag in item.tags for tag in tags)]

    return results  # 返回最终筛选结果
