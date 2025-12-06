import asyncio
from fastapi import HTTPException, status
from loguru import logger
from app.core.security import hash_password
from app.modules.auth.schemas import UserRegister
from app.modules.users.service import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register_user(self, schema: UserRegister):
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

        return await self.user_service.create_user(schema)
