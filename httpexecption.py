"""某些情况下，需要向客户端返回错误提示。

这里所谓的客户端包括前端浏览器、其他应用程序、物联网设备等。

需要向客户端返回错误提示的场景主要如下：

客户端没有执行操作的权限
客户端没有访问资源的权限
客户端要访问的项目不存在
等等 ..."""

'''
遇到这些情况时，通常要返回 4XX（400 至 499）HTTP 状态码。
4XX 状态码与表示请求成功的 2XX（200 至 299） HTTP 状态码类似。
只不过，4XX 状态码表示客户端发生的错误。
'''

# 向客户端返回 HTTP 错误响应，可以使用 HTTPException
from fastapi import FastAPI, HTTPException

app = FastAPI()

items = {"foo": "The Foo Wrestlers"}


@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}


# #################触发HTTPException：####################
# HTTPException 是额外包含了和 API 有关数据的常规 Python 异常。
# 因为是 Python 异常，所以不能 return，只能 raise


# 如在调用*路径操作函数*里的工具函数时，触发了 HTTPException，FastAPI 就不再继续执行*路径操作函数*中的后续代码，
# 而是立即终止请求，并把 HTTPException 的 HTTP 错误发送至客户端。


# ################################### 添加自定义响应头 ##################################
# 有些场景下要为 HTTP 错误添加自定义响应头。例如，出于某些方面的安全需要。
# 一般情况下可能不会需要在代码中直接使用响应头。但对于某些高级应用场景，还是需要添加自定义响应头：
# items = {"foo": "The Foo Wrestlers"}


@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


# ################################### 安装自定义异常处理器¶ ###################################
# 添加自定义处理器，要使用 Starlette 的异常工具。
# 假设要触发的自定义异常叫作 UnicornException。
# 且需要 FastAPI 实现全局处理该异常。
# 此时，可以用 @app.exception_handler() 添加自定义异常控制器：
from fastapi import Request
from fastapi.responses import JSONResponse


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


# 使用 RequestValidationError 的请求体¶
# RequestValidationError 包含其接收到的无效数据请求的 body 。
#
# 开发时，可以用这个请求体生成日志、调试错误，并返回给用户。
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


class Item(BaseModel):
    title: str
    size: int


@app.post("/items/")
async def create_item(item: Item):
    return item