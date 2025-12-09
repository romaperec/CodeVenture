from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from redis.asyncio import ConnectionPool, Redis
from app.core.config import settings

redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_pool, redis_client

    redis_pool = ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
        max_connections=500,
    )
    redis_client = Redis(connection_pool=redis_pool)

    await redis_client.ping()
    logger.info("Redis connection pool создан.")

    yield

    await redis_client.aclose()
    await redis_pool.disconnect()
    logger.info("Redis connection pool закрыт.")


def get_redis_client() -> Redis:
    return redis_client
