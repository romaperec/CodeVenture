from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    url=settings.DB_URL,
    echo=settings.DB_ECHO,
    pool_size=60,
    max_overflow=20,
    pool_timeout=20,
    pool_recycle=3600,
    pool_pre_ping=True,
)
sessionmaker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with sessionmaker() as session:
        yield session


class Base(DeclarativeBase): ...
