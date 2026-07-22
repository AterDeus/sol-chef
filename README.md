# sol-chef — Кухонная шпаргалка

Личный сайт-справочник: крупы, мясо, советы Энди Кукса, рецепты.  
План: [PLAN.md](PLAN.md)

## Структура

```
index.html              — главная (контент из JSON)
recipe.html             — страница одного рецепта
js/main.js              — точка входа (+ модули в js/)
css/global.css          — переменные, шрифты, reset
css/layout.css          — wrap, header, tabs
css/components.css      — карточки, таблицы
style.css               — @import css/*
data/
  site.json             — название, описание сайта
  grains.json           — таблица круп
  meat-beef.json        — говядина
  meat-pork.json        — свинина
  meat-poultry.json     — птица
  tips.json             — советы Энди
  recipes/              — рецепты (index.json + файлы по методу/продукту)
  schemas/              — JSON Schema
docs/                   — промпты для ИИ
scripts/                — валидация JSON
assets/favicon.svg
.github/workflows/      — CI
```

## Локальный просмотр

```bash
python -m http.server 3456
```

## Публикация на GitHub Pages

1. Создайте репозиторий `sol-chef` на GitHub.
2. Push всех файлов в `main`.
3. **Settings → Pages** → branch `main`, folder `/ (root)`.
4. Сайт: `https://ваш-логин.github.io/sol-chef/`

## Домен sol-chef.ru (когда купите)

1. Переименуйте `CNAME.example` → `CNAME` (содержимое: `sol-chef.ru`).
2. DNS у регistratora: A-записи GitHub Pages (см. [PLAN.md](PLAN.md)).
3. GitHub → Settings → Pages → Custom domain.

До покупки домена **не** добавляйте файл `CNAME` — иначе может сломаться URL на github.io.

## Добавление контента через ИИ

| Этап | Документ |
|------|----------|
| Системный промпт для ChatGPT/Claude | [docs/RECIPE_AI_SYSTEM.md](docs/RECIPE_AI_SYSTEM.md) |
| Короткая версия (custom instructions) | [docs/RECIPE_AI_PROMPT.txt](docs/RECIPE_AI_PROMPT.txt) |
| Добавить в Cursor после JSON | [docs/ADD_RECIPE.md](docs/ADD_RECIPE.md) |
| Советы | [docs/ADD_TIP.md](docs/ADD_TIP.md) |

## Валидация локально

```bash
node scripts/validate-recipes.js
node scripts/validate-tips.js
node scripts/validate-reference.js
```

Подробнее: [CONTRIBUTING.md](CONTRIBUTING.md)
