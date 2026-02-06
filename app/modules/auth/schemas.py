from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Схема для регистрации нового пользователя."""

    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Схема для входа пользователя."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Схема для ответа с информацией о пользователе."""

    username: str
    email: EmailStr
    description: str | None


class UserLoginOAuth2(BaseModel):
    """Схема для входа пользователя через OAuth2."""

    username: str | None
    email: EmailStr
