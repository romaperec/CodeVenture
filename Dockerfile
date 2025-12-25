FROM python:3.13

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock ./

RUN if [ ! -d ".venv" ]; then \
        uv sync --frozen --no-install-project; \
    else \
        echo ".venv already exists, skipping initial sync"; \
    fi

COPY . .

RUN if [ ! -d ".venv" ]; then \
        uv sync --frozen; \
    else \
        echo ".venv exists, skipping full sync"; \
    fi

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
