# app/core/jwt_service.py
"""Сервис управления JWT токенами."""

import uuid
from datetime import UTC, datetime, timedelta
from enum import Enum

import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from loguru import logger
from redis.asyncio import Redis

from app.core.config import settings
from app.core.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class TokenType(str, Enum):
    """Типы JWT токенов."""

    ACCESS = "access"
    REFRESH = "refresh"


class JWTService:
    """Сервис для создания, проверки и управления JWT токенами."""

    def __init__(self, redis_client: Redis) -> None:
        """
        Инициализирует JWTService.

        Args:
            redis_client: Клиент Redis для управления refresh токенами.
        """
        self.redis = redis_client

    async def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """Создает access JWT токен."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
        else:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire, "token_type": TokenType.ACCESS})
        encoded_jwt: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def create_refresh_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """Создает refresh JWT токен и сохраняет его в Redis."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
        else:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        token_jti = str(uuid.uuid4())
        user_id = str(data.get("sub"))

        to_encode.update(
            {"exp": expire, "token_type": TokenType.REFRESH, "jti": token_jti}
        )
        encoded_jwt: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        if self.redis:
            current_time = datetime.now(UTC).replace(tzinfo=None)
            ttl_seconds = int((expire - current_time).total_seconds())

            if ttl_seconds > 0:
                await self.redis.set(
                    name=f"refresh_token:{token_jti}", value=user_id, ex=ttl_seconds
                )

        return encoded_jwt

    async def verify_token(
        self, token: str, expected_token_type: TokenType
    ) -> TokenData | None:
        """Проверяет валидность и тип JWT токена."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            jti: str | None = payload.get("jti")

            if user_id is None or token_type != expected_token_type:
                return None

            if expected_token_type == TokenType.REFRESH:
                if self.redis:
                    if not jti:
                        logger.warning("Не получилось получить jti у Refresh токена.")
                        return None

                    is_active = await self.redis.get(f"refresh_token:{jti}")

                    if not is_active:
                        logger.warning("Токен не найден в Redis.")
                        return None

            return TokenData(id=user_id)

        except PyJWTError as e:
            logger.warning(f"JWT Error: {e}")
            return None

    async def revoke_refresh_token(self, token: str):
        """Отзывает refresh токен, удаляя его из Redis."""
        if not self.redis:
            logger.warning("Redis не подключен к jwt_service!")
            return

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_signature": False, "verify_exp": False},
            )

            jti: str | None = payload.get("jti")

            if jti:
                await self.redis.delete(f"refresh_token:{jti}")
                logger.info(f"Refresh токен: {jti} был успешно удален.")
            else:
                logger.warning("Не получилось получить jti у Refresh токена.")
                return

        except PyJWTError as e:
            logger.warning(f"JWT Error: {e}")
            return None
