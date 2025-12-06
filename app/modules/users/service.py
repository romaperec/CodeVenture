from fastapi import HTTPException, status

from loguru import logger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.schemas import UserCreate, UserResponse


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int):
        existing_user = await self.db.execute(select(User).where(User.id == id))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user is None:
            logger.warning(f"Пользователь с id: {id} не был найден в базе данных.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found by id"
            )

        return UserResponse(
            id=existing_user.id,
            username=existing_user.username,
            email=existing_user.email,
        )

    async def get_by_email(self, email: str):
        existing_user = await self.db.execute(select(User).where(User.email == email))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user is None:
            logger.warning(
                f"Пользователь с email: {email} не был найден в базе данных."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found by email"
            )

        return UserResponse(
            id=existing_user.id,
            username=existing_user.username,
            email=existing_user.email,
        )

    async def create_user(self, schema: UserCreate):
        new_user = User(
            username=schema.username,
            email=schema.email,
            password=schema.hashed_password,
        )
        self.db.add(new_user)
        await self.db.commit()

        logger.info(f"Был создан пользователь с email: {new_user.email}.")
        return UserResponse(
            id=new_user.id, username=new_user.username, email=new_user.email
        )

    async def delete_user(self, id: int):
        existing_user = await self.db.execute(select(User).where(User.id == id))
        existing_user = existing_user.scalar_one_or_none()

        if existing_user is None:
            logger.warning(f"Пользователь с id: {id} не был найден в базе данных.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found by id"
            )

        await self.db.delete(existing_user)
        await self.db.commit()

        logger.info(f"Пользователь с id: {id} был удален.")
        return {"status": "success", "deleted_id": id}
