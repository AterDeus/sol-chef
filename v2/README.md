# sol-chef 2.0

Основное приложение. Статический V1 — [`archive/v1/`](../archive/v1/), не корень репо.

| | Команда | URL |
|--|---------|-----|
| V2 срез | `docker compose -f v2/infra/docker-compose.yml up --build` | http://localhost:8080 |
| Архив V1 | из `archive/v1/`: `python -m http.server 3456` | http://localhost:3456 |
| Прод / домен | [docs/CUTOVER.md](docs/CUTOVER.md) | https://sol-chef.ru |

Задача сессии: [CURRENT_SPRINT.md](CURRENT_SPRINT.md). Агент: [AGENTS.md](AGENTS.md). Экраны: [docs/UX-PROPOSAL.md](docs/UX-PROPOSAL.md). Как сайт выглядит человеку (для внешнего аналитика): [docs/PRODUCT.md](docs/PRODUCT.md). Куда какой файл: [docs/README.md](docs/README.md).

```
v2/
  CURRENT_SPRINT.md   задача этой сессии
  frontend/           Next.js 15
  backend/            Django 5.2
  infra/              Compose, Caddy
  docs/               план, архитектура, словари
```

Срез поднимается Compose из `v2/infra`. Без `up` это исходники, не сайт.
