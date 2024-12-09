# 如果有一组查询参数，可以创建pydantic模型来声明他们--这样可以在多个地方使用模型进行校验---测试了下 不可行，会默认是body参数

from typing import List

from fastapi import FastAPI, Query, Body
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal

app = FastAPI()


# literal： 定义一个参数只能接受预定义的几个值中的一个
class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: List[str] = []


@app.get("/items/")
async def read_items(filter_query: FilterParams = Body(...), name: str = Query(...)):
    return filter_query


from typing import Union

from fastapi import Cookie, FastAPI
from pydantic import BaseModel
from typing_extensions import Annotated

app = FastAPI()


class Cookies(BaseModel):
    session_id: str
    fatebook_tracker: Union[str, None] = None
    googall_tracker: Union[str, None] = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies