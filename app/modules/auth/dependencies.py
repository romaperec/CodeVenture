from fastapi import Depends

from app.modules.auth.service import AuthService
from app.modules.users.dependencies import get_full_user_service
from app.modules.users.service import UserService


def get_auth_service(
    user_service: UserService = Depends(get_full_user_service),
) -> AuthService:
    return AuthService(user_service)
