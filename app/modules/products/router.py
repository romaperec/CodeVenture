from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user_id
from app.modules.products.dependencies import get_full_product_service
from app.modules.products.schemas import ProductCreate
from app.modules.products.service import ProductService


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/healthy")
async def root():
    return {"Module": "Working!"}


@router.post("/create")
async def create_product(
    product: ProductCreate,
    user_id: int = Depends(get_current_user_id),
    # user_service: UserService = Depends(get_cached_user_service),
    service: ProductService = Depends(get_full_product_service),
):
    # user = await user_service.get_by_id(user_id)
    return await service.create_product(user_id, product)


@router.get("/")
async def get_all_products(service: ProductService = Depends(get_full_product_service)):
    return await service.get_all_products()


@router.get("/{id}")
async def get_product(
    id: int, service: ProductService = Depends(get_full_product_service)
):
    return await service.get_product_by_id(id)
