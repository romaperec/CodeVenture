from fastapi import APIRouter, Depends, Request

from app.modules.auth.dependencies import get_current_user_id
from app.modules.products.dependencies import (
    get_cached_product_service,
    get_full_product_service,
)
from app.modules.products.schemas import ProductCreate
from app.modules.products.service import ProductService
from app.core.rate_limit import limiter


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/healthy")
async def root():
    return {"Module": "Working!"}


@router.post("/create")
@limiter.limit("2/minute")
async def create_product(
    request: Request,
    product: ProductCreate,
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    return await service.create_product(user_id, product)


@router.get("/")
async def get_all_products(service: ProductService = Depends(get_full_product_service)):
    return await service.get_all_products()


@router.get("/{id}")
async def get_product(
    id: int, service: ProductService = Depends(get_cached_product_service)
):
    return await service.get_product_by_id(id)
