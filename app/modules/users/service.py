from fastapi import HTTPException, status
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import sessionmaker as async_session_factory
from app.modules.users.models import User
from app.modules.users.schemas import (
    UserCreate,
    UserPrivateResponse,
)


class UserService:
    """Сервис управления пользователями."""

    def __init__(
        self,
        redis_client: Redis,
        db: AsyncSession | None = None,
    ):
        """
        Инициализирует сервис управления пользователями.

        Args:
            redis_client: Клиент Redis для кэширования.
            db: Сессия базы данных (опционально).
        """
        self.redis = redis_client
        self.db = db

    async def get_by_id(self, id: int):
        """Получает пользователя по ID с кэшированием."""
        cached_user = await self.redis.get(f"user:{id}")
        if cached_user:
            return UserPrivateResponse.model_validate_json(cached_user)

        if self.db:
            existing_user = await self.db.execute(select(User).where(User.id == id))
            existing_user = existing_user.scalar_one_or_none()

            if existing_user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
        else:
            async with async_session_factory() as temp_db:
                existing_user = await temp_db.execute(select(User).where(User.id == id))
                existing_user = existing_user.scalar_one_or_none()

                if existing_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found",
                    )

        user_schema = UserPrivateResponse.model_validate(existing_user)

        await self.redis.set(f"user:{id}", user_schema.model_dump_json(), ex=1800)

        return user_schema

    async def get_by_email(self, email: str):
        """Получает пользователя по email."""
        existing_user = await self.db.execute(select(User).where(User.email == email))
        existing_user = existing_user.scalar_one_or_none()

        return existing_user

    async def create_user(self, schema: UserCreate):
        """Создает нового пользователя."""
        password = getattr(schema, "password", None)
        if password:
            new_user = User(
                username=schema.username,
                email=schema.email,
                password=schema.password,
            )
        else:
            new_user = User(
                username=schema.username,
                email=schema.email,
            )

        self.db.add(new_user)
        await self.db.commit()

        logger.debug(f"Был создан пользователь с email: {new_user.email}.")
        return new_user

    async def delete_user(self, id: int):
        """Удаляет пользователя по ID."""
        existing_user = await self.db.execute(select(User).where(User.id == id))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user is None:
            logger.warning(f"Пользователь с id: {id} не был найден в базе данных.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found by id",
            )

        await self.db.delete(existing_user)
        await self.db.commit()

        logger.debug(f"Пользователь с id: {id} был удален.")
        return {"status": "success", "deleted_id": id}

    async def _invalidate_user_cache(self, id: int):
        """Инвалидирует кэш пользователя."""
        await self.redis.delete(f"user:{id}")
        logger.debug(f"Кэш пользователя {id} инвалидирован.")

    async def become_seller(self, id: int):
        """Делает пользователя продавцом."""
        existing_user = await self.db.execute(select(User).where(User.id == id))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user is None:
            logger.warning(f"Пользователь с id: {id} не был найден в базе данных.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found by id",
            )

        if existing_user.is_seller == True:  # noqa: E712
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="User already seller"
            )

        existing_user.is_seller = True

        await self.db.commit()
        await self.db.refresh(existing_user)

        await self._invalidate_user_cache(id)

        return {"status": "success", "seller_id": id}
