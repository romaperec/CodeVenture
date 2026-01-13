from fastapi import HTTPException, status

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product


class ProductService:
    def __init__(self, redis: Redis, db: AsyncSession | None = None) -> None:
        self.redis = redis
        self.db = db

    async def get_all_products(self):
        products = await self.db.execute(select(Product))
        products = products.scalars().all()

        if products is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Products not found"
            )

        return products

    async def get_product_by_id(self, id: int):
        product = await self.db.execute(select(Product).where(Product.id == id))
        product = product.scalar_one_or_none()

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        return product
