# AGENTS.md — sol-chef 2.0

Сначала: **[CURRENT_SPRINT.md](CURRENT_SPRINT.md)**. Куда какой документ: [docs/README.md](docs/README.md). В конце сессии обновить [docs/STATUS.md](docs/STATUS.md) — это журнал, не место менять архитектуру.

## Законы

- Код и документы 2.0 — только папка `v2/`. Корень репозитория — рабочий V1: не менять `index.html`, `recipe.html`, `js/`, `data/`, `css/` (токены `css/global.css` копировать). Не удалять V1 до cutover.
- Корневой `PLAN.md` — архив V1, не запрет React/БД.
- `v2/preview/` не референс и не восстанавливать. Экраны: [docs/UX-PROPOSAL.md](docs/UX-PROPOSAL.md) (**D+**, правки HUMAN §9). В UI **«Калькулятор»**, URL **`/calculator`**.
- JSON корня — ETL в Postgres, не рантайм Next.
- Пустая ячейка [docs/HUMAN.md](docs/HUMAN.md) ≠ «да». Ответ в HUMAN действует после правки канона (VOCAB / UX-PROPOSAL / SAFETY…), не вместо неё. UI по-русски, код по-английски.
- Стек: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Схема: [docs/DATA-MODEL.md](docs/DATA-MODEL.md). HTTP: [docs/API.md](docs/API.md). Числа: [docs/DEFAULTS.md](docs/DEFAULTS.md). Коды: [docs/VOCAB.md](docs/VOCAB.md). Safety: [docs/SAFETY.md](docs/SAFETY.md). Сдача: [docs/TESTING.md](docs/TESTING.md).

## Не всегда открывать

- [docs/UX.md](docs/UX.md) — закрытый бриф аналитика; открывать только при переигровке IA.
- [docs/RECIPE.md](docs/RECIPE.md) — конвейер волн; массовую генерацию не начинать без явного старта в чате / CURRENT_SPRINT.
- HUMAN §6–§7 — юрист, почта, MinIO.

## Запреты

- Код 2.0 вне `v2/`. Ломать текущий сайт.
- Runtime LLM, JWT, CORS, сборка образов на VPS, публичный Next `app/api`.
- GET magic link логинит. `unknown` аллерген = «нет».
- `gentle` как в V1 JS (`1+(ratio-1)*0.5`). Ранжирование калькулятора на клиенте Next.
- Сессии в Redis. ClamAV на VPS 8 ГБ. Gmail / Госуслуги.
- Волны и оверлеи без явного старта в чате / CURRENT_SPRINT. `editorial_tested` от агента. High-risk без «Осторожно».
- Коммит `.env`, ключей, дампов. Пуш в `main` как прод. Деплой production.
- Regex как основной ETL-аллергенов. `__icontains` для поиска каталога. `scale_mode=fixed` / поле `scalable_rule`.

## Git

Пути только под `v2/`. Сообщения по-русски, зачем. Секреты не в git.

## Проверка

Команды — в TESTING и CURRENT_SPRINT. Нет Compose — срез не готов. V1 после правок 2.0 должен открываться из корня (`python -m http.server 3456`).
