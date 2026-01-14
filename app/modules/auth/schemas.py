from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    username: str
    email: EmailStr
    description: str | None


class UserLoginOAuth2(BaseModel):
    username: str | None
    email: EmailStr
