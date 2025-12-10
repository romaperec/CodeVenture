from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings


class JWTService:
    def __init__(self) -> None:
        pass

    async def create_access_token(
        data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
        else:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire, "token_type": "access"})
        encoded_jwt: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def create_refresh_token(
        data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC).replace(tzinfo=None) + expires_delta
        else:
            expire = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        to_encode.update({"exp": expire, "token_type": "refresh"})
        encoded_jwt: str = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt
