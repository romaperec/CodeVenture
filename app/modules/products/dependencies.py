from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_helper import get_session
from app.core.redis import get_redis_client
from app.modules.products.service import ProductService


def get_full_product_service(
    redis: Redis = Depends(get_redis_client),
    db: AsyncSession = Depends(get_session),
) -> ProductService:
    return ProductService(redis=redis, db=db)


def get_cached_product_service(
    redis: Redis = Depends(get_redis_client),
) -> ProductService:
    return ProductService(redis=redis)
