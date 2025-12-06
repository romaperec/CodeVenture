from pydantic import BaseModel


class UserCreate(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
