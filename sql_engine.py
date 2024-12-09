from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sql_model_ import Base

database_url = "mysql+aiomysql://root:qtzh14174@localhost:3306/test?connect_timeout=10"
engine = create_async_engine(url=database_url, pool_pre_ping=True, echo=True)


async def create_tables_async(async_engine):
    async with async_engine.sync_session() as session1:
        # 注意：这里实际上还是在同步上下文中执行 DDL
        Base.metadata.create_all(bind=session1.get_bind())


# Base.metadata.create_all(bind=engine)  # 该语句是同步环境下创建表

# async def get_db():
#     async with async_sessionmaker() as session:
#         async with session.begin():
#             yield session

# 用于创建会话（Session）对象。会话对象是与数据库进行交互的主要接口，它管理着对象的生命周期、事务以及与数据库的连接。
session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession)


async def get_db():
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
