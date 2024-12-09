from pydantic import BaseModel
from sql_engine import get_db
from sql_model_ import User
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_user(db: AsyncSession, user_id: int):
    sf = select(User).filter(User.id == user_id)
    res_user = await db.execute(sf)
    # print(res_user.scalars().first())  # 不能在这调用，否则后面就会提示closed
    return res_user.scalars().first()


async def create_user(db: AsyncSession, name: str, email: str):
    db_user = User(name=name, email=email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(db: AsyncSession, user_id: int, name: str = None, email: str = None):
    db_user = await get_user(db, user_id)
    if db_user is None:
        return None
    if name is not None:
        db_user.name = name
    if email is not None:
        db_user.email = email
    await db.commit()
    # 重新从数据库中加载一个对象的当前状态，以覆盖该对象在内存中的当前状态。
    await db.refresh(db_user)  # 并不支持异步模式。
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if db_user is None:
        return None
    await db.delete(db_user)
    await db.commit()
    return db_user


app = FastAPI()


class Users(BaseModel):
    # 这里可以放置一些启动时的初始化代码，比如创建数据库连接池等
    id: int
    name: str
    email: str

    # class Config:
    #     orm_mode = True


@app.on_event("shutdown")
async def shutdown_event():
    # 这里可以放置一些关闭时的清理代码，比如关闭数据库连接池等
    pass


@app.post("/users/", response_model=Users)
async def create_user_route(user: Users, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user.name, user.email)


@app.get("/users/{user_id}", response_model=Users)
async def read_user_route(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/users/{user_id}", response_model=Users)
async def update_user_route(user_id: int, user: Users, db: AsyncSession = Depends(get_db)):
    return await update_user(db, user_id, user.name, user.email)


@app.delete("/users/{user_id}", response_model=Users)
async def delete_user_route(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
