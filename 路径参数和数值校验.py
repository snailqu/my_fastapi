# ######################### Path ######################

# 与使用 Query 为查询参数声明更多的校验和元数据的方式相同，你也可以使用 Path 为路径参数声明相同类型的校验和元数据。
from typing import Union

from fastapi import FastAPI, Path, Query
from typing_extensions import Annotated

app = FastAPI()


# Annotated：允许为参数添加额外的验证信息或元数据
@app.get("/items/{item_id}")
async def read_items(
        item_id: Annotated[int, Path(title="The ID of the item to get")],
        q: Annotated[Union[str, None], Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# *, 传递 * 作为函数的第一个参数。
# Python 不会对该 * 做任何事情，但是它将知道之后的所有参数都应作为关键字参数（键值对），也被称为 kwargs，来调用。即使它们没有默认值。


# ############################## 路径操作配置 ##############################
# 路径操作装饰器支持多种配置参数

# ############# 1.status_code 状态码 ##################
# status_code 用于定义路径操作响应中的 HTTP 状态码。
# 可以直接传递 int 代码， 比如 404。
# 如果记不住数字码的涵义，也可以用 status 的快捷常量
from typing import Set, Union
from fastapi import FastAPI, status
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()


@app.post("/items2/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item


# ############# 2.tags 参数 ##################  -- 在api文档中可看
# tags 参数的值是由 str 组成的 list （一般只有一个 str ），tags 用于为*路径操作*添加标签：
@app.post("/items3/", response_model=Item, tags=["items"])
async def create_item(item: Item):
    return item


@app.get("/items4/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]


@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]


# ############# 3.summary 和 description 参数 ##################
# summary 是对一个路径操作的总结 -- 在api文档中可看
# description 是对路径操作的描述 -- 在api文档中可看
@app.post(
    "/items5/",
    response_model=Item,
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
async def create_item(item: Item):
    return item


# ############# 4.文档字符串（docstring） ##################¶
# 描述内容比较长且占用多行时，可以在函数的 docstring 中声明*路径操作*的描述，FastAPI 支持从文档字符串中读取描述内容。
# 文档字符串支持 Markdown，能正确解析和显示 Markdown 的内容，但要注意文档字符串的缩进。
#  -- 在api文档中可看
@app.post("/items6/", response_model=Item, summary="Create an item")
async def create_item(item: Item):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item


# ############# 5.响应描述 ##################¶
# response_description 参数用于定义响应的描述说明：
class Item(BaseModel):
    name:Union[str,None] = None
    description:Union[str, None] = None
    price:float
    tax: Union[float,None] = None
    tags:Set[str] = set()

@app.get('/items7/',
         tags=['items7'],
         summary='get items',
         response_description='the get items')
async def get_item(item):
    """
    get item from me
    - **item**:the item you give
    - **return**:the item you get
    """
    return item

# ############# 5.弃用路径操作：deprecated ##################
# deprecated 参数可以把*路径操作*标记为弃用，无需直接删除：
@app.get('/items8/',
         tags=['items7'],
         summary='get items',
         response_description='the get items',
         deprecated=True
        )
async def get_item(item):
    """
    get item from me
    - **item**:the item you give
    - **return**:the item you get
    """
    return item