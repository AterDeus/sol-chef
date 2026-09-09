# Черновики рецептов 2.0

Не канон. Правила: [RECIPE.md](../../RECIPE.md). Каталог живёт в **Postgres**, не в этой папке.

Новый или правленый slug — один JSON сюда, затем:

```text
python manage.py export_draft --slug <id> --path v2/docs/drafts/recipes/<id>.json
python manage.py import_draft --check --path v2/docs/drafts/recipes/<id>.json
python manage.py import_draft --path v2/docs/drafts/recipes/<id>.json
```

Эталон валидатора: `v2/backend/tests/fixtures/gold_overlay.json`. Не корневой `data/recipes/`.

Packet новой волны — [../packets/](../packets/README.md). Compose **не** импортирует эту папку: `import_v1` не затирает карточки с `time_profile`.
