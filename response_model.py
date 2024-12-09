# 响应模型：限定响应返回的内容和规则
from typing import Any, List, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []


@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items/", response_model=List[Item], response_model_exclude_unset=True)  # unset：输出时不显示默认值字段无值的
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]


# status_code; 声明响应的状态码---可以使用 fastapi.status 中的快捷变量
from fastapi import status


# @app.post("/items/", status_code=201)
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}
