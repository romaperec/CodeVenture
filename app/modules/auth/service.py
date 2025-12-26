import asyncio
from datetime import timedelta

from fastapi import HTTPException, Request, Response, status
from loguru import logger

from app.core.config import settings
from app.core.jwt_service import JWTService, TokenType
from app.core.security import hash_password, verify_password
from app.modules.auth.schemas import UserLogin, UserRegister
from app.modules.auth.tasks import send_welcome_email
from app.modules.users.service import UserService


class AuthService:
    def __init__(self, user_service: UserService, jwt_service: JWTService):
        self.user_service = user_service
        self.jwt_service = jwt_service

    async def register_user(self, schema: UserRegister, response: Response):
        existing_user = await self.user_service.get_by_email(schema.email)

        if existing_user:
            logger.warning(
                f"Попытка регистрации с занятым аккаунтом. Email: {schema.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = await asyncio.to_thread(hash_password, schema.password)
        schema.password = hashed_password

        new_user = await self.user_service.create_user(schema)

        await send_welcome_email.kiq(schema.email)

        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await self.jwt_service.create_access_token(
            data={"sub": str(new_user.id)},
            expires_delta=access_token_expire,
        )

        refresh_token = await self.jwt_service.create_refresh_token(
            data={"sub": str(new_user.id)}
        )
        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def login_user(self, schema: UserLogin, response: Response) -> dict:
        existing_user = await self.user_service.get_by_email(schema.email)

        if existing_user is None:
            logger.warning(
                f"Неудачная попытка входа. Пользователя с email: {schema.email} не существует."
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        correct_password = await asyncio.to_thread(
            verify_password, schema.password, existing_user.password
        )

        if not correct_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await self.jwt_service.create_access_token(
            data={"sub": str(existing_user.id)},
            expires_delta=access_token_expire,
        )

        refresh_token = await self.jwt_service.create_refresh_token(
            data={"sub": str(existing_user.id)}
        )
        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def update_access_token(self, request: Request, response: Response) -> dict:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing.",
            )

        user_data = await self.jwt_service.verify_token(
            refresh_token, TokenType.REFRESH
        )
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        await self.jwt_service.revoke_refresh_token(refresh_token)

        new_access_token = await self.jwt_service.create_access_token(
            data={"sub": str(user_data.id)}
        )
        new_refresh_token = await self.jwt_service.create_refresh_token(
            data={"sub": str(user_data.id)}
        )

        max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=max_age,
        )

        logger.debug(
            f"Все токены были успешно обновлены для пользователя с id: {user_data.id}"
        )
        return {"access_token": new_access_token, "token_type": "bearer"}

    async def delete_refresh_token(self, request: Request, response: Response):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing.",
            )

        response.delete_cookie(
            "refresh_token",
            domain="localhost",
            path="/",
            secure=False,
            samesite="lax",
        )

        await self.jwt_service.revoke_refresh_token(refresh_token)

        return {"status": "success"}
