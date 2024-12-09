# 创建表单（Form）参数的方式与 Body 和 Query 一样：
from typing import Union, List

from fastapi import FastAPI, Form
from starlette.responses import HTMLResponse

app = FastAPI()


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


# 使用 Form 可以声明与 Body （及 Query、Path、Cookie）相同的元数据和验证。

# Form 是直接继承自 Body 的类。

# 声明表单体要显式使用 Form ，否则，FastAPI 会把该参数当作查询参数或请求体（JSON）参数。

# 表单数据的「媒体类型」编码一般为 application/x-www-form-urlencoded。
# 但包含文件的表单编码为 multipart/form-data

# 可在一个路径操作中声明多个 Form 参数，但不能同时声明要接收 JSON 的 Body 字段。
# 因为此时请求体的编码是 application/x-www-form-urlencoded，不是 application/json。


# form model
from pydantic import BaseModel
from typing_extensions import Annotated

app = FastAPI()


class FormData(BaseModel):
    username: str
    password: str
    model_config = {
        'extra': 'forbid'
    }


@app.post("/login/")
async def login(data: FormData = Form()):
    return data


#  ############# 请求文件 ###################
from fastapi import File, UploadFile


# File 是直接继承自 Form 的类。
@app.post('/load_file/')
async def loadfile(file: bytes = File()):
    print(type(file))
    print(file.decode())
    with open('new_file.py', 'a') as f1:
        for line in file.decode().split('\n'):
            print(line)
            f1.write(line)
    return '保存文件成功'


@app.post('/upload_file/')
async def loadfile(file: UploadFile):
    # uploadFile文件的相关属性
    print(file.file)  # SpooledTemporaryFile（ file-like 对象），就是 Python文件，可直接传递给其他预期 file-like 对象的函数或支持库。
    print(file.content_type)  # 内容类型：image/jpeg
    print(file.filename)  # 文件名

    # 相关方法，async方法 需要搭配await使用
    # write read seek
    await file.seek(1)
    content = await file.read()
    print('文件内容：', content)
    return file.filename


# UploadFile 与 bytes 相比有更多优势：
# 使用 spooled 文件：
# 存储在内存的文件超出最大上限时，FastAPI 会把文件存入磁盘；
# 这种方式更适于处理图像、视频、二进制文件等大型文件，好处是不会占用所有内存；
# 可获取上传文件的元数据；
# 自带 file-like async 接口；
# 暴露的 Python SpooledTemporaryFile 对象，可直接传递给其他预期「file-like」对象的库。

# 不包含文件时，表单数据一般用 application/x-www-form-urlencoded「媒体类型」编码。
# 但表单包含文件时，编码为 multipart/form-data。使用了 File，FastAPI 就知道要从请求体的正确位置获取文件。


# 可以通过使用标准类型注解并将 None 作为默认值的方式将一个文件参数设为可选
@app.post("/files1/")
async def create_file(file: Union[bytes, None] = File(default=None)):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile1/")
async def create_upload_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}


# 您也可以将 File() 与 UploadFile 一起使用，例如，设置额外的元数据
@app.post("/files2/")
async def create_file(file: bytes = File(description="A file read as bytes")):
    return {"file_size": len(file)}


@app.post("/uploadfile2/")
async def create_upload_file(
        file: UploadFile = File(description="A file read as UploadFile"),
):
    return {"filename": file.filename}


# ##################多文件上传¶################################
# FastAPI 支持同时上传多个文件。
# 可用同一个「表单字段」发送含多个文件的「表单数据」。
# 上传多个文件时，要声明含 bytes 或 UploadFile 的列表（List）：
@app.post("/files3/")
async def create_files(files: List[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles3/")
async def create_upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
            <body>
            <form action="/files3/" enctype="multipart/form-data" method="post">
            <input name="files" type="file" multiple>
            <input type="submit">
            </form>
            <form action="/uploadfiles3/" enctype="multipart/form-data" method="post">
            <input name="files" type="file" multiple>
            <input type="submit">
            </form>
            </body>
    """
    return HTMLResponse(content=content)


# ###############FastAPI 支持同时使用 File 和 Form 定义文件和表单字段########################
@app.post("/files4/")
async def create_file(
    file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }