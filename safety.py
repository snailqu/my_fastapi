"""
OAuth2¶
OAuth2是一个规范，它定义了几种处理身份认证和授权的方法。
它是一个相当广泛的规范，涵盖了一些复杂的使用场景。
它包括了使用「第三方」进行身份认证的方法。
这就是所有带有「使用 Facebook，Google，Twitter，GitHub 登录」的系统背后所使用的机制。

OAuth 1¶
有一个 OAuth 1，它与 OAuth2 完全不同，并且更为复杂，因为它直接包含了有关如何加密通信的规范。
如今它已经不是很流行，没有被广泛使用了。
OAuth2 没有指定如何加密通信，它期望你为应用程序使用 HTTPS 进行通信。

OpenID Connect¶
OpenID Connect 是另一个基于 OAuth2 的规范。
它只是扩展了 OAuth2，并明确了一些在 OAuth2 中相对模糊的内容，以尝试使其更具互操作性。
例如，Google 登录使用 OpenID Connect（底层使用OAuth2）。
但是 Facebook 登录不支持 OpenID Connect。它具有自己的 OAuth2 风格。

OpenID（非「OpenID Connect」）¶
还有一个「OpenID」规范。它试图解决与 OpenID Connect 相同的问题，但它不是基于 OAuth2。
因此，它是一个完整的附加系统。
如今它已经不是很流行，没有被广泛使用了。

OpenAPI¶
OpenAPI（以前称为 Swagger）是用于构建 API 的开放规范（现已成为 Linux Foundation 的一部分）。
FastAPI 基于 OpenAPI。
这就是使多个自动交互式文档界面，代码生成等成为可能的原因。
OpenAPI 有一种定义多个安全「方案」的方法。
通过使用它们，你可以利用所有这些基于标准的工具，包括这些交互式文档系统。
OpenAPI 定义了以下安全方案：
    · apiKey：一个特定于应用程序的密钥，可以来自：
        · 查询参数。
        · 请求头。
        · cookie。
    · http：标准的 HTTP 身份认证系统，包括：
        · bearer: 一个值为 Bearer 加令牌字符串的 Authorization 请求头。这是从 OAuth2 继承的。
        · HTTP Basic 认证方式。
        · HTTP Digest，等等。
    · oauth2：所有的 OAuth2 处理安全性的方式（称为「流程」）。 *以下几种流程适合构建 OAuth 2.0
     身份认证的提供者（例如 Google，Facebook，Twitter，GitHub 等）：
     * implicit * clientCredentials * authorizationCode
        · 但是有一个特定的「流程」可以完美地用于直接在同一应用程序中处理身份认证：
            · password：接下来的几章将介绍它的示例。
    · openIdConnect：提供了一种定义如何自动发现 OAuth2 身份认证数据的方法。
        · 此自动发现机制是 OpenID Connect 规范中定义的内容。
"""

# FastAPI 在 fastapi.security 模块中为每个安全方案提供了几种工具，
# 这些工具简化了这些安全机制的使用方法。

# ############################### 安全- 第一步 ####################################
'''
假设后端 API 在某个域。
前端在另一个域，或（移动应用中）在同一个域的不同路径下。
并且，前端要使用后端的 username 与 password 验证用户身份。
固然，FastAPI 支持 OAuth2 身份验证。
但为了节省开发者的时间，不要只为了查找很少的内容，不得不阅读冗长的规范文档。
我们建议使用 FastAPI 的安全工具。
'''
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


"""
Password 流是 OAuth2 定义的，用于处理安全与身份验证的方式（流）。
OAuth2 的设计目标是为了让后端或 API 独立于服务器验证用户身份。
但在本例中，FastAPI 应用会处理 API 与身份验证。
下面，我们来看一下简化的运行流程：
    ·用户在前端输入 username 与password，并点击回车
    ·（用户浏览器中运行的）前端把 username 与password 发送至 API 中指定的 URL
        （使用 tokenUrl="token" 声明）
    ·API 检查 username 与password，并用令牌（Token） 响应（暂未实现此功能）：
    ·令牌只是用于验证用户的字符串
    ·一般来说，令牌会在一段时间后过期
        ·过时后，用户要再次登录
        ·这样一来，就算令牌被人窃取，风险也较低。因为它与永久密钥不同，在绝大多数情况下不会长期有效
    ·前端临时将令牌存储在某个位置
    ·用户点击前端，前往前端应用的其它部件
    ·前端需要从 API 中提取更多数据：
        ·为指定的端点（Endpoint）进行身份验证
        ·因此，用 API 验证身份时，要发送值为 Bearer + 令牌的请求头 Authorization
        ·假如令牌为 foobar，Authorization 请求头就是： Bearer foobar

创建 OAuth2PasswordBearer 的类实例时，要传递 tokenUrl 参数。该参数包含客户端（用户浏览器中运
行的前端） 的 URL，用于发送 username 与 password，并获取令牌。
     
在此，tokenUrl="token" 指向的是暂未创建的相对 URL token。这个相对 URL 相当于 ./token。
因为使用的是相对 URL如果 API 位于 https://example.com/，则指向 https://example.com/token。
但如果 API 位于 https://example.com/api/v1/，它指向的就是
https://example.com/api/v1/token。
使用相对 URL 非常重要，可以确保应用在遇到使用代理这样的高级用例时，也能正常运行。
"""

# ##################### OAuth2 实现简单的 Password 和 Bearer 验证 #####################
"""
1.获取 username 和 password¶
    首先，使用 FastAPI 安全工具获取 username 和 password。
    OAuth2 规范要求使用密码流时，客户端或用户必须以<表单数据形式>发送 username 和 password 字段。
    并且，这两个字段必须命名为 username 和 password ，不能使用 user-name 或 email 等其它名称。
    但对于登录路径操作，则要使用兼容规范的 username 和 password，（例如，实现与 API 文档集成）。
    该规范要求必须以表单数据形式发送 username 和 password，因此，不能使用 JSON 对象。
    
2.Scope（作用域）¶
    OAuth2 还支持客户端发送scope表单字段。
    虽然表单字段的名称是 scope（单数），但实际上，它是以空格分隔的，由多个scope组成的长字符串。
    作用域只是不带空格的字符串。
    常用于声明指定安全权限，例如：
        常见用例为，users:read 或 users:write
        脸书和 Instagram 使用 instagram_basic
        谷歌使用 https://www.googleapis.com/auth/drive
        
3.返回 Token¶
    token 端点的响应必须是 JSON 对象。
    响应返回的内容应该包含 token_type。本例中用的是BearerToken，因此， Token 类型应为bearer。
    返回内容还应包含 access_token 字段，它是包含权限 Token 的字符串。
    本例只是简单的演示，返回的 Token 就是 username，但这种方式极不安全。
    
4.更新依赖项¶
    接下来，更新依赖项。
    使之仅在当前用户为激活状态时，才能获取 current_user。
    为此，要再创建一个依赖项 get_current_active_user，此依赖项以 get_current_user 依赖项为
        基础。
    如果用户不存在，或状态为未激活，这两个依赖项都会返回 HTTP 错误。
    因此，在端点中，只有当用户存在、通过身份验证、且状态为激活时，才能获得该用户：
"""
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()


def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """仅在当前用户为激活状态时，才能获取 current_user"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# OAuth2PasswordRequestForm 是用以下几项内容声明表单请求体的类依赖项：
# username
# password
# 可选的 scope 字段，由多个空格分隔的字符串组成的长字符串
# 可选的 grant_type
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 使用表单字段 username，从（伪）数据库中获取用户数据。
    user_dict = fake_users_db.get(form_data.username)

    # 如果不存在指定用户，则返回错误消息，提示用户名或密码错误。
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # 首先将数据放入 Pydantic 的 UserInDB 模型。
    user = UserInDB(**user_dict)  # 直接把 user_dict 的键与值当作关键字参数传递

    # 将传入的密码字符通过哈希函数转换为指定编码
    hashed_password = fake_hash_password(form_data.password)

    # 如果转换后的密码编码与数据库存储的对应账号的密码不相等，抛出密码错误
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # access_token：包含权限 Token 的字符串。 本例中用的是BearerToken，token_type是bearer
    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


"""
使用以上的方案实现基于 username 和 password 的完整 API 安全系统。
这些工具让安全系统兼容任何数据库、用户及数据模型。
唯一欠缺的是，它仍然不是真的安全。
>>> 接下来使用密码哈希支持库与JWT令牌实现真正的安全机制
"""

# ###################### OAuth2 实现密码哈希与 Bearer JWT 令牌验证  ####################
# ################## JWT 简介
# 定义：JWT 即JSON 网络令牌（JSON Web Tokens）。
# 目的：JWT的目的是在不同的服务和客户端之间安全地传输信息，这些信息可以是用户身份验证、访问权限等
# 格式：
# Header（头部）：包含令牌的类型和所使用的签名算法。
# Payload（负载）：包含令牌的具体信息，如用户ID、角色等。
# Signature（签名）：用于验证令牌的完整性和真实性
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6I
# kpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_
# adQssw5c
# JWT 字符串没有加密，任何人都能用它恢复原始信息。
# 但 JWT 使用了签名机制。接受令牌时，可以用签名校验令牌。
# 使用 JWT 创建有效期为一周的令牌。第二天，用户持令牌再次访问时，仍为登录状态。
# 令牌于一周后过期，届时，用户身份验证就会失败。只有再次登录，才能获得新的令牌。如果用户（或第三方）
# 篡改令牌的过期时间，因为签名不匹配会导致身份验证失败。

# ################## 密码哈希
# 哈希是指把特定内容（本例中为密码）转换为乱码形式的字节序列（其实就是字符串）。
# 每次传入完全相同的内容时（比如，完全相同的密码），返回的都是完全相同的乱码。
# 但这个乱码无法转换回传入的密码。

# 密码哈希与校验¶
# 1.从 passlib 导入所需工，创建用于密码哈希和身份校验的 PassLib 上下文。

# 2.创建三个工具函数，
#     其中一个函数用于哈希用户的密码。
#     第二个函数用于校验接收的密码是否匹配存储的哈希值。
#     第三个函数用于身份验证，并返回用户。
from datetime import datetime, timedelta, timezone
from typing import Union

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from typing_extensions import Annotated

# to get a string like this run:
# openssl rand -hex 32 ：创建用于 JWT 令牌签名的随机密钥
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# 指定 JWT 令牌签名算法
ALGORITHM = "HS256"

# 设置令牌过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    接收JWT 令牌,解码并校验接收到的令牌，然后，返回当前用户
    :param token:
    :return:
    """
    # 如果令牌无效，则直接返回 HTTP 错误
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 用令牌过期时间创建 timedelta 对象
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 创建并返回真正的 JWT 访问令牌
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
        current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

# sub 键是可选的，在整个应用中应该只有一个唯一的标识符，而且应该是字符串
# JWT可以为实体添加权限，比如驾驶（汽车）或编辑（博客）。
# 把 JWT 令牌交给用户（或机器人），他们就可以执行驾驶汽车，或编辑博客等操作。无需注册账户
# ，只要有 API 生成的 JWT 令牌就可以。


# ################### scopes 高级用法¶
# OAuth2 支持scopes（作用域）。
# scopes为 JWT 令牌添加指定权限。
# 让持有令牌的用户或第三方在指定限制条件下与 API 交互。
# 高级用户指南中将介绍如何使用 scopes，及如何把 scopes 集成至 FastAPI。