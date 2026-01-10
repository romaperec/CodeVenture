from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FRONTEND_URL: str = "http://localhost:8000"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DataBase
    DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5435/codeventure"
    DB_ECHO: bool = False

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    REDIS_DB_CACHE: int = 0
    REDIS_DB_QUEUE: int = 1

    @cached_property
    def REDIS_URL_QUEUE(self) -> str:
        if not self.REDIS_PASSWORD:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_QUEUE}"
        return (
            f"redis://:{self.REDIS_PASSWORD}@"
            f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB_QUEUE}"
        )

    # Mail
    MAIL_USERNAME: str = "user@gmail.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "user@gmail.com"
    MAIL_FROM_NAME: str = "CodeVenter"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    # Google
    GOOGLE_CLIENT_ID: str = "your_client_id"
    GOOGLE_CLIENT_SECRET: str = "your_client_secret"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"

    # MiniO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_PRODUCTS: str = "products-files"
    MINIO_SECURE: bool = False
    MINIO_MAX_FILE_SIZE_MB: int = 500

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
