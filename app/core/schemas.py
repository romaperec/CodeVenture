from pydantic import BaseModel
from pydantic.networks import EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(Token):
    email: EmailStr
