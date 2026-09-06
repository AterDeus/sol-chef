# Черновики оверлея 43

Не канон. Правила: [RECIPE.md](../../RECIPE.md), задача: [CURRENT_SPRINT.md](../../../CURRENT_SPRINT.md).

| Путь | Что |
|------|-----|
| `recipes/<slug>.json` | карточка 2.0 (DATA-MODEL: профиль, variants 0–10, adaptations) |
| `reviews/<slug>.json` | вердикт независимого агента |

В Postgres только после `verdict=accept` и `cookable=true`:

```text
python manage.py import_draft --check
python manage.py import_draft --accepted
```

Packet оверлея = V1 JSON того же slug в корневом `data/recipes/`. Не писать в `data/recipes/`.
