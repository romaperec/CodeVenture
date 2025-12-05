from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserRegisterResponse(BaseModel):
    username: str
    email: EmailStr
