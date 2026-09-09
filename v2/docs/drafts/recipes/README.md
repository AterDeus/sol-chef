# Черновики рецептов 2.0

Не канон. Правила: [RECIPE.md](../../RECIPE.md), задача: [CURRENT_SPRINT.md](../../../CURRENT_SPRINT.md). Здесь оверлей 43 и волны 1–9.

| Путь | Что |
|------|-----|
| `recipes/<slug>.json` | карточка 2.0 (DATA-MODEL: профиль, variants 0–10, adaptations) |
| `reviews/<slug>.json` | вердикт независимого агента |

В Postgres только после `verdict=accept` и `cookable=true`:

```text
python manage.py import_draft --check
python manage.py import_draft --accepted
```

Packet оверлея 43 = V1 JSON того же slug в корневом `data/recipes/`. Packet новой волны — [../packets/](../packets/README.md). Не писать в `data/recipes/`.
