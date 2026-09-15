# infra

Срез (локально): postgres 16, redis 7 (AOF), Django `runserver`, Next `next dev`, Caddy. На хост публикуется только **8080** (Caddy). Postgres и Redis — только Docker-сеть.

Прод (ВМ): [docker-compose.prod.yml](docker-compose.prod.yml) — gunicorn, Next `standalone`, Caddy **80/443**. Чеклист DNS и Timeweb: [../docs/CUTOVER.md](../docs/CUTOVER.md).

В срезе нет MinIO, Mailpit, Celery worker, ClamAV.

Образы на VPS после появления реестра не собирать — только CI `pull`. Первый cutover собирает на ВМ (HUMAN 7.7 «позже»). RAM ориентир: 8 ГБ + swap 4, Timeweb, РФ. Подробно: [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## Запуск среза

Из **корня репозитория** (нужен Docker Desktop):

```bash
cp v2/infra/.env.example v2/infra/.env
docker compose -f v2/infra/docker-compose.yml up --build
```

`.env` не коммитить. `DJANGO_SECRET_KEY` в примере — локальная заглушка, не прод-секрет.

Сайт за Caddy: http://localhost:8080. Backend (`pyproject.toml`) и frontend (`package.json`) уже в срезе.

Остановка с данными БД: `docker compose -f v2/infra/docker-compose.yml down`. Сброс томов (расширения Postgres живут в томе): `down -v`.

## Что внутри (срез)

| Сервис | Порт в сети | На хост |
|--------|-------------|---------|
| caddy | 80 | **8080** |
| frontend | 3000 | нет |
| backend | 8000 | нет |
| postgres | 5432 | нет |
| redis | 6379 | нет |

- Backend: `uv sync` → `migrate` → идемпотентный `import_v1` → `runserver 0.0.0.0:8000`. Код: bind-mount `v2/backend`. Каталог V1: корень репозитория **read-only** в `/v1-src`; ETL сам находит `archive/v1` (`V1_DATA_ROOT=/v1-src`).
- Frontend: `npm install && npm run dev -- -H 0.0.0.0 -p 3000`. `INTERNAL_API_URL=http://backend:8000`, `NEXT_PUBLIC_API_URL` пустой.
- Caddy: `/api` `/admin` `/static` `/healthz` → backend; `/_internal/*` снаружи 404; остальное (включая `/_next/webpack-hmr`) → frontend.
- TZ: `Europe/Moscow`.

Прод не вызывает `import_v1` при старте: каталог — дамп Postgres, см. CUTOVER.
