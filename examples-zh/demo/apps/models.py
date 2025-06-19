from typing import List, Optional  # 导入类型提示，用于定义列表和可选类型
from sqlmodel import Field, SQLModel   # 导入 SQLModel 用于数据校验和模型定义


class Item(SQLModel):
    """
    物品数据模型，用于定义物品的属性。
    继承自 Pydantic 的 BaseModel，用于数据校验和序列化。
    """
    id: int = Field(default=None, primary_key=True)  # 物品的唯一标识符
    name: str = Field(default=None, max_length=100)  # 物品的名称
    description: Optional[str] = Field(default=None, max_length=100)  # 物品的描述，可选字段
    price: float = Field(default=None)  # 物品的价格
    tags: List[str] = Field(default_factory=list)  # 物品的标签列表，默认为空列表


