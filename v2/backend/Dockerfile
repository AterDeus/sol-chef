FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tzdata libpq5 \
    && ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo Europe/Moscow > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

# Compose overrides CMD: migrate + import_v1 + runserver. curl is for healthcheck.
CMD ["sh", "-c", "uv sync && exec uv run python manage.py runserver 0.0.0.0:8000"]
