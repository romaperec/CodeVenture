from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    """Схема для создания нового пользователя."""

    username: str | None
    email: str
    password: str | None


class UserPublicResponse(BaseModel):
    """Схема публичного ответа с информацией о пользователе."""

    id: int
    username: str | None
    description: str
    is_seller: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPrivateResponse(UserPublicResponse):
    """Схема приватного ответа с полной информацией о пользователе."""

    id: int
    username: str | None
    email: str
    description: str | None
    is_active: bool
    is_seller: bool
    is_admin: bool
    created_at: datetime
