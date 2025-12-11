from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    email: EmailStr
