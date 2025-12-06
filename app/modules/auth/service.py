from app.modules.auth.schemas import UserRegister


class AuthService:
    def __init__(self, user_service: ...):
        self.user_service = user_service

    async def register_user(self, schema: UserRegister): ...
