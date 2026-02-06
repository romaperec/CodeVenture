# app/modules/products/service.py

import mimetypes
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from loguru import logger
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.db_helper import sessionmaker as async_session_factory
from app.core.minio_client import minio_client
from app.modules.products.models import Product, ProductImage
from app.modules.products.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductDetailResponse,
    ProductDownloadResponse,
    ProductFileInfo,
    ProductFileUploadResponse,
    ProductImageResponse,
    ProductImageUploadResponse,
    ProductPublicResponse,
)


class ProductService:
    def __init__(self, redis: Redis, db: AsyncSession | None = None) -> None:
        self.redis = redis
        self.db = db
        self.minio = minio_client

    # ═══════════════════════════════════════════════════════════════
    # CRUD OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    async def create_product(self, user_id: int, schema: ProductCreate) -> Product:
        """Создает новый товар."""
        new_product = Product(
            title=schema.title,
            description=schema.description,
            price=schema.price,
            user_id=user_id,
        )

        self.db.add(new_product)
        await self.db.commit()
        await self.db.refresh(new_product)

        logger.info(f"Created product {new_product.id} by user {user_id}")
        return new_product

    async def get_product_by_id(self, product_id: int) -> Product | None:
        """Получает товар по ID с изображениями."""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.images))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_product_with_cache(self, product_id: int) -> ProductDetailResponse:
        """Получает товар с кэшированием."""
        cache_key = f"product:{product_id}"

        # Проверка кэша
        cached = await self.redis.get(cache_key)
        if cached:
            return ProductDetailResponse.model_validate_json(cached)

        # Получение из БД
        if self.db:
            product = await self.get_product_by_id(product_id)
        else:
            async with async_session_factory() as temp_db:
                result = await temp_db.execute(
                    select(Product)
                    .options(selectinload(Product.images))
                    .where(Product.id == product_id)
                )
                product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        # Формирование ответа
        response = await self._build_product_detail_response(product)

        # Кэширование
        await self.redis.set(cache_key, response.model_dump_json(), ex=1800)

        return response

    async def _build_product_detail_response(
        self, product: Product
    ) -> ProductDetailResponse:
        """Формирует детальный ответ для товара."""
        images = []
        for img in product.images:
            image_url = await self.minio.generate_public_url(
                settings.MINIO_BUCKET_IMAGES, img.image_key
            )
            images.append(
                ProductImageResponse(
                    id=img.id,
                    image_url=image_url,
                    is_main=img.is_main,
                    position=img.position,
                )
            )

        return ProductDetailResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            price=product.price,
            seller_id=product.user_id,
            images=images,
            file_info=ProductFileInfo(
                file_name=product.file_name,
                file_size=product.file_size,
                file_content_type=product.file_content_type,
                has_file=product.file_key is not None,
            ),
            is_published=product.is_published,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

    async def invalidate_product_cache(self, product_id: int) -> None:
        """Инвалидирует кэш товара."""
        await self.redis.delete(f"product:{product_id}")

    # ═══════════════════════════════════════════════════════════════
    # FILE UPLOAD / DOWNLOAD
    # ═══════════════════════════════════════════════════════════════

    async def upload_product_file(
        self,
        user_id: int,
        product_id: int,
        file: UploadFile,
    ) -> ProductFileUploadResponse:
        """Загружает файл товара."""
        # Проверка владельца
        product = await self._get_product_for_owner(product_id, user_id)

        # Валидация файла
        await self._validate_product_file(file)

        # Чтение файла
        file_data = await file.read()
        file_size = len(file_data)

        # Определение content-type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if not content_type:
            content_type = "application/octet-stream"

        # Удаление старого файла если есть
        if product.file_key:
            await self.minio.delete_file(
                settings.MINIO_BUCKET_PRODUCTS, product.file_key
            )

        # Загрузка нового файла
        file_key = await self.minio.upload_file(
            bucket=settings.MINIO_BUCKET_PRODUCTS,
            file_data=BytesIO(file_data),
            file_size=file_size,
            original_filename=file.filename,
            content_type=content_type,
            folder=f"products/{product_id}",
        )

        # Обновление записи в БД
        product.file_key = file_key
        product.file_name = file.filename
        product.file_size = file_size
        product.file_content_type = content_type

        await self.db.commit()
        await self.invalidate_product_cache(product_id)

        logger.info(f"Uploaded file for product {product_id}: {file.filename}")

        return ProductFileUploadResponse(
            file_name=file.filename,
            file_size=file_size,
            file_content_type=content_type,
        )

    async def _validate_product_file(self, file: UploadFile) -> None:
        """Валидирует файл товара."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required"
            )

        # Проверка расширения
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_PRODUCT_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {settings.ALLOWED_PRODUCT_EXTENSIONS}",
            )

        # Проверка размера (читаем частично)
        file.file.seek(0, 2)  # Переход в конец
        size = file.file.tell()
        file.file.seek(0)  # Возврат в начало

        max_size = settings.MINIO_MAX_FILE_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.MINIO_MAX_FILE_SIZE_MB}MB",
            )

    async def get_download_url(
        self,
        user_id: int,
        product_id: int,
    ) -> ProductDownloadResponse:
        """
        Генерирует URL для скачивания файла.

        TODO: Добавить проверку покупки товара
        """
        product = await self.get_product_by_id(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if not product.file_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product has no file"
            )

        # TODO: Проверка что пользователь купил товар или является владельцем
        # if product.user_id != user_id and not await self._check_purchase(user_id, product_id):
        #     raise HTTPException(status_code=403, detail="Access denied")

        # Генерация presigned URL
        download_url = await self.minio.generate_presigned_url(
            bucket=settings.MINIO_BUCKET_PRODUCTS,
            object_name=product.file_key,
            expires_seconds=3600,
        )

        return ProductDownloadResponse(
            download_url=download_url,
            file_name=product.file_name,
            expires_in=3600,
        )

    async def delete_product_file(
        self,
        user_id: int,
        product_id: int,
    ) -> dict:
        """Удаляет файл товара."""
        product = await self._get_product_for_owner(product_id, user_id)

        if not product.file_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product has no file"
            )

        # Удаление из MinIO
        await self.minio.delete_file(settings.MINIO_BUCKET_PRODUCTS, product.file_key)

        # Обновление БД
        product.file_key = None
        product.file_name = None
        product.file_size = None
        product.file_content_type = None

        await self.db.commit()
        await self.invalidate_product_cache(product_id)

        return {"status": "success", "message": "File deleted"}

    # ═══════════════════════════════════════════════════════════════
    # IMAGE UPLOAD
    # ═══════════════════════════════════════════════════════════════

    async def upload_product_image(
        self,
        user_id: int,
        product_id: int,
        file: UploadFile,
        is_main: bool = False,
    ) -> ProductImageUploadResponse:
        """Загружает изображение товара."""
        product = await self._get_product_for_owner(product_id, user_id)

        # Проверка лимита изображений
        images_count = await self._count_product_images(product_id)
        if images_count >= settings.MAX_IMAGES_PER_PRODUCT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.MAX_IMAGES_PER_PRODUCT} images allowed",
            )

        # Валидация изображения
        await self._validate_image_file(file)

        # Чтение файла
        file_data = await file.read()
        file_size = len(file_data)

        # Content-type
        content_type = file.content_type or "image/jpeg"

        # Загрузка в MinIO
        image_key = await self.minio.upload_file(
            bucket=settings.MINIO_BUCKET_IMAGES,
            file_data=BytesIO(file_data),
            file_size=file_size,
            original_filename=file.filename,
            content_type=content_type,
            folder=f"products/{product_id}",
        )

        # Если это главное изображение - убираем флаг у остальных
        if is_main:
            await self._unset_main_image(product_id)

        # Позиция для нового изображения
        position = images_count

        # Создание записи
        new_image = ProductImage(
            product_id=product_id,
            image_key=image_key,
            original_name=file.filename,
            content_type=content_type,
            size=file_size,
            is_main=is_main,
            position=position,
        )

        self.db.add(new_image)
        await self.db.commit()
        await self.db.refresh(new_image)

        await self.invalidate_product_cache(product_id)

        # Генерация URL
        image_url = await self.minio.generate_public_url(
            settings.MINIO_BUCKET_IMAGES, image_key
        )

        logger.info(f"Uploaded image for product {product_id}: {file.filename}")

        return ProductImageUploadResponse(
            id=new_image.id,
            image_url=image_url,
            original_name=file.filename,
            size=file_size,
            is_main=is_main,
            position=position,
        )

    async def upload_product_images(
        self,
        user_id: int,
        product_id: int,
        files: list[UploadFile],
        main_index: int | None = None,
    ) -> list[ProductImageUploadResponse]:
        """Загружает несколько изображений."""
        results = []
        for i, file in enumerate(files):
            is_main = main_index == i
            result = await self.upload_product_image(
                user_id=user_id,
                product_id=product_id,
                file=file,
                is_main=is_main,
            )
            results.append(result)
        return results

    async def _validate_image_file(self, file: UploadFile) -> None:
        """Валидирует файл изображения."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required"
            )

        # Проверка расширения
        ext = Path(file.filename).suffix.lower()
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image type not allowed. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}",
            )

        # Проверка MIME-type
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File is not an image"
            )

        # Проверка размера
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        max_size = settings.MINIO_MAX_IMAGE_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image too large. Max size: {settings.MINIO_MAX_IMAGE_SIZE_MB}MB",
            )

    async def delete_product_image(
        self,
        user_id: int,
        product_id: int,
        image_id: int,
    ) -> dict:
        """Удаляет изображение товара."""
        await self._get_product_for_owner(product_id, user_id)

        result = await self.db.execute(
            select(ProductImage)
            .where(ProductImage.id == image_id)
            .where(ProductImage.product_id == product_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
            )

        # Удаление из MinIO
        await self.minio.delete_file(settings.MINIO_BUCKET_IMAGES, image.image_key)

        # Удаление из БД
        await self.db.delete(image)
        await self.db.commit()

        await self.invalidate_product_cache(product_id)

        return {"status": "success", "message": "Image deleted"}

    async def set_main_image(
        self,
        user_id: int,
        product_id: int,
        image_id: int,
    ) -> dict:
        """Устанавливает главное изображение."""
        await self._get_product_for_owner(product_id, user_id)

        result = await self.db.execute(
            select(ProductImage)
            .where(ProductImage.id == image_id)
            .where(ProductImage.product_id == product_id)
        )
        image = result.scalar_one_or_none()

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
            )

        # Убираем флаг у остальных
        await self._unset_main_image(product_id)

        # Устанавливаем для выбранного
        image.is_main = True
        await self.db.commit()

        await self.invalidate_product_cache(product_id)

        return {"status": "success", "message": "Main image set"}

    async def reorder_images(
        self,
        user_id: int,
        product_id: int,
        image_ids: list[int],
    ) -> dict:
        """Изменяет порядок изображений."""
        await self._get_product_for_owner(product_id, user_id)

        for position, image_id in enumerate(image_ids):
            await self.db.execute(
                ProductImage.__table__.update()
                .where(ProductImage.id == image_id)
                .where(ProductImage.product_id == product_id)
                .values(position=position)
            )

        await self.db.commit()
        await self.invalidate_product_cache(product_id)

        return {"status": "success", "message": "Images reordered"}

    # ═══════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════

    async def _get_product_for_owner(self, product_id: int, user_id: int) -> Product:
        """Получает товар и проверяет владельца."""
        product = await self.get_product_by_id(product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        if product.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this product",
            )

        return product

    async def _count_product_images(self, product_id: int) -> int:
        """Подсчитывает количество изображений товара."""
        result = await self.db.execute(
            select(func.count(ProductImage.id)).where(
                ProductImage.product_id == product_id
            )
        )
        return result.scalar_one()

    async def _unset_main_image(self, product_id: int) -> None:
        """Убирает флаг главного изображения у всех изображений товара."""
        await self.db.execute(
            ProductImage.__table__.update()
            .where(ProductImage.product_id == product_id)
            .values(is_main=False)
        )
