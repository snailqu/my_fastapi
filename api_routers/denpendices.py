from fastapi import Header, HTTPException

# dependence
async def get_token_header(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")

async def get_user_header(y_token:str=Header()):
    if y_token!='user':
        raise HTTPException(status_code=400, detail="this is not user token")

