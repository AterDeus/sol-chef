# Вердикты модератора

Модель: GPT-5.6 Terra Medium. Промпт: [PROMPT.md](PROMPT.md) (чеклист + JSON, запрет инструментов). Канон: [RECIPE.md](../../RECIPE.md).

Оркестратор не даёт Terra ходить по репозиторию: в Task только текст промпта и JSON рецепта. Запрещены Read/Grep/Glob/Shell и любые пути.

Поля `<slug>.json`: `verdict`, `cookable`, `real`, `comment`, `recipe_json: null`. В БД только `accept` + `cookable: true`.
