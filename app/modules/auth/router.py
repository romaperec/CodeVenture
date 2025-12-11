from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.core.jwt_service import JWTService, TokenType
from app.modules.auth.dependencies import get_auth_service, get_jwt_service
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
async def refresh_access_token(
    request: Request, service: AuthService = Depends(get_auth_service)
):
    return await service.update_access_token(request)
