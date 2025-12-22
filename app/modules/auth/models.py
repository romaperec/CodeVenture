from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_helper import Base


class RefreshToken(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
