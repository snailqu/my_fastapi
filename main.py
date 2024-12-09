from fastapi import FastAPI

app = FastAPI()


@app.get('/')
async def test(name: str):
    return "my name is {}".format(name)


# ####################### 路径参数 #################################
# @app.get('/item/{itemid}/')  # 查询参数 放在/之间用{}包裹的参数
# async def test(itemid: str):
#     return "my itemid is {}".format(itemid)


# 声明路径参数的类型
@app.get('/item/{itemid}/')
async def test(itemid: int):
    return "my itemid is {}".format(itemid)


# 路径操作函数的顺序很重要,有相同路径的，特殊的函数要放在前面
@app.get('/user/me')  # 若果这个放在后面，则永远不可能输出 the user name is qutao
async def test():
    return "the user  name is qutao"


@app.get('/user/{userid}')
async def test(userid: int):
    return "the user  name is {}".format(userid)


# 预定义路径参数 Enum
from enum import Enum


class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, 'message': 'deep learning ftw'}
    if model_name is ModelName.resnet:
        return {"model_name": model_name, 'message': 'lecnn all the images'}
    if model_name is ModelName.lenet:
        return {"model_name": model_name, 'message': 'have some resduals'}


# 包含路径的路径参数--使用路径转换器 /file/{file_path:path}
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# ########################### 查询参数 ################################
# 注意： 声明的参数不是路径参数时，路径操作函数会把该参数自动解释为**查询**参数
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


# ############################ 请求体  ###############################
"""FastAPI 使用**请求体**从客户端（例如浏览器）向 API 发送数据。

**请求体**是客户端发送给 API 的数据。**响应体**是 API 发送给客户端的数据。

API 基本上肯定要发送**响应体**，但是客户端不一定发送**请求体**。

使用 Pydantic 模型声明**请求体**，能充分利用它的功能和优点。
"""

# 导入 Pydantic 的 BaseModel
from pydantic import BaseModel
from typing import Union, Set


# 创建数据模型
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


@app.post("/items1/")
async def create_item(item: Item):  # 声明请求体参数;请求体参数类型是个数据模型
    s = item.name.upper()
    return s


# 可以同时声明路径参数和请求体。
@app.put("/items1/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


# ### 请求体-字段：使用Pydantic的Field在Pydantic模型内部声明校验和元数据
from fastapi import Body
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Item1(BaseModel):
    name: str
    description: Union[str, None] = Field(default=None, title='des of the item', max_length=300)
    price: float = Field(gt=0, description='greater than 0')
    tax: Union[float, None] = None


@app.put('items2/{itemid}')
async def update_item(itemid: int, item: Annotated[Item, Body(embed=True)]):
    res = {'item_id': itemid,
           'item': item}
    return res


# 请求体--嵌套模型：List Dict Tuple
from typing import List, Dict, Tuple


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


# 定义子模型
class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    image: Union[Image, None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


"""这意味着 FastAPI 将期望类似于以下内容的请求体：

{
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2,
    "tags": ["rock", "metal", "bar"],
    "image": {
        "url": "http://example.com/baz.jpg",
        "name": "The Foo live"
    }
}
"""


# 可以将 Pydantic 模型用作 list、set 等的子类型
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    images: Union[List[Image], None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


# Dict类型嵌套[int, folat] -- key是int类型，value是float类型
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights


# ################# 可以同时声明多个请求体 #######################
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


# 它将使用参数名称作为请求体中的键（字段名称），并期望一个类似于以下内容的请求体：
#
# {
#     "item": {
#         "name": "Foo",
#         "description": "The pretender",
#         "price": 42.0,
#         "tax": 3.2
#     },
#     "user": {
#         "username": "dave",
#         "full_name": "Dave Grohl"
#     }
# }

# 当有个单一值的请求体，和其他请求体放在一起，可能会被默认为查询参数。所以可以用Body声明为请求体参数
@app.put("/items12/{item_id}")
async def update_item(
        item_id: int,
        item: Item,
        user: User,
        importance: Annotated[int, Body()]  # 单值请求体参数
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


# ################# 表单 #################################
# 接收的不是 JSON，而是表单字段时，要使用 Form
from fastapi import FastAPI, Form


# app = FastAPI()


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


class FormData(BaseModel):
    username: str
    password: str
    model_config = {"extra": "forbid"}


@app.post("/login1/")
async def login(data: FormData = Form()):
    return data


# ################################ JSON 兼容编码器：jsonable_encoder ################################
# 在某些情况下，您可能需要将数据类型（如Pydantic模型）转换为与JSON兼容的数据类型（如dict、list等）。
# 比如，如果您需要将其存储在数据库中。
# 对于这种要求， **FastAPI**提供了jsonable_encoder()函数。

"""
让我们假设你有一个数据库名为fake_db，它只能接收与JSON兼容的数据。
例如，它不接收datetime这类的对象，因为这些对象与JSON不兼容。
因此，datetime对象必须将转换为包含ISO格式化的str类型对象。
同样，这个数据库也不会接收Pydantic模型（带有属性的对象），而只接收dict。
对此你可以使用jsonable_encoder。
它接收一个对象，比如Pydantic模型，并会返回一个JSON兼容的版本：
"""
from datetime import datetime
from typing import Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

fake_db = {}


class Item(BaseModel):
    title: str
    timestamp: datetime
    description: Union[str, None] = None


@app.put("/items-json-loader/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return fake_db


# ##################### 请求体更新数据：put #################
# 可以先用jsonable_encoder 将输入数据转成jison格式，然后存储进数据库

from typing import List, Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Item(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[float, None] = None
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items-put1/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


@app.put("/items-put2/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded

# ##################### 用 PATCH 进行部分更新 #################

# 使用 Pydantic 的 exclude_unset 参数¶
# 更新部分数据时，可以在 Pydantic 模型的 .dict() 中使用 exclude_unset 参数。
# 比如，item.dict(exclude_unset=True)。
# 这段代码生成的 dict 只包含创建 item 模型时显式设置的数据，而不包括默认值。
# 然后再用它生成一个只含已设置（在请求中所发送）数据，且省略了默认值的 dict：

'''
更新部分数据小结¶
简而言之，更新部分数据应：

使用 PATCH 而不是 PUT （可选，也可以用 PUT）；
提取存储的数据；
把数据放入 Pydantic 模型；
生成不含输入模型默认值的 dict （使用 exclude_unset 参数）；
只更新用户设置过的值，不用模型中的默认值覆盖已存储过的值。
为已存储的模型创建副本，用接收的数据更新其属性 （使用 update 参数）。
把模型副本转换为可存入数据库的形式（比如，使用 jsonable_encoder）。
这种方式与 Pydantic 模型的 .dict() 方法类似，但能确保把值转换为适配 JSON 的数据类型，例如， 把 datetime 转换为 str 。
把数据保存至数据库；
返回更新后的模型。
'''
from typing import List, Union

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

class Item(BaseModel):
    name: Union[str, None] = None
    description: Union[str, None] = None
    price: Union[float, None] = None
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


