# app/modules/products/schemas.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# ═══════════════════════════════════════════════════════════════
# CREATE / UPDATE
# ═══════════════════════════════════════════════════════════════


class ProductCreate(BaseModel):
    """Схема для создания нового товара."""

    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10)
    price: float = Field(..., ge=0)


class ProductUpdate(BaseModel):
    """Схема для обновления товара."""

    title: str | None = Field(None, min_length=3, max_length=150)
    description: str | None = Field(None, min_length=10)
    price: float | None = Field(None, ge=0)
    is_published: bool | None = None


# ═══════════════════════════════════════════════════════════════
# IMAGE RESPONSES
# ═══════════════════════════════════════════════════════════════


class ProductImageResponse(BaseModel):
    """Ответ с информацией об изображении товара."""

    id: int
    image_url: str
    is_main: bool
    position: int

    model_config = ConfigDict(from_attributes=True)


class ProductImageUploadResponse(BaseModel):
    """Ответ после загрузки изображения товара."""

    id: int
    image_url: str
    original_name: str
    size: int
    is_main: bool
    position: int


# ═══════════════════════════════════════════════════════════════
# FILE RESPONSES
# ═══════════════════════════════════════════════════════════════


class ProductFileInfo(BaseModel):
    """Информация о файле товара."""

    file_name: str | None
    file_size: int | None
    file_content_type: str | None
    has_file: bool


class ProductFileUploadResponse(BaseModel):
    """Ответ после загрузки файла товара."""

    file_name: str
    file_size: int
    file_content_type: str
    message: str = "File uploaded successfully"


class ProductDownloadResponse(BaseModel):
    """Ответ с URL для скачивания файла товара."""

    download_url: str
    file_name: str
    expires_in: int = 3600  # seconds


# ═══════════════════════════════════════════════════════════════
# PRODUCT RESPONSES
# ═══════════════════════════════════════════════════════════════

class ProductPublicResponse(BaseModel):
    """Публичный ответ (для каталога)."""
    id: int
    title: str
    description: str
    price: float
    seller_id: int
    seller_username: str | None = None
    main_image_url: str | None = None
    images_count: int = 0
    has_file: bool = False
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(BaseModel):
    """Детальный ответ (страница товара)."""
    id: int
    title: str
    description: str
    price: float
    seller_id: int
    seller_username: str | None = None
    images: list[ProductImageResponse] = []
    file_info: ProductFileInfo
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductPrivateResponse(ProductDetailResponse):
    """Приватный ответ для владельца."""
    downloads_count: int = 0
    total_sales: float = 0.0


# ═══════════════════════════════════════════════════════════════
# LIST RESPONSES
# ═══════════════════════════════════════════════════════════════


class ProductListResponse(BaseModel):
    """Ответ со списком товаров с пагинацией."""

    items: list[ProductPublicResponse]
    total: int
    page: int
    per_page: int
    pages: int
