# Документы 2.0

Не грузить всё сразу. Задача сессии — [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md). Индекс не дублирует содержимое файлов.

Каждый факт — **один** хозяин. Остальные только ссылаются. При конфликте:

1. [HUMAN.md](HUMAN.md) — решение человека (после правки канона, не вместо неё)
2. [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md) — что делать сейчас
3. [../AGENTS.md](../AGENTS.md) — что запрещено всегда
4. Канон предметки: [ARCHITECTURE.md](ARCHITECTURE.md), [DATA-MODEL.md](DATA-MODEL.md), [API.md](API.md), [UX-PROPOSAL.md](UX-PROPOSAL.md), [VOCAB.md](VOCAB.md), [SAFETY.md](SAFETY.md)
5. [DEFAULTS.md](DEFAULTS.md) — версии и числа
6. [PLAN.md](PLAN.md) — дорожная карта, не команда сессии
7. [STATUS.md](STATUS.md) — факт сессии, **не** источник решений
8. [RECIPE.md](RECIPE.md) / [UX.md](UX.md) — волны и бриф аналитика (не код спринта)

## Что открыть

| Нужно | Файлы |
|-------|--------|
| Новая задача / срез | CURRENT_SPRINT → AGENTS |
| Внешнему аналитику / одностраничник продукта | [PRODUCT.md](PRODUCT.md) — сценарии, экраны, полный пример рецепта; не канон при конфликте с UX-PROPOSAL |
| Backend, модели, ETL | ARCHITECTURE → DATA-MODEL → API → SAFETY → VOCAB → TESTING |
| UI / маршруты | UX-PROPOSAL (не `v2/preview/`, не UX.md) → `css/global.css` |
| Визуал / полировка UI | бриф дизайнеру: [drafts/DESIGN-BRIEF.md](drafts/DESIGN-BRIEF.md); канон экранов не менять |
| Аккаунты / избранное / «готовил» | план: [ACCOUNTS.md](ACCOUNTS.md); экраны UX-PROPOSAL §13; архив черновика [drafts/ACCOUNTS.md](drafts/ACCOUNTS.md) |
| Калькулятор (как считает) | [CALCULATOR.md](CALCULATOR.md) — разбор экрана; контракт [API.md](API.md) |
| Калькулятор как сборка (архив) | [drafts/COOKING-SOLUTION.md](drafts/COOKING-SOLUTION.md) — перенесён в CALCULATOR / DEC-017 |
| Семейство / посуда (архив) | [drafts/FAMILY-AND-EQUIPMENT.md](drafts/FAMILY-AND-EQUIPMENT.md) — перенесён в VOCAB / DATA-MODEL / DEC-012…015 |
| КБЖУ | канон: [DATA-MODEL.md](DATA-MODEL.md), [API.md](API.md), [DECISIONS.md](DECISIONS.md) DEC-022; архив спеки [drafts/NUTRITION.md](drafts/NUTRITION.md) |
| Заготовки на неделю (идея, не канон) | продукт: [drafts/WEEKLY-PREP.md](drafts/WEEKLY-PREP.md); карта сущностей: [drafts/WEEKLY-PREP-MAP.md](drafts/WEEKLY-PREP-MAP.md); ТЗ анализа: [drafts/WEEKLY-PREP-TZ.md](drafts/WEEKLY-PREP-TZ.md) |
| Коды и маппинг V1 | VOCAB |
| Почему так | [DECISIONS.md](DECISIONS.md) |
| Что уже сделано | STATUS |
| Выход на VPS / cutover | [CUTOVER.md](CUTOVER.md) — операционный чеклист; стек не меняет |
| Контент-волна / оверлей 43 | [RECIPE.md](RECIPE.md) + [RECIPE-INVENTORY.md](RECIPE-INVENTORY.md); пакеты волн — [drafts/packets/](drafts/packets/README.md); оси посуды на существующих — [drafts/packets/OVERLAY-AXES.md](drafts/packets/OVERLAY-AXES.md); бриф JSON автора — [drafts/RECIPE-V2-UPGRADE.md](drafts/RECIPE-V2-UPGRADE.md); оверлей — CURRENT_SPRINT |
| Переигровка IA | UX.md — только UX-аналитик |

## Хозяева

| Файл | Владеет |
|------|---------|
| [../CURRENT_SPRINT.md](../CURRENT_SPRINT.md) | чек-лист этой сессии |
| [../AGENTS.md](../AGENTS.md) | запреты, git, приоритет документов |
| [ARCHITECTURE.md](ARCHITECTURE.md) | стек, Compose, Caddy, BFF, env SSR |
| [DATA-MODEL.md](DATA-MODEL.md) | поля, null, инварианты, FTS, ETL-модель |
| [API.md](API.md) | URL, JSON, фильтры, масштаб query |
| [TESTING.md](TESTING.md) | unit / e2e / acceptance |
| [DEFAULTS.md](DEFAULTS.md) | версии пакетов, `gentle`, веса, снимок «43/19» |
| [UX-PROPOSAL.md](UX-PROPOSAL.md) | экраны D+, жесты, empty-state |
| [PRODUCT.md](PRODUCT.md) | снимок для людей: как сайт работает пользователю; не источник решений |
| [CALCULATOR.md](CALCULATOR.md) | логика подбора `/calculator` (разбор, не контракт) |
| [ACCOUNTS.md](ACCOUNTS.md) | план V2.1 A/B/C: вход, память, голос |
| [VOCAB.md](VOCAB.md) | коды и маппинг V1 |
| [SAFETY.md](SAFETY.md) | температуры, аллергены, high-risk |
| [DECISIONS.md](DECISIONS.md) | ADR |
| [PLAN.md](PLAN.md) | этапы V2.0–cutover |
| [CUTOVER.md](CUTOVER.md) | чеклист деплоя и DNS; не канон стека |
| [HUMAN.md](HUMAN.md) | ответы человека |
| [STATUS.md](STATUS.md) | журнал агента |
| [UX.md](UX.md) | бриф аналитика; **не** код |
| [RECIPE.md](RECIPE.md) | конвейер волн |
| [RECIPE-INVENTORY.md](RECIPE-INVENTORY.md) | 43 утверждённых + черновик сотни |

`v2/preview/` и корневой `PLAN.md` — не про 2.0.
