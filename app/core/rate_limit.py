# app/core/rate_limit.py
"""Конфигурация ограничения частоты запросов (rate limiting)."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Обработчик ошибки превышения лимита запросов."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests. Please try again later."},
    )
