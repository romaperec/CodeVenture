import redis.asyncio as redis

from app.core.config import settings

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    ssl=False,
)


async def check_redis():
    try:
        return await r.ping()
    except Exception:
        return False
