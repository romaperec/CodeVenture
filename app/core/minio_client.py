# app/core/minio_client.py
"""Клиент для работы с MinIO хранилищем файлов."""

import asyncio
from datetime import timedelta
from io import BytesIO
from pathlib import Path
import uuid

from loguru import logger
from minio import Minio
from minio.error import S3Error


from app.core.config import settings


class MinIOClient:
    """Клиент для управления файлами в MinIO."""

    def __init__(self):
        """Инициализирует клиент MinIO и создает необходимые buckets."""
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Проверяет и создает необходимые buckets если они не существуют."""
        buckets = [settings.MINIO_BUCKET_PRODUCTS, settings.MINIO_BUCKET_IMAGES]
        try:
            for bucket in buckets:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise

    async def upload_file(
        self,
        bucket: str,
        file_data: BytesIO,
        file_size: int,
        original_filename: str,
        content_type: str = "application/octet-stream",
        folder: str | None = None,
    ) -> str:
        """Загружает файл в MinIO хранилище и возвращает имя объекта."""
        ext = Path(original_filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"

        if folder:
            object_name = f"{folder}/{unique_name}"
        else:
            object_name = unique_name

        try:
            await asyncio.to_thread(
                self.client.put_object,
                bucket_name=bucket,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
            )
            logger.info(f"Uploaded file: {object_name} to bucket: {bucket}")
            return object_name
        except S3Error as e:
            logger.error(f"MinIO upload error: {e}")
            raise

    async def delete_file(self, bucket: str, object_name: str):
        """Удаляет файл из MinIO хранилища."""
        try:
            await asyncio.to_thread(self.client.remove_object, bucket, object_name)
            logger.info(f"Deleted file: {object_name} from bucket {bucket}")
            return True
        except S3Error as e:
            logger.error(f"MinIO delete error: {e}")
            raise

    async def delete_files(self, bucket: str, object_names: list[str]) -> None:
        """Удаляет несколько файлов из MinIO хранилища."""
        from minio.deleteobjects import DeleteObject

        try:
            delete_objects = [DeleteObject(name) for name in object_names]
            errors = await asyncio.to_thread(
                lambda: list(self.client.remove_object(bucket, delete_objects))
            )
            for error in errors:
                logger.error(f"Error deleting {error.name}: {error.message}")
        except S3Error as e:
            logger.error(f"MinIO bulk delete error: {e}")

    async def generate_presigned_url(
        self, bucket: str, object_name: str, expires_seconds: int = 3600
    ) -> str:
        """Генерирует временную ссылку для скачивания файла."""
        try:
            url = await asyncio.to_thread(
                self.client.presigned_get_object,
                bucket_name=bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            return url
        except S3Error as e:
            logger.error(f"URL generation error {e}")
            raise

    async def generate_public_url(self, bucket: str, object_name: str) -> str:
        """Генерирует публичную ссылку на файл."""
        if settings.MINIO_SECURE:
            protocol = "https"
        else:
            protocol = "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"

    async def get_file_info(self, bucket: str, object_name: str) -> dict | None:
        """Получает информацию о файле (размер, тип, дату изменения)."""
        try:
            stat = await asyncio.to_thread(self.client.stat_object, bucket, object_name)
            return {
                "size": stat.size,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
                "etag": stat.etag,
            }
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            logger.error(f"File info error {e}")
            raise

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """Проверяет существует ли файл в MinIO хранилище."""
        info = await self.get_file_info(bucket, object_name)
        return info is not None

    async def set_bucket_public_read(self, bucket: str) -> None:
        """Устанавливает публичный доступ на чтение для бакета."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }

        import json

        try:
            await asyncio.to_thread(
                self.client.set_bucket_policy, bucket, json.dumps(policy)
            )
            logger.info(f"Set public read policy for bucket: {bucket}")
        except S3Error as e:
            logger.error(f"Failed to set bucket policy: {e}")


minio_client = MinIOClient()
