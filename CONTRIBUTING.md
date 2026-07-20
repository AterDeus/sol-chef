# Руководство по наполнению sol-chef

## Быстрый старт

1. Откройте проект в Cursor.
2. Для рецепта — промпт из [docs/ADD_RECIPE.md](docs/ADD_RECIPE.md).
3. Проверьте локально: `python -m http.server` → http://localhost:8000
4. Закоммитьте и запушьте в `main`.

## Структура данных

- `data/recipes.json` — все рецепты (массив объектов)
- `data/schemas/recipe.schema.json` — формат записи

## Публикация

GitHub Pages: Settings → Pages → branch `main`, folder `/ (root)`.

После push CI (`.github/workflows/validate.yml`) проверяет JSON.  
Если CI красный — исправьте ошибки до merge; на сайте останется предыдущая версия.

## Что проверить после добавления рецепта

- [ ] Карточка на вкладке «Рецепты»
- [ ] Поиск находит по названию/тегам
- [ ] Страница `recipe.html?id=ваш-id` открывается
- [ ] Ссылка «Источник» ведёт на видео/статью

## CI локально

```bash
node scripts/validate-recipes.js
node scripts/validate-tips.js
node scripts/validate-reference.js
```

## Домен sol-chef.ru

Инструкция в [PLAN.md](PLAN.md), раздел «Подключение домена».
