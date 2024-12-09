# ################################### 中间件 #########################################
# ################### 中间件定义
"""
"中间件"是一个函数,它在每个请求被特定的路径操作处理之前,以及在每个响应返回之前工作.
    ·它接收你的应用程序的每一个请求.
    ·然后它可以对这个请求做一些事情或者执行任何需要的代码.
    ·然后它将请求传递给应用程序的其他部分 (通过某种路径操作).
    ·然后它获取应用程序生产的响应 (通过某种路径操作).
    ·它可以对该响应做些什么或者执行任何需要的代码.
    ·然后它返回这个 响应.
"""


# ################### 创建中间件
# 在函数的顶部使用装饰器 @app.middleware("http")
# 中间件参数接收如下参数:
#     ·request.
#     ·call_next：一个函数，它将接收 request 作为参数.
#         ·这个函数将 request 传递给相应的 路径操作.
#         ·然后它将返回由相应的路径操作生成的 response.
#     ·然后你可以在返回 response 前进一步修改它.
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
# ######################### 添加 ASGI 中间件¶
# 因为 FastAPI 基于 Starlette，且执行 ASGI 规范，所以可以使用任意 ASGI 中间件。
# 中间件不必是专为 FastAPI 或 Starlette 定制的，只要遵循 ASGI 规范即可。
# 总之，ASGI 中间件是类，并把 ASGI 应用作为第一个参数。
# 因此，有些第三方 ASGI 中间件的文档推荐以如下方式使用中间件：

# from unicorn import UnicornMiddleware
# app = SomeASGIApp()
# new_app = UnicornMiddleware(app, some_config="rainbow")

# #################### 常用中间件
# ##### HTTPSRedirectMiddleware¶
# 强制所有传入请求必须是 https 或 wss。
# 任何传向 http 或 ws 的请求都会被重定向至安全方案。
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

app.add_middleware(HTTPSRedirectMiddleware)


@app.get("/")
async def main():
    return {"message": "Hello World"}

# ##### TrustedHostMiddleware
# 强制所有传入请求都必须正确设置 Host 请求头，以防 HTTP 主机头攻击。
# 支持以下参数：
# allowed_hosts - 允许的域名（主机名）列表。*.example.com 等通配符域名可以匹配子域名
# ，或使用 allowed_hosts=["*"] 允许任意主机名，或省略中间件。
# 如果传入的请求没有通过验证，则发送 400 响应。
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"]
)


@app.get("/")
async def main():
    return {"message": "Hello World"}


# ####### GZipMiddleware¶
# 处理 Accept-Encoding 请求头中包含 gzip 请求的 GZip 响应。
# 中间件会处理标准响应与流响应。

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


@app.get("/")
async def main():
    return "somebigcontent"