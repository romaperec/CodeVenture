from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer

from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.schemas import UserLogin, UserRegister
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/")
async def root():
    return {"Module": "Working!"}


@router.post("/register")
async def register_user(
    schema: UserRegister, service: AuthService = Depends(get_auth_service)
):
    return await service.register_user(schema)


@router.post("/login")
async def login_user(
    response: Response,
    schema: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login_user(schema, response)


@router.post("/refresh")
async def refresh_access_token(request: Request):
    pass
