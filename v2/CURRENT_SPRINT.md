# Спринт 6 — ориентировочное КБЖУ на карточке

Человек (чат 2026-09-06): «приступай к планам и разработке». Контракт: [docs/drafts/NUTRITION.md](docs/drafts/NUTRITION.md). После этапа 0 канон в хозяевах, черновик — «перенесён».

Оверлей 43 не бросать: валидатор и `import_draft` не ломать. Движок калькулятора / ranking не трогать. Корневой V1 не трогать. Волну новых 10 не стартовать. Runtime LLM / runtime USDA нет. `v2/preview/` не референс.

## Цель

На `/recipes/<slug>` — ориентировочное КБЖУ **входного набора до готовки**. Числа с `Ingredient`, расчёт после assemble+scale. Автор не пишет ккал в JSON рецепта.

## Канон (этап 0)

| Тема | Как |
|------|-----|
| Базис | `raw_input` / `nutrition_basis=raw_100g`. Не готовое блюдо |
| API | `nutrition.total`, `per_100g_input`, `per_serving` (или null), `incomplete`, `basis`. Не `per_100g` / `per_100g_raw` |
| Строка | проекция `nutrition_line` только на карточке; клиент после `scaleLine` |
| Exclude | `nutrition_exclude` целиком из числителя и массы. Нет `nutrition_factor` |
| kcal | сумма источника, не Atwater 4/9/4 |
| Порции | `per_serving` только если `servings` задан |
| `energy_profile` | по-прежнему не ккал |

Этап 3 (`yield_weight_g`, фильтр `kcal_max`, коэффициент масла) **не** делать.

## Чек-лист

- Канон: DATA-MODEL, API, DEFAULTS, UX-PROPOSAL §6, RECIPE, TESTING U23–U35, DEC-022, HUMAN 2.15, PLAN.
- Миграция: нутриенты на `Ingredient`, `nutrition_exclude` на строке.
- Сид `ingredient_nutrition.json` → Postgres при import (не runtime FDC).
- `services/nutrition.py` + pytest U23–U35.
- Валидатор: запрет `kcal` на рецепте; жирный `to_taste` — ошибка.
- Карточка: блок после «У меня»; слайдер и чип пересчитывают; `incomplete` заметно.
- Клиент `lib/nutrition.ts` ≡ Django. Каталог и калькулятор КБЖУ не показывают.

## Готово, когда

Эталон на `:8080/recipes/barhatnaya-govyadina-po-kitajski`: total + per_100g_input; порции null если нет servings; «У меня» двигает КБЖУ. Pytest зелёные. Compose жив. V1 на `:3456`. Нет Atwater, нет `kcal_max`, нет выдуманных servings.
