from fastapi import APIRouter, Depends

from app.modules.products.dependencies import get_full_product_service
from app.modules.products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
async def get_all_products(service: ProductService = Depends(get_full_product_service)):
    return await service.get_all_products()


@router.get("/{id}")
async def get_product(
    id: int, service: ProductService = Depends(get_full_product_service)
):
    return await service.get_product_by_id(id)
