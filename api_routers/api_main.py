from fastapi import FastAPI
from api_routers.item import item_router
from api_routers.users import user_router

app = FastAPI()

app.include_router(item_router)
app.include_router(user_router)

