# app/modules/products/router.py

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile

from app.core.rate_limit import limiter
from app.modules.auth.dependencies import get_current_user_id
from app.modules.products.dependencies import (
    get_cached_product_service,
    get_full_product_service,
)
from app.modules.products.schemas import (
    ProductCreate,
    ProductDetailResponse,
    ProductDownloadResponse,
    ProductFileUploadResponse,
    ProductImageUploadResponse,
    ProductUpdate,
)
from app.modules.products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


# ═══════════════════════════════════════════════════════════════
# CRUD
# ═══════════════════════════════════════════════════════════════


@router.get("/healthy")
async def health_check():
    return {"module": "products", "status": "healthy"}


@router.post("/", status_code=201)
@limiter.limit("10/minute")
async def create_product(
    request: Request,
    product: ProductCreate,
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """Создает новый товар."""
    return await service.create_product(user_id, product)


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_cached_product_service),
):
    """Получает товар по ID."""
    return await service.get_product_with_cache(product_id)


# ═══════════════════════════════════════════════════════════════
# FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════


@router.post(
    "/{product_id}/file",
    response_model=ProductFileUploadResponse,
    summary="Upload product file",
)
@limiter.limit("5/minute")
async def upload_product_file(
    request: Request,
    product_id: int,
    file: UploadFile = File(..., description="Product file (zip, rar, pdf, etc.)"),
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """
    Загружает файл товара.

    - Только владелец может загружать файл
    - Максимальный размер: 500MB
    - Разрешенные форматы: .zip, .rar, .7z, .tar, .gz, .pdf
    """
    return await service.upload_product_file(user_id, product_id, file)


@router.get(
    "/{product_id}/download",
    response_model=ProductDownloadResponse,
    summary="Get download URL",
)
async def get_download_url(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """
    Получает URL для скачивания файла товара.

    - URL действителен 1 час
    - Требуется покупка товара (или быть владельцем)
    """
    return await service.get_download_url(user_id, product_id)


@router.delete("/{product_id}/file")
async def delete_product_file(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """Удаляет файл товара."""
    return await service.delete_product_file(user_id, product_id)


# ═══════════════════════════════════════════════════════════════
# IMAGE OPERATIONS
# ═══════════════════════════════════════════════════════════════


@router.post(
    "/{product_id}/images",
    response_model=ProductImageUploadResponse,
    summary="Upload product image",
)
@limiter.limit("20/minute")
async def upload_product_image(
    request: Request,
    product_id: int,
    file: UploadFile = File(..., description="Image file"),
    is_main: bool = Form(False, description="Set as main image"),
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """
    Загружает изображение товара.

    - Максимум 10 изображений на товар
    - Максимальный размер: 10MB
    - Форматы: .jpg, .jpeg, .png, .gif, .webp
    """
    return await service.upload_product_image(
        user_id=user_id,
        product_id=product_id,
        file=file,
        is_main=is_main,
    )


@router.post(
    "/{product_id}/images/batch",
    response_model=list[ProductImageUploadResponse],
    summary="Upload multiple images",
)
@limiter.limit("5/minute")
async def upload_product_images_batch(
    request: Request,
    product_id: int,
    files: list[UploadFile] = File(..., description="Image files"),
    main_index: int | None = Query(None, description="Index of main image (0-based)"),
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """Загружает несколько изображений за раз."""
    return await service.upload_product_images(
        user_id=user_id,
        product_id=product_id,
        files=files,
        main_index=main_index,
    )


@router.delete("/{product_id}/images/{image_id}")
async def delete_product_image(
    product_id: int,
    image_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """Удаляет изображение товара."""
    return await service.delete_product_image(user_id, product_id, image_id)


@router.patch("/{product_id}/images/{image_id}/main")
async def set_main_image(
    product_id: int,
    image_id: int,
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """Устанавливает изображение как главное."""
    return await service.set_main_image(user_id, product_id, image_id)


@router.patch("/{product_id}/images/reorder")
async def reorder_images(
    product_id: int,
    image_ids: list[int],
    user_id: int = Depends(get_current_user_id),
    service: ProductService = Depends(get_full_product_service),
):
    """Изменяет порядок изображений."""
    return await service.reorder_images(user_id, product_id, image_ids)
