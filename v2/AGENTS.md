# AGENTS.md — sol-chef 2.0

Сначала: **[CURRENT_SPRINT.md](CURRENT_SPRINT.md)**. Куда какой документ: [docs/README.md](docs/README.md). В конце сессии обновить [docs/STATUS.md](docs/STATUS.md) — это журнал, не место менять архитектуру.

## Законы

- Код и документы 2.0 — только папка `v2/`. Корень репозитория — монорепо, не статическая главная. V1 — [`archive/v1/`](../archive/v1/), не возвращать в корень как прод. Токены `archive/v1/css/global.css` копировать в V2, не перезаписывать.
- Корневой архивный PLAN — история V1, не запрет React/БД.
- `v2/preview/` не референс и не восстанавливать. Экраны: [docs/UX-PROPOSAL.md](docs/UX-PROPOSAL.md) (**D+**, правки HUMAN §9). В UI **«Калькулятор»**, URL **`/calculator`**.
- JSON архива V1 — ETL в Postgres, не рантайм Next.
- Пустая ячейка [docs/HUMAN.md](docs/HUMAN.md) ≠ «да». Ответ в HUMAN действует после правки канона (VOCAB / UX-PROPOSAL / SAFETY…), не вместо неё. UI по-русски, код по-английски.
- Стек: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Схема: [docs/DATA-MODEL.md](docs/DATA-MODEL.md). HTTP: [docs/API.md](docs/API.md). Числа: [docs/DEFAULTS.md](docs/DEFAULTS.md). Коды: [docs/VOCAB.md](docs/VOCAB.md). Safety: [docs/SAFETY.md](docs/SAFETY.md). Сдача: [docs/TESTING.md](docs/TESTING.md). Выход на ВМ: [docs/CUTOVER.md](docs/CUTOVER.md).

## Не всегда открывать

- [docs/UX.md](docs/UX.md) — закрытый бриф аналитика; открывать только при переигровке IA.
- [docs/RECIPE.md](docs/RECIPE.md) — конвейер волн; массовую генерацию не начинать без явного старта в чате / CURRENT_SPRINT.
- HUMAN §6–§7 — юрист, почта, MinIO.

## Запреты

- Код 2.0 вне `v2/`. Возвращать V1 в корень как прод.
- Runtime LLM, JWT, CORS, публичный Next `app/api`.
- GET magic link логинит. `unknown` аллерген = «нет».
- `gentle` как в V1 JS (`1+(ratio-1)*0.5`). Ранжирование калькулятора на клиенте Next.
- Сессии в Redis. ClamAV на VPS 8 ГБ. Gmail / Госуслуги.
- Волны и оверлеи без явного старта в чате / CURRENT_SPRINT. `editorial_tested` от агента. High-risk без «Осторожно».
- Коммит `.env`, ключей, дампов. Пуш в `main` как прод, пока домен не на V2 (см. CUTOVER). Сборка образов на VPS после появления реестра — только `pull`.
- Regex как основной ETL-аллергенов. `__icontains` для поиска каталога. `scale_mode=fixed` / поле `scalable_rule`.
- `import_v1` на проде вместо дампа — затирает оверлеи и теряет ~135 карточек.

## Git

Пути только под `v2/` (архив V1 — только по явной просьбе). Сообщения по-русски, зачем. Секреты не в git.

## Проверка

Команды — в TESTING и CURRENT_SPRINT. Нет Compose — срез не готов. Архив V1: `python -m http.server 3456` из `archive/v1/`.

## Локальный Next

При запущенном `v2/infra/docker-compose.yml` не запускать на хосте `npm run build` / `next build` из `v2/frontend`: bind-mount делает `.next` общей с `next dev`, из-за чего сервер начинает отдавать 404 на старые чанки. Для быстрой проверки клиента использовать `npx tsc --noEmit`; production-сборку проверять только отдельным Docker-образом через `docker-compose.prod.yml`. Если `.next` уже перезаписана, перезапустить контейнер `frontend`.
