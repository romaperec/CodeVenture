from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis

from app.core.jwt_service import JWTService, TokenType, oauth2_scheme
from app.core.redis import get_redis_client
from app.modules.auth.service import AuthService
from app.modules.users.dependencies import get_full_user_service
from app.modules.users.service import UserService


def get_jwt_service(redis_client: Redis = Depends(get_redis_client)) -> JWTService:
    return JWTService(redis_client)


def get_auth_service(
    jwt_service: JWTService = Depends(get_jwt_service),
    user_service: UserService = Depends(get_full_user_service),
) -> AuthService:
    return AuthService(user_service, jwt_service)


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
):
    payload = await jwt_service.verify_token(token, TokenType.ACCESS)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return payload.id
