from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_helper import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    seller: Mapped["User"] = relationship(back_populates="products")  # noqa: F821
