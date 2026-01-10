from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_helper import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(25), nullable=True)
    email: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)

    balance: Mapped[float] = mapped_column(default=0.0)

    is_active: Mapped[bool] = mapped_column(default=True)
    is_seller: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    products: Mapped[list["Product"]] = relationship(back_populates="seller")  # noqa: F821
