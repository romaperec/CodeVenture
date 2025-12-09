from fastapi import APIRouter, Depends

from app.modules.users.dependencies import get_cached_user_service
from app.modules.users.service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{id}")
async def get_user_by_id(
    id: int, service: UserService = Depends(get_cached_user_service)
):
    return await service.get_by_id(id)
