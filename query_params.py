# 查询参数和字符串校验

# 添加约束条件：即使 q 是可选的，但只要提供了该参数，则该参数值**不能超过50个字符的长度**。
from typing import Union, List

from fastapi import FastAPI, Query

app = FastAPI()


# Query对查询参数做校验
# pattern：正则表达式
@app.get("/items/")
async def read_items(
        q: Union[str, None] = Query(default=None, max_length=50, pattern='^ss*')):  # Query 显式地将其声明为查询参数,pattern是正则匹配表达式
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# q: str = Query(default=.../Required, max_length=50, pattern='^ss*') -- 显式的声明一个值是必需的，即将默认参数的默认值设为 ...，同Required
# q: str = Query(max_length=50, pattern='^ss*') -- 这样也是必须参数，不过是隐式的


# 使用 Query 显式地定义查询参数时，可以声明它去接收一组值，或换句话来说，接收多个值。
@app.get("/items2/")
async def read_items(q: Union[List[str], None] = Query(default=None)):
    query_items = {"q": q}
    return query_items


# 元数据：可以添加更多有关查询参数的元数据，比如title和description
@app.get("/items3/")
async def read_items(
        q: Union[str, None] = Query(
            default=None,
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
        ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# alias： 用 alias 参数声明一个别名，该别名将用于在 URL 中查找查询参数值
@app.get("/items4/")
async def read_items(q: Union[str, None] = Query(default=None, alias="item-query")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# deprecated：
# 现在假设你不再喜欢此参数。你不得不将其保留一段时间，因为有些客户端正在使用它，但你希望文档清楚地将其展示为已弃用。
# 那么将参数 deprecated=True 传入 Query
@app.get("/items5/")
async def read_items(
        q: Union[str, None] = Query(
            default=None,
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
