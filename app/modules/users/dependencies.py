from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import get_session
from app.modules.users.service import UserService


def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(db)
