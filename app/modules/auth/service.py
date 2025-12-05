from app.modules.auth.schemas import UserRegister, UserRegisterResponse


class AuthService:
    async def register_user(self, schema: UserRegister) -> UserRegisterResponse: ...
