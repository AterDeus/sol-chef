# Два slug — замена leftover («Без вчерашнего»)

Не волна 1–9. Не пять сентябрьских A/E/F/H/J. Явный старт: чат 2026-09-10 — человек: нужны **новые** карточки на место `reheat`, не slug из сетки недели и не готовый каталог (чечевица / картофель с грибами).

Автор: один JSON на packet → `v2/docs/drafts/recipes/<id>.json`. Эталон валидатора: `v2/backend/tests/fixtures/gold_overlay.json`. Карточка из БД: `export_draft --slug`. Terra после валидатора.

Общее: супермаркет РФ; `servings` 2; якорь в г; заметки 3–10; `editorial_tested` не ставить; `source_type` article, редакция sol-chef, `source_url` null; без `kcal` на корне; без кодов `duhovka`/`skovoroda`; соль `gentle`; шаги бытовым русским.

Будни **10–20 мин** активных рук. Это блюдо **с нуля в будни**, не из вс-бокса. Книга должна готовиться без набора. В notes можно коротко: если рис уже сварен — пропустить варку.

Не копировать `ovoshchnoe-ragu` / `kartofel-s-gribami` / `chechevitsa-s-ovoshchami` / лобио / боулы сентября.

---

### 1. `tushenye-kabachki-s-risom`

```json
{
  "id": "tushenye-kabachki-s-risom",
  "title": "Тушёные кабачки с рисом",
  "recipe_family": "zucchini_rice",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "кабачок g, is_anchor; рис сухой g — часть тарелки, не щепотка",
  "use_cases": ["fast", "easy", "budget", "one_pan"],
  "situations": ["сентябрь, кабачок в магазине", "обед вместо разогрева вчерашнего супа"],
  "equipment_variants": [],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["omission sour_cream", "substitution rice→buckwheat"],
  "safety": {"target_note": "без мяса; сметана milk"},
  "author_must": ["кабачок заметной порцией", "рис в составе и в шагах (сухой → готовый в кастрюле)", "лук и помидор или томатная паста", "сметана в тарелку", "хлеб в шаге подачи", "active_minutes ≤ 20, total ≤ 30"],
  "author_free": ["морковь, чеснок, укроп", "сковорода вместо кастрюли если одна посуда"],
  "do_not": ["духовка 40 мин", "фарш", "яйца в блюдо", "чечевица", "баклажан как основа", "protein_base=legumes"]
}
```

Если база на сковороде — `equipment=skillet`, `cook_method=stew` ок. Рис всё равно сварить: в той же кастрюле или рядом, не «добавить горсть».

---

### 2. `baklazhany-s-kartofelem-na-skovorode`

```json
{
  "id": "baklazhany-s-kartofelem-na-skovorode",
  "title": "Баклажаны с картофелем на сковороде",
  "recipe_family": "eggplant_potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "баклажан g + картофель g, оба заметные; не щепотка",
  "use_cases": ["fast", "easy", "budget", "one_pan"],
  "situations": ["сентябрь", "обед сытнее рыбного ужина"],
  "equipment_variants": [],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["omission garlic", "substitution eggplant volume → extra potato не делать"],
  "safety": {"target_note": "баклажан прожарить до мягкости, не сырая губка"},
  "author_must": ["баклажан и картофель оба якоря по смыслу, картофель можно не is_anchor если баклажан is_anchor", "лук", "масло g или tbsp", "помидор или томатная паста", "зелень", "хлеб в шаге подачи", "не перегружать сковороду", "active_minutes ≤ 20, total ≤ 30"],
  "author_free": ["чеснок, перец сладкий"],
  "do_not": ["духовка как база", "фарш", "яйца", "грибы как основа (это не картофель с грибами)", "кабачок как основа", "protein_base=mushrooms"]
}
```

---

Слоты kit (после accept):

| Набор | Слот leftover | Новый slug |
|--------|----------------|------------|
| Для занятых | вт обед (вместо борща) | `tushenye-kabachki-s-risom` |
| Бюджетная | ср обед (вместо супа) | `baklazhany-s-kartofelem-na-skovorode` |
| Бюджетная | вс обед (вместо нута) | `tushenye-kabachki-s-risom` |
