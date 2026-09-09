# backend — Django 5.2

DRF + `drf-spectacular`. Владеет данными, сессией, CSRF, масштабом и калькулятором. Сессии в Postgres.

Пакетный менеджер: **uv** (`pyproject.toml` + `uv.lock`).

## Запуск

```bash
cd v2/backend
uv sync --group dev
# Postgres из compose: POSTGRES_HOST=postgres (дефолт)
# Локально без Docker:
#   set POSTGRES_HOST=localhost
#   set V1_DATA_ROOT=K:\Work\sol-chef
uv run python manage.py migrate
uv run python manage.py import_v1 --dry-run
uv run python manage.py import_v1
uv run python manage.py runserver 0.0.0.0:8000
```

Админка: `/admin/` (создать пользователя вручную: `createsuperuser`). Статика — WhiteNoise.

OpenAPI: `/api/schema/`. Health: `/healthz`.

## Тесты

```bash
cd v2/backend
set V1_DATA_ROOT=K:\Work\sol-chef
uv run pytest
```

U1–U9 и разбор V1 (43 рецепта) не требуют Postgres. FTS/API — после `migrate` на Postgres 16.

## `import_v1`

Читает `{V1_DATA_ROOT}/data/recipes/index.json` (19 файлов, 43 объекта). Сиды:

- `apps/recipes/fixtures/v1_ingredient_map.json` — точная строка V1 `name` → `canonical_id` + аллергены
- `apps/recipes/fixtures/v1_step_temperatures.json` — 13 рецептов птица/свинина/рыба

`--dry-run` печатает отчёт, БД не трогает. Повторный запуск — upsert, count остаётся 43.

## Отклонения от DATA-MODEL

- `notes` на `Recipe` — JSONField (список объектов), не строка.
- Вариации — таблица `RecipeVariant` (дельты), не JSONField на `Recipe`. В ответе API поле `variations` собирается из вариантов.
- `ingredient_titles` — денормализация для generated `search_vector` (title + имена + summary).
- Единица V1 «стакана» нормализуется в `ml` (×250 мл), в enum нет `cup`.
- Счётные единицы вне VOCAB (`банка`, `стебля`, `стручков`, `порции`, `листиков`, `полоски`) → `pcs`.
- Query «без аллергена» для рекомендаций: `without` (CSV кодов VOCAB), запасной ключ `exclude_allergen`.
