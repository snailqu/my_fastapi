# ##################### 后台任务¶ ##################################
# 定义：你可以定义在返回响应后运行的后台任务。
# 这对需要在请求之后执行的操作很有用，但客户端不必在接收响应之前等待操作完成。
# 包括这些例子：
#   执行操作后发送的电子邮件通知：
#       由于连接到电子邮件服务器并发送电子邮件往往很“慢”（几秒钟），您可以立即返回响应并在后台发送电子邮件通知。
#   处理数据：
#       例如，假设您收到的文件必须经过一个缓慢的过程，您可以返回一个"Accepted"(HTTP 202)响应并在后台处理它。
from typing import Annotated

# ######## 1.使用 BackgroundTasks¶
# 首先导入 BackgroundTasks 并在 路径操作函数 中使用类型声明 BackgroundTasks 定义一个参数：

# ####### 2.创建一个任务函数
# 创建要作为后台任务运行的函数。
# 它只是一个可以接收参数的标准函数。
# 它可以是 async def 或普通的 def 函数，FastAPI 知道如何正确处理。
# 在这种情况下，任务函数将写入一个文件（模拟发送电子邮件）。
# 由于写操作不使用 async 和 await，我们用普通的 def 定义函数

# ####### 3.添加后台任务: 用 .add_task() 方法将任务函数传到 后台任务 对象中
# .add_task() 接收以下参数：
#   在后台运行的任务函数(write_notification)。
#   应按顺序传递给任务函数的任意参数序列(email)。
#   应传递给任务函数的任意关键字参数(message="some notification")。

from fastapi import BackgroundTasks, FastAPI, Depends

# 标签元数据
tag_li = [
    {"name": "send1", "description": "this is send1, just one backend task"},
    {"name": "send2", "description": "this is send2, have many backend tasks"},
]

app = FastAPI(openapi_tags=tag_li,
              # api元数据
              title="BackGroundTask",
              description='this is the course of the backgroundtask,please learn it carfully',
              summary="Deadpool's favorite app. Nuff said.",
              version="0.0.1",
              terms_of_service="http://example.com/terms/",
              contact={
                  "name": "Deadpoolio the Amazing",
                  "url": "http://x-force.example.com/contact/",
                  "email": "dp@x-force.example.com",
              },
              license_info={
                  "name": "Apache 2.0",
                  "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
              },
              )


def write_notification(email: str, message: str):
    with open("log.txt", mode='w') as f:
        f.write(f"Sending notification to {email}: {message}")


@app.post("/send_notif/{email}", tags=['send1'])
async def send_notification(email: str, backtask: BackgroundTasks):
    backtask.add_task(write_notification, email=email, message="some notification")
    return {"message": "notification has been sent"}


# ################### 依赖注入¶
# 使用 BackgroundTasks 也适用于依赖注入系统，你可以在多个级别声明 BackgroundTasks 类型的参数：在
# 路径操作函数 里，在依赖中(可依赖)，在子依赖中，等等。
# FastAPI 知道在每种情况下该做什么以及如何复用同一对象，因此所有后台任务被合并在一起并且随后在后台运行：

# 创建多个后台任务，其中一个作为依赖项注入
def write_log(message: str):
    with open("log.txt", mode='a') as f:
        f.write(f"{message}")


def write_query(back_tasks11: BackgroundTasks, query: str):
    if query:
        back_tasks11.add_task(write_log, f"query={query}")
    return query


@app.post("/backtask/{email}", tags=['send2'])
async def send_notification2(email: str, back_tasks: BackgroundTasks, query: Annotated[str, Depends(write_query)]):
    content = "the second background task"
    back_tasks.add_task(write_notification, email, content)
    return {"message": "notification has been sent 2"}

# ################# 告诫
# 如果您需要执行繁重的后台计算，并且不一定需要由同一进程运行（例如，您不需要共享内存、变量等），那么使用其他更大的工具（如 Celery）可能更好。

# 它们往往需要更复杂的配置，即消息/作业队列管理器，如RabbitMQ或Redis，但它们允许您在多个进程中运行后台任务，甚至是在多个服务器中。
# 但是，如果您需要从同一个FastAPI应用程序访问变量和对象，或者您需要执行小型后台任务（如发送电子邮件通知），您只需使用 BackgroundTasks 即可。
