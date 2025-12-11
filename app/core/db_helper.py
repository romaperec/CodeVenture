from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(url=settings.DB_URL, echo=settings.DB_ECHO)
sessionmaker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with sessionmaker() as session:
        yield session


class Base(DeclarativeBase): ...
