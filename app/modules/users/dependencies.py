from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import get_session
from app.core.redis import get_redis_client
from app.modules.users.service import UserService


def get_user_service(
    db: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis_client),
) -> UserService:
    return UserService(db, redis_client)
