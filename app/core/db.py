from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


from app.core.config import settings

engine = create_async_engine(url=settings.DB_URL, echo=settings.DB_ECHO)
session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase): ...
