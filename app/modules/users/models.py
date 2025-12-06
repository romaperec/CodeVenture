from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_helper import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(25))
    email: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(Text)
