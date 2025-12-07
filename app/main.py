from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.redis import check_redis, r
from app.modules.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if await check_redis():
        logger.info("Redis подключен.")
    else:
        logger.warning("Произошла ошибка при подключении Redis.")

    logger.debug("Приложение успешно запущено.")

    yield
    await r.close()


app = FastAPI(title="CodeVenture API", lifespan=lifespan)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"API": "Working!"}
