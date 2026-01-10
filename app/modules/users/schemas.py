from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str | None
    email: str
    password: str | None


class UserPublicResponse(BaseModel):
    id: int
    username: str | None
    description: str
    is_seller: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPrivateResponse(UserPublicResponse):
    id: int
    username: str | None
    email: str
    description: str | None
    is_active: bool
    is_seller: bool
    is_admin: bool
    created_at: datetime
