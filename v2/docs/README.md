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
| Backend, модели, ETL | ARCHITECTURE → DATA-MODEL → API → SAFETY → VOCAB → TESTING |
| UI / маршруты | UX-PROPOSAL (не `v2/preview/`, не UX.md) → `css/global.css` |
| Калькулятор (как считает) | [CALCULATOR.md](CALCULATOR.md) — разбор экрана; контракт [API.md](API.md) |
| Калькулятор как сборка (архив) | [drafts/COOKING-SOLUTION.md](drafts/COOKING-SOLUTION.md) — перенесён в CALCULATOR / DEC-017 |
| КБЖУ (черновик, не канон) | [drafts/NUTRITION.md](drafts/NUTRITION.md) — не кодить, пока HUMAN не принял; БЖУ в DEFAULTS вне скоупа |
| Коды и маппинг V1 | VOCAB |
| Почему так | [DECISIONS.md](DECISIONS.md) |
| Что уже сделано | STATUS |
| Контент-волна / оверлей 43 | [RECIPE.md](RECIPE.md) + [RECIPE-INVENTORY.md](RECIPE-INVENTORY.md); пакеты волн — [drafts/packets/](drafts/packets/README.md); оверлей — CURRENT_SPRINT |
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
| [CALCULATOR.md](CALCULATOR.md) | логика подбора `/calculator` (разбор, не контракт) |
| [VOCAB.md](VOCAB.md) | коды и маппинг V1 |
| [SAFETY.md](SAFETY.md) | температуры, аллергены, high-risk |
| [DECISIONS.md](DECISIONS.md) | ADR |
| [PLAN.md](PLAN.md) | этапы V2.0–cutover |
| [HUMAN.md](HUMAN.md) | ответы человека |
| [STATUS.md](STATUS.md) | журнал агента |
| [UX.md](UX.md) | бриф аналитика; **не** код |
| [RECIPE.md](RECIPE.md) | конвейер волн |
| [RECIPE-INVENTORY.md](RECIPE-INVENTORY.md) | 43 утверждённых + черновик сотни |

`v2/preview/` и корневой `PLAN.md` — не про 2.0.
