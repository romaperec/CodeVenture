from fastapi import Depends

from app.core.jwt_service import JWTService
from app.modules.auth.service import AuthService
from app.modules.users.dependencies import get_full_user_service
from app.modules.users.service import UserService


def get_jwt_service() -> JWTService:
    return JWTService()


def get_auth_service(
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_full_user_service),
) -> AuthService:
    return AuthService(user_service, jwt_service)
