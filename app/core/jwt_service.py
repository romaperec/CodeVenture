from datetime import UTC, datetime, timedelta
from enum import Enum

import jwt
from jwt.exceptions import PyJWTError
from loguru import logger

from app.core.config import settings
from app.core.schemas import TokenData


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class JWTService:
    def __init__(self) -> None:
        pass

    async def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
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
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
        else:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        to_encode.update({"exp": expire, "token_type": TokenType.REFRESH})
        encoded_jwt: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def verify_token(
        self, token: str, expected_token_type: TokenType
    ) -> TokenData:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")

            if email is None or token_type != expected_token_type:
                return None

            return TokenData(email=email)

        except PyJWTError as e:
            logger.warning(f"JWT Error: {e}")
            return None
