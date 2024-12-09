'''
FastAPI 提供了简单易用，但功能强大的**依赖注入**系统。
这个依赖系统设计的简单易用，可以让开发人员轻松地把组件集成至 FastAPI。
'''

# ################################## 什么是「依赖注入」 ###############################
# 编程中的**「依赖注入」**是声明代码（本文中为*路径操作函数* ）运行所需的，或要使用的「依赖」
# 的一种方式。

# 然后，由系统（本文中为 FastAPI）负责执行任意需要的逻辑，为代码提供这些依赖（「注入」依赖项）。
# 依赖注入常用于以下场景：
# 共享业务逻辑（复用相同的代码逻辑）
# 共享数据库连接
# 实现安全、验证、角色权限
# 等……
# 上述场景均可以使用**依赖注入**，将代码重复最小化。


# ################################## 依赖注入的工作机制 ##############################
# ############## 第一步：创建依赖项¶
# 依赖项就是一个函数，且可以使用与*路径操作函数*相同的参数：可以把依赖项当做没有装饰器的路径操作函数
import json
from typing import Union
import requests
from fastapi import Depends, FastAPI

app = FastAPI()


async def common_parameters(
        q: Union[str, None] = None, skip: int = 0, limit: int = 100
):
    limit = limit + 111
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons


# 依赖项的入参即是对应的路径操作函数的入参
# 用正确的参数调用依赖项函数（「可依赖项」）
# 获取函数返回的结果
# 把函数返回的结果赋值给*路径操作函数*的参数

"""
要不要使用 async？¶
FastAPI 调用依赖项的方式与*路径操作函数*一样，因此，定义依赖项函数，也要应用与路径操作函数相同的
规则。即，既可以使用异步的 async def，也可以使用普通的 def 定义依赖项。
在普通的 def *路径操作函数*中，可以声明异步的 async def 依赖项；也可以在异步的
 async def *路径操作函数*中声明普通的 def 依赖项。
上述这些操作都是可行的，FastAPI 知道该怎么处理。
"""

# ################################## 类作为依赖项 ##################################
# 依赖项应该是 "可调用对象"，可以是函数，也可以是类
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: Union[str, None] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    # async def read_items(ccommons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response


# ################################## 子依赖项 ##################################
# FastAPI 支持创建含**子依赖项**的依赖项。并且，可以按需声明任意**深度**的子依赖项嵌套层级。
# FastAPI 负责处理解析不同深度的子依赖项。
from fastapi import Cookie


def query_extractor(q: Union[str, None] = None):
    return q


# 尽管该函数自身是依赖项，但还声明了另一个依赖项（它「依赖」于其他对象）
# 该函数依赖 query_extractor, 并把 query_extractor 的返回值赋给参数 q
# 同时，该函数还声明了类型是 str 的可选 cookie（last_query）
# 用户未提供查询参数 q 时，则使用上次使用后保存在 cookie 中的查询
def query_or_cookie_extractor(
        q: str = Depends(query_extractor),
        last_query: Union[str, None] = Cookie(default=None),
):
    if not q:
        return last_query
    return q


@app.get("/items/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}


# ################################## 多次使用同一个依赖项¶
# 如果在同一个*路径操作* 多次声明了同一个依赖项，例如，多个依赖项共用一个子依赖项，FastAPI
# 在处理同一请求时，只调用一次该子依赖项。
#
# FastAPI 不会为同一个请求多次调用同一个依赖项，而是把依赖项的返回值进行「缓存」，
# 并把它传递给同一请求中所有需要使用该返回值的「依赖项」。
#
# 在高级使用场景中，如果不想使用「缓存」值，而是为需要在同一请求的每一步操作（多次）中都实际调用
# 依赖项，可以把 Depends 的参数 use_cache 的值设置为 False :
# async def needy_dependency(fresh_value: str = Depends(get_value, use_cache=False)):
#     return {"fresh_value": fresh_value}


# ################################## 路径操作装饰器依赖项 ###########################
# 有时，我们并不需要在路径操作函数中使用依赖项的返回值。
# 或者说，有些依赖项不返回值。
# 但仍要执行或解析该依赖项。
# 对于这种情况，不必在声明路径操作函数的参数时使用 Depends，而是可以在路径操作装饰器中添加一个由
# dependencies 组成的 list。
from fastapi import Depends, FastAPI, Header, HTTPException
import uvicorn

app = FastAPI()


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


async def show_name(nm: Union[str, None] = None):
    if nm:
        nm = nm + 'is mine'
    return nm


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items(name: str = Depends(show_name)):
    return [{"item": "Foo"}, {"item": "Bar"}, {"name": name}]


# ############################ 全局依赖项¶  ############################
# 有时，我们要为整个应用添加依赖项。
# 通过与定义路径装饰器依赖项 类似的方式，可以把依赖项添加至整个 FastAPI 应用。
# 这样一来，就可以为所有路径操作应用该依赖项：

from fastapi import Depends, FastAPI, Header, HTTPException


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])


@app.get("/items/")
async def read_items():
    return [{"item": "Portal Gun"}, {"item": "Plumbus"}]


@app.get("/users/")
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


from fastapi import Depends, FastAPI, HTTPException
from typing_extensions import Annotated

# app = FastAPI()


data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}


class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


@app.get("/items/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError(username)
    return item


@app.get('/cors')
def get_cors(name):
    res = requests.get(url='http://localhost:3322/cors/main?name={}'.format(name))
    print(res.json())
    return res.json()


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=2212)
