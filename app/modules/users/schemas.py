from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str | None
    email: str
    password: str | None


class UserPublicResponse(BaseModel):
    id: int
    username: str | None

    model_config = ConfigDict(from_attributes=True)


class UserPrivateResponse(UserPublicResponse):
    email: str
    description: str | None
    is_active: bool
    is_admin: bool
