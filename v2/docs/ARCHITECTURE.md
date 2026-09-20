# Архитектура 2.0

Стек и маршруты. Числа — [DEFAULTS.md](DEFAULTS.md). Схема — [DATA-MODEL.md](DATA-MODEL.md). HTTP — [API.md](API.md). Задача сессии — [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md). Продукт — [PLAN.md](PLAN.md). ADR — [DECISIONS.md](DECISIONS.md).

## Сервисы

| Сервис | Образ / стек | Сеть Compose | На хост |
|--------|--------------|--------------|---------|
| caddy | Caddy | срез: 80→**8080**; прод: **80 и 443** | срез: http://localhost:8080; прод: https://sol-chef.ru |
| frontend | Next.js 15, Node 22 | 3000 | не публиковать в проде |
| backend | Django 5.2, Python 3.12, uv | 8000 | не публиковать в проде |
| postgres | 16 | 5432 | только Docker-сеть |
| redis | 7, **AOF on** | 6379 | только Docker-сеть |

Сессии — в Postgres, не в Redis. Redis — брокер очередей (в срезе worker не обязателен).

Локально в compose: Django **runserver**, Next **`next dev`**. Прод: gunicorn (2 воркера) + WhiteNoise; Next `output: 'standalone'`. Не путать. Чеклист ВМ и DNS: [CUTOVER.md](CUTOVER.md).

### Срез vs позже

В **гостевом срезе** в compose: caddy, frontend, backend, postgres, redis.

**V2.1-A:** + Mailpit (SMTP для Django, UI писем на loopback). Письмо в запросе, без Celery.

Не в V2.1: Celery worker, MinIO, ClamAV. Фото — V2.2. Сборка образов на VPS запрещена (CI `pull`). Postbox — прод, не локальный compose.

## Caddy (BFF, один origin)

```
Срез:  браузер → Caddy :8080
Прод:  браузер → Caddy :443 (Let's Encrypt)
  /api /admin /static /healthz  → backend:8000
  /_internal/*                  → 404 снаружи
  всё остальное                 → frontend:3000
```

`POST /_internal/revalidate` на Next — только из Docker-сети (Django, HMAC). Браузер туда не ходит.

- Без JWT и CORS. Браузер вызывает `/api/` того же хоста.
- Next SSR: `INTERNAL_API_URL=http://backend:8000`, клиент: `NEXT_PUBLIC_API_URL` пустой. Публичные GET без `cookies()` — иначе страница не кэшируется. Cookie и CSRF — когда появятся сессии и мутации. Не `fetch` на `localhost:8080` из контейнера.
- ISR — только публичное тело. Персональные блоки и счётчики «приготовили N» / комментарии — клиентский `/api/` после гидрации ([ACCOUNTS.md](ACCOUNTS.md)). `community_confirmed` на `Recipe` можно в SSR.
- Статика Django (админка): WhiteNoise у backend, чтобы `/static/` через Caddy работал и с gunicorn. В срезе достаточно runserver + WhiteNoise в deps.
- `/admin/` на VPS закрывать авторизацией **до** cutover: Caddy basic auth + Django login. См. [CUTOVER.md](CUTOVER.md).

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

Источник: `archive/v1/data/`, не рантайм Next. Идемпотентный upsert, одна транзакция, сиды аллергенов и температур — DATA-MODEL. Команда: `import_v1`, флаг `--dry-run`. На проде каталог переносят дампом Postgres, не повторным `import_v1` (оверлеи 43 и новые карточки иначе потеряются). Число рецептов V1 в JSON — DEFAULTS; живой каталог V2 — в БД.

## Запреты инфра

Runtime LLM. JWT. CORS. `next build` на хосте VPS (сборка только в образе). ClamAV на 8 ГБ. Сессии в Redis. Публичный Next `/api/`. Код 2.0 вне `v2/`.
