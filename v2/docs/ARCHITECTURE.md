# Архитектура 2.0

Стек и маршруты. Числа — [DEFAULTS.md](DEFAULTS.md). Схема — [DATA-MODEL.md](DATA-MODEL.md). HTTP — [API.md](API.md). Задача сессии — [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md). Продукт — [PLAN.md](PLAN.md). ADR — [DECISIONS.md](DECISIONS.md).

## Сервисы

| Сервис | Образ / стек | Сеть Compose | На хост |
|--------|--------------|--------------|---------|
| caddy | Caddy | 80 | **8080** → http://localhost:8080 |
| frontend | Next.js 15, Node 22 | 3000 | не публиковать в проде |
| backend | Django 5.2, Python 3.12, uv | 8000 | не публиковать в проде |
| postgres | 16 | 5432 | только Docker-сеть |
| redis | 7, **AOF on** | 6379 | только Docker-сеть |

Сессии — в Postgres, не в Redis. Redis — брокер очередей (в срезе worker не обязателен).

Локально в compose: Django **runserver**, Next **`next dev`**. Прод: gunicorn (2 воркера) + WhiteNoise; Next `output: 'standalone'`. Не путать.

### Срез vs позже

В **спринте 1** в compose: caddy, frontend, backend, postgres, redis.

Не в срезе: Celery worker, MinIO, Mailpit, ClamAV. Письма и фото — V2.1. Сборка образов на VPS запрещена (CI `pull`).

## Caddy (BFF, один origin)

```
Браузер → Caddy :8080
  /api /admin /static /healthz  → backend:8000
  /_internal/*                  → 404 снаружи
  всё остальное                 → frontend:3000
```

`POST /_internal/revalidate` на Next — только из Docker-сети (Django, HMAC). Браузер туда не ходит.

- Без JWT и CORS. Браузер вызывает `/api/` того же хоста.
- Next SSR: `INTERNAL_API_URL=http://backend:8000`, клиент: `NEXT_PUBLIC_API_URL` пустой. Пробрасывать `Cookie` (и CSRF, когда появятся мутации). Не `fetch` на `localhost:8080` из контейнера.
- ISR — только публичное тело. Персональные блоки (когда появятся) — клиентский `/api/` после гидрации.
- Статика Django (админка): WhiteNoise у backend, чтобы `/static/` через Caddy работал и с gunicorn. В срезе достаточно runserver + WhiteNoise в deps.
- `/admin/` на VPS закрывать авторизацией **до** cutover (не срез, не забыть в деплое).

301 `recipe.html?id=` — страница Next, не `redirects()` по pathname. См. API/UX-PROPOSAL.

## Кто чем владеет

| | Django | Next |
|--|--------|------|
| Данные, сессия, CSRF | да | нет |
| Масштаб «У меня» / порции | domain service; `gentle` = `ratio^0.7` | порт той же формулы на карточке, мгновенно |
| Ранжирование калькулятора | тот же бэкенд, веса DEFAULTS | фильтры в URL, карточки из API |
| HTML, SEO, Schema.org Recipe | нет | SSR |
| Публичный REST в `app/api` | — | **запрещён** (`/api/` = Django) |

Next на карточке рецепта повторяет формулу Django (`lib/scale.ts`), не формулу V1. Золотые тесты — pytest. Ранжирование калькулятора на клиенте нет.

Query масштаба — [API.md](API.md). Нет ни servings, ни якоря — масштаб выключен, ETL не выдумывает порции.

## Данные

Контракт полей — [DATA-MODEL.md](DATA-MODEL.md). Кратко: живые поля на `Recipe`; ревизии для истории; якорь `is_anchor`; справочники — пять `ContentDocument`; FTS = `normalize_ru` + `to_tsvector('russian')` + `pg_trgm` (не `__icontains`; `unaccent` не делает `ё`→`е`).

## ETL

Источник: корневой `data/`, не рантайм Next. Идемпотентный upsert, одна транзакция, сиды аллергенов и температур — DATA-MODEL. Команда: `import_v1`, флаг `--dry-run`. Число рецептов — DEFAULTS.

## Запреты инфра

Runtime LLM. JWT. CORS. `next build` на VPS. ClamAV на 8 ГБ. Сессии в Redis. Публичный Next `/api/`. Код 2.0 вне `v2/`.
