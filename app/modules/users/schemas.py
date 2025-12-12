from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserPublicResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserPrivateResponse(UserPublicResponse):
    email: str
    is_active: bool
    is_admin: bool
