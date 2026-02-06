from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import get_session
from app.core.redis import get_redis_client
from app.modules.users.service import UserService


def get_full_user_service(
    redis_client: Redis = Depends(get_redis_client),
    db: AsyncSession = Depends(get_session),
) -> UserService:
    """Возвращает экземпляр UserService с доступом к БД."""
    return UserService(redis_client=redis_client, db=db)


def get_cached_user_service(
    redis_client: Redis = Depends(get_redis_client),
) -> UserService:
    """Возвращает экземпляр UserService только с Redis кэшем."""
    return UserService(redis_client=redis_client)
