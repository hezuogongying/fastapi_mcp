from fastapi import APIRouter, FastAPI
from typing import Callable, Optional, List

# 引入自定义业务逻辑
from services import logic_a, logic_b


app = FastAPI()


def create_router(
    method: str,
    path: str,
    logic_func: Callable,
    tags: Optional[List[str]] = None,
    include_in_schema: bool = True
):
    router = APIRouter()
    method = method.lower()
    if method == "get":
        @router.get(path, tags=tags, include_in_schema=include_in_schema, response_model=dict[str, str])
        async def get_endpoint(**query):    
            return logic_func(**query)
    elif method == "post":
        @router.post(path, tags=tags, include_in_schema=include_in_schema)
        async def post_endpoint(data: dict):
            return logic_func(data)
    elif method == "put":
        @router.put(path, tags=tags, include_in_schema=include_in_schema)
        async def put_endpoint(data: dict):
            return logic_func(data)
    elif method == "delete":
        @router.delete(path, tags=tags, include_in_schema=include_in_schema)
        async def delete_endpoint(id: int):
            return logic_func(id)
    elif method == "patch":
        @router.patch(path, tags=tags, include_in_schema=include_in_schema)
        async def patch_endpoint(data: dict):
            return logic_func(data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    return router


router_a = create_router("post", "/a", logic_a, tags=["a"])
router_b = create_router("get", "/b", logic_b, tags=["b"])
app.include_router(router_a)
app.include_router(router_b)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)