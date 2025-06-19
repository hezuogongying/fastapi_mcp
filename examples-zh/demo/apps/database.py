from .models import Item

# 模拟数据库，用于存储物品数据，键为物品ID，值为物品对象

items_db: dict[int, Item] = {}  

# 示例数据：用于初始化数据库中的物品
sample_items = [
    Item(id=1, name="锤子", description="用于敲钉子的工具", price=9.99, tags=["工具", "五金"]),
    Item(id=2, name="螺丝刀", description="用于拧螺丝的工具", price=7.99, tags=["工具", "五金"]),
    Item(id=3, name="扳手", description="用于拧紧螺栓的工具", price=12.99, tags=["工具", "五金"]),
    Item(id=4, name="锯子", description="用于切割木材的工具", price=19.99, tags=["工具", "五金", "切割"]),
    Item(id=5, name="电钻", description="用于钻孔的工具", price=49.99, tags=["工具", "五金", "电动"]),
]

# 将示例数据加载到模拟数据库中
for item_data in sample_items:  # 使用 item_data 避免与函数参数 item 重名
    items_db[item_data.id] = item_data