from fastapi import APIRouter, Depends, Request, Response

from app.core.rate_limit import limiter
from app.core.sso import sso
from app.modules.auth.dependencies import get_auth_service
from app.modules.auth.schemas import UserLogin, UserRegister
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/healthy")
async def root():
    return {"Module": "Working!"}


@router.post("/register", status_code=201)
@limiter.limit("3/minute")
async def register_user(
    request: Request,
    schema: UserRegister,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register_user(schema, response)


@router.post("/login")
@limiter.limit("10/minute")
async def login_user(
    request: Request,
    response: Response,
    schema: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login_user(schema, response)


@router.post("/refresh")
@limiter.limit("30/minute")
async def refresh_access_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    return await service.update_access_token(request, response)


@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    return await service.delete_refresh_token(request, response)


@router.get("/google/login")
async def login_with_google():
    return await sso.get_login_redirect()


@router.get("/google/callback")
async def login_with_google_callback(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    return await service.auth_user_with_google(request, response)
