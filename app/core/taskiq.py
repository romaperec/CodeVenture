# app/core/taskiq.py
"""Конфигурация асинхронного брокера задач Taskiq."""

import taskiq_fastapi
from taskiq_redis import ListQueueBroker

from app.core.config import settings

# Создание брокера задач на основе Redis
broker = ListQueueBroker(url=settings.REDIS_URL_QUEUE)

# Инициализация интеграции с FastAPI
taskiq_fastapi.init(broker, "app.main:app")
