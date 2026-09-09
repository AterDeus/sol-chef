---
name: sol-chef-recipe
description: Writes and moderates sol-chef 2.0 recipe JSON (VOCAB codes, SAFETY temps/allergens, Grok author → Terra Medium moderator). Use when drafting recipes, input packets, content waves, high-risk flags, or validating recipe JSON for sol-chef V2.
---

# Рецепты sol-chef 2.0

Сначала прочитать:

1. `v2/docs/RECIPE.md` — конвейер и ворота
2. `v2/docs/VOCAB.md` — коды
3. `v2/docs/SAFETY.md` — температуры, аллергены, high-risk

Без packet не выдумывать бриф. Без явного старта в чате / CURRENT_SPRINT («стартуй волну N» / «стартуй оверлей осей N») — не массовая генерация.

## Автор

Один JSON. Факты из packet. `id` = транслит `title`. Не заполнять `editorial_tested`. Не использовать коды `duhovka` / `skovoroda`. Соль — `gentle` (`ratio^0.7`). Сода в бархате/маринаде — `linear`; в выпечке и дрожжи — `manual`. Неизвестные аллергены — `unknown` **на каноне**, не `allergens_*` в строке рецепта.

Оверлей 43: эталон `v2/docs/drafts/recipes/barhatnaya-govyadina-po-kitajski.json`. Обязателен профиль (`time_profile`, effort/washing, `use_cases`). `variants` 0–10, не квота. `adaptations[]` отдельно. `new_ingredients` только если канона нет в сиде. `prep: []` не писать.

Восемь вопросов: основа; посуда; обязательное; что убрать; что заменить; другой способ; редакционные варианты; `use_cases` (не `dinner`/`cozy`).

Если данных мало: `{ "error": "чего не хватает" }`.

## Модератор (Terra Medium)

Оркестратор вставляет в промпт чеклист + JSON рецепта (`v2/docs/drafts/reviews/PROMPT.md`). Task: `model=gpt-5.6-terra-medium`, без вложений. Явный запрет: не вызывать инструменты, не открывать репозиторий. Terra проверяет готовится / ничего не упущено / вкусно / real / цепочка варианта / физика замены / русский без внутреннего жаргона. `recipe_json` всегда null.

## Куда писать

`v2/docs/drafts/recipes/<slug>.json`. Не корневой `data/recipes/`.
