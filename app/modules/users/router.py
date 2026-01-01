from fastapi import APIRouter, Depends, Request

from app.core.rate_limit import limiter
from app.modules.auth.dependencies import get_current_user_id
from app.modules.users.dependencies import (
    get_cached_user_service,
    get_full_user_service,
)
from app.modules.users.schemas import UserPrivateResponse, UserPublicResponse
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def root():
    return {"Module": "Working!"}


@router.get("/me", response_model=UserPrivateResponse)
@limiter.limit("60/minute")
async def get_me(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_cached_user_service),
):
    return await service.get_by_id(user_id)


@router.get("/{id}", response_model=UserPublicResponse)
async def get_user_by_id(
    id: int, service: UserService = Depends(get_cached_user_service)
):
    return await service.get_by_id(id)


@router.post("/become-seller")
@limiter.limit("2/minute")
async def become_seller(
    request: Request,
    user_id: int = Depends(get_current_user_id),
    service: UserService = Depends(get_full_user_service),
):
    return await service.become_seller(user_id)
