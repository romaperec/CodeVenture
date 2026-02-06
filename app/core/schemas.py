# app/core/schemas.py
"""Схемы для core модуля."""

from pydantic import BaseModel


class TokenData(BaseModel):
    """Данные, содержащиеся в JWT токене."""

    id: int
