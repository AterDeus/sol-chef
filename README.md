# sol-chef — Кухонная шпаргалка

Сайт: **[sol-chef.ru](https://sol-chef.ru)**. Приложение **2.0** — папка [`v2/`](v2/) (Next.js + Django + Postgres). Статический V1 лежит в [`archive/v1/`](archive/v1/).

Next и Django в корень не переносить.

## Запуск локально

```bash
cp v2/infra/.env.example v2/infra/.env
docker compose -f v2/infra/docker-compose.yml up --build
```

Сайт: http://localhost:8080

Задача сессии: [`v2/CURRENT_SPRINT.md`](v2/CURRENT_SPRINT.md). Агент: [`v2/AGENTS.md`](v2/AGENTS.md).

## Прод на ВМ + домен

Сейчас в DNS домен ещё может смотреть на GitHub Pages (V1). Перенос на ВМ Timeweb: **[`v2/docs/CUTOVER.md`](v2/docs/CUTOVER.md)**.

Пока V2 не открывается по `https://sol-chef.ru`, **не пушить `main`**: в корне больше нет `index.html` / `CNAME`, Pages перестанет отдавать сайт.

## Архив V1

```bash
cd archive/v1
python -m http.server 3456
```
