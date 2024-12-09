# from sqlalchemy import Column, Integer, String
#
#
# # 创建一个基类。这个基类将作为所有模型类的父类.通过继承这个基类可以创建映射到数据库表的类
# from sqlalchemy.ext.declarative import declarative_base
#
# base = declarative_base()
#


from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True)
    email = Column(String(200), unique=True, index=True)


# 定义一个表模型--物品表（在你的应用启动之前，确保数据库中的表已经存在）
class Items(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    def __repr__(self) -> str:
        return f"Items(id={self.id}, name={self.name}, description={self.description})"
