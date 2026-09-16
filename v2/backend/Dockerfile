FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl tzdata libpq5 \
    && ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime \
    && echo Europe/Moscow > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

# Compose overrides CMD: migrate + runserver. curl is for healthcheck.
# Venv lives in /opt/venv so a bind-mount of /app does not hide it.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
