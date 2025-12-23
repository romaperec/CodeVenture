from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings
from app.core.taskiq import broker

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
    redis_client = Redis(connection_pool=redis_pool, db=settings.REDIS_DB_CACHE)

    await redis_client.ping()
    logger.info(f"Redis Cache подключен (DB {settings.REDIS_DB_CACHE})")

    if not broker.is_worker_process:
        await broker.startup()
    logger.info(f"Taskiq Broker подключен (DB {settings.REDIS_DB_QUEUE})")

    yield

    if not broker.is_worker_process:
        await broker.shutdown()
    logger.info("Taskiq Broker остановлен.")

    await redis_client.aclose()
    await redis_pool.disconnect()
    logger.info("Redis Cache отключен.")


def get_redis_client() -> Redis:
    return redis_client
