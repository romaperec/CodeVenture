from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DataBase
    DB_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
    DB_ECHO: bool = False


settings = Settings()
