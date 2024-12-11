from fastapi import HTTPException

from fastapi import APIRouter
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from api_routers.denpendices import get_user_header

user_router = APIRouter(
    prefix="/users",
    tags=['users'],
    dependencies=[Depends(get_user_header)],
    responses={"404": {"description": "not find user"}}
)

users_dict = {
    "liudehua":{"name":'ldh',"age":34, 'local':'HongKong'},
    "maobuyi":{"name":'mby',"age":22, 'local':'haerbing'},
    "zhoujielun":{"name":'zjl',"age":32, 'local':'taiwan'},
}
@user_router.get("/")
async def get_users():
    return JSONResponse(content=jsonable_encoder(users_dict))

@user_router.get("/{user_id}")
async def get_user(user_id:str):
    if user_id not in users_dict:
        raise HTTPException(status_code=404, detail="user not exists",)

    return JSONResponse(content=jsonable_encoder(users_dict.get(user_id)))