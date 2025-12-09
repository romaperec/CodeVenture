from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from redis.asyncio import ConnectionPool, Redis
from app.core.config import settings

redis_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_pool

    redis_pool = ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=100,
    )
    logger.info("Redis connection pool создан.")
    yield

    await redis_pool.disconnect()
    logger.info("Redis connection pool закрыт.")


async def get_redis_client() -> Redis:
    return Redis(connection_pool=redis_pool)
