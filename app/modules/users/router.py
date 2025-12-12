from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user_id
from app.modules.users.dependencies import get_cached_user_service
from app.modules.users.schemas import UserPrivateResponse, UserPublicResponse
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPrivateResponse)
async def get_me(
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_cached_user_service),
):
    return await service.get_by_id(user_id)


@router.get("/{id}", response_model=UserPublicResponse)
async def get_user_by_id(
    id: int, service: UserService = Depends(get_cached_user_service)
):
    return await service.get_by_id(id)
