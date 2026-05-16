import uvicorn
import uuid
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_users import FastAPIUsers
from starlette.responses import Response

from back.src.auth.auth_backend import auth_backend
from back.src.auth.models import User
from back.src.auth.schemas import UserRead, UserCreate
from back.src.auth.user_manager import get_user_manager, UserManager
from back.src.auth.auth_backend import redis

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

from back.src.core.router import router as core_router


app = FastAPI(title="YourToDoList")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_request(request: Request, call_next):
    response: Response = await call_next(request)
    logger.info(f"Request: {request.method} {request.url} {response.status_code}")
    return response

current_user = fastapi_users.current_user()

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

@app.post("/auth/logout", tags=["auth"])
async def logout(user = Depends(current_user), manager: UserManager = Depends(get_user_manager)):
    await redis.delete(user.redis_token_key)
    await manager._update(user, {"redis_token_key": None})

    return {"detail": "Successfully logged out"}

app.include_router(
    fastapi_users.get_auth_router(backend=auth_backend),
    prefix='/auth',
    tags=['auth']
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix='/auth',
    tags=['auth']
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags = ["auth"]
)

app.include_router(core_router)

if __name__ == "__main__":
    uvicorn.run(
        __name__ + ":app",
        host='127.0.0.1',
        port=7000,
        reload=True
    )
    