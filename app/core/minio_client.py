import asyncio
from datetime import timedelta
from io import BytesIO

from loguru import logger
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


class MinIOClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET_PRODUCTS
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise

    async def upload_file(
        self,
        object_name: str,
        file_data: BytesIO,
        file_size: int,
        content_type: str = "application/octet-stream",
    ) -> str:
        try:
            await asyncio.to_thread(
                self.client.put_object,
                bucket_name=self.bucket,
                data=file_data,
                length=file_size,
                content_type=content_type,
            )
            logger.info(f"Uploaded file: {object_name}")
            return object_name
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise

    async def delete_file(self, object_name: str):
        try:
            await asyncio.to_thread(self.client.remove_object, self.bucket, object_name)
            logger.info(f"Deleted file: {object_name}")
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise

    async def generate_presigned_url(self, object_name: str, expires: int = 300) -> str:
        try:
            url = await asyncio.to_thread(
                self.client.presigned_get_object,
                bucket_name=self.bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            logger.error(f"URL generation error {e}")
            raise

    async def get_file_info(self, object_name) -> str:
        try:
            stat = await asyncio.to_thread(
                self.client.stat_object, self.bucket, object_name
            )
            return {
                "size": stat.size,
                "last_modified": stat.last_modified,
                "content_type": stat.content_type,
            }
        except S3Error as e:
            logger.error(f"File info error {e}")
            raise


minio_client = MinIOClient()
