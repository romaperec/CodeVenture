from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserPublicResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserPrivateResponse(UserPublicResponse):
    is_active: bool
    is_admin: bool
