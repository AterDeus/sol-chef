# V1 — архив

Статический сайт, который до cutover отдавал GitHub Pages на `sol-chef.ru`.

Не прод. Не править «чтобы починить текущий сайт» — текущий сайт это V2 в `v2/`. JSON здесь — сырьё ETL (`import_v1`), не рантайм Next.

Локально посмотреть архив:

```bash
cd archive/v1
python -m http.server 3456
```

Токены UI: `css/global.css` — копировать в V2, не перезаписывать.

Валидаторы JSON:

```bash
node archive/v1/scripts/validate-recipes.js
node archive/v1/scripts/validate-tips.js
node archive/v1/scripts/validate-reference.js
```

Выход на VPS и домен: [v2/docs/CUTOVER.md](../../v2/docs/CUTOVER.md).
