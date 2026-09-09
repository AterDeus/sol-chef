# Пакеты «На неделю» — сентябрь (5 новых slug)

Не волна 1–9. Явный старт: чат 2026-09-09, бриф [BRIEFS-SEPTEMBER.md](../weekly-prep/BRIEFS-SEPTEMBER.md).

Автор: один JSON на packet → `v2/docs/drafts/recipes/<id>.json`. Эталон валидатора: `v2/backend/tests/fixtures/gold_overlay.json`. Terra после валидатора, не в этом файле.

Оверлеи B/C/D/I/G — не эти packet’ы (`PrepSlot.steps`).

Общее: супермаркет РФ; `servings` 2; якорь в г; заметки 3–10; `editorial_tested` не ставить; `source_type` article, редакция sol-chef, `source_url` null; без `kcal` на корне; без кодов `duhovka`/`skovoroda`; соль `gentle`; шаги бытовым русским.

---

### 1. `boul-s-gorbushoy-ili-tuntsem`

```json
{
  "id": "boul-s-gorbushoy-ili-tuntsem",
  "title": "Боул с горбушей или тунцом",
  "recipe_family": "fish_bowl",
  "stream": "wave",
  "protein_base": "fish_canned",
  "cook_method": "no_cook",
  "dish_type": "main",
  "equipment": null,
  "allowed_cuts": [],
  "anchor": "консервы рыбы, g, is_anchor; горбуша и тунец — choice_group, не два slug",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["крупа уже готовая или остывшая с вс", "на двоих часто две банки"],
  "equipment_variants": [],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["substitution canned pink salmon ↔ canned tuna"],
  "safety": {"target_note": "рыба уже готова; не raw_fish; соль после банки"},
  "author_must": ["крупа g (рис или гречка choice или одна база рис + notes гречка)", "огурец/помидор/зелень сейчас", "заправка масло+лимон или йогурт, не майонез как база", "servings 2, честно 1 или 2 банки"],
  "author_free": ["кунжут, капуста тонко"],
  "do_not": ["варить рыбу", "открывать банку впрок", "лапша быстрого приготовления", "микроволновка рыбы", "protein_base=seafood"]
}
```

Если `equipment` для `no_cook` без сосуда — ключ не ставить (пустое поле), не выдумывать `bowl` / `none`.

---

### 2. `teplyy-boul-s-tykvoy-i-fettoy`

```json
{
  "id": "teplyy-boul-s-tykvoy-i-fettoy",
  "title": "Тёплый боул с тыквой и фетой",
  "recipe_family": "autumn_bowl",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "тыква g + нут/фасоль g + сыр 60–80 г на порцию",
  "use_cases": ["easy", "budget"],
  "situations": ["тыква и овощи уже с противня вс — прогреть, не печь заново 40 мин", "гренки в будни"],
  "equipment_variants": [],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["substitution feta→brynza", "omission croutons если есть хлеб"],
  "safety": {"target_note": "tree_nut если орехи; milk на сыре"},
  "author_must": ["тыква, нут или фасоль банка, feta или брынза choice_group 60–80 г на едока", "2 ст. л. масла суммарно на противень", "при подаче: орехи/семечки XOR 1 ст. л. оливкового, не оба", "гренки ржаные или хлеб в шагах", "зелень", "два тела в notes: с нуля (противень) и из заготовки (прогреть)"],
  "author_free": ["специи тыквы"],
  "do_not": ["айсберг + 30 г сыра", "protein_base=vegetarian", "сыр коркой 40 мин", "завтрак"]
}
```

База `oven` — полный рецепт с сырой тыквой (книга должна готовиться с нуля). В notes / шаге: если овощи уже запечены — прогреть 8–10 мин.

---

### 3. `boul-s-nutom-i-zapechennymi-ovoshchami`

```json
{
  "id": "boul-s-nutom-i-zapechennymi-ovoshchami",
  "title": "Боул с нутом и запечёнными овощами",
  "recipe_family": "chickpea_bowl",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "нут g, is_anchor (банка после откидывания или сваренный)",
  "use_cases": ["fast", "easy", "pantry", "budget"],
  "situations": ["банка: промыть, 3 мин со специями", "овощи с противня прогреть", "второй день — разогрев вчерашнего боула"],
  "equipment_variants": [],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["substitution canned_chickpeas как база"],
  "safety": {"target_note": "не high-risk"},
  "author_must": ["нут, кумин кориандр паприка, лимон, масло, зелень", "овощи (кабачок/перец/морковь/тыква) g", "с нуля: овощи запечь; из заготовки: прогреть"],
  "author_free": ["зира"],
  "do_not": ["красная чечевица вместо нута", "сыр коркой", "protein_base=vegetarian"]
}
```

Нут 400 г готового на двоих может закрыть `protein` и `energy_source` одновременно. Для обеда слота редактор оценивает сытость; при недостатке — `companion` хлеб/крупа в `PrepSlot`, не второй slug и не обязательная крупа внутри этой карточки.

---

### 4. `govyadina-na-volokna-s-garnirom`

```json
{
  "id": "govyadina-na-volokna-s-garnirom",
  "title": "Говядина на волокна с гарниром",
  "recipe_family": "pulled_beef",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["shoulder"],
  "anchor": "готовые волокна говядины g, is_anchor (уже томлёные, с желе)",
  "use_cases": ["fast", "batch"],
  "situations": ["разморозить плоский пакет с запасом суток", "прогреть 5–10 мин с соком", "день 1 капуста, день 2 крупа"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_cabbage", "title": "С тушёной капустой", "add": ["капуста уже тушёная или быстро на сковороде"]},
    {"code": "with_groats", "title": "С гречкой или рисом", "add": ["готовая крупа"]}
  ],
  "energy": [],
  "adaptations_hint": ["addon cabbage vs groats взаимоисключающие"],
  "safety": {"target_note": "говядина повторный прогрев до горячего, ориентир 71 °C если куски сомнительны; не сырое мясо в этой карточке"},
  "author_must": ["граммы готовых волокон на 2 порции ~300–400 г", "как прогреть с желе не высушивая", "оба гарнира как addon с дельтой шагов — для слота-приёма обязателен один, база без чипа не FULL_MEAL", "notes: мясо из заготовки «тушёная говядина на волокна», не копировать 3,5 часа сюда", "зелень в тарелку"],
  "author_free": ["перец, соль после желе (оно уже солёное)"],
  "do_not": ["томление 3 часа в шагах этой карточки", "пирог", "второй slug на капусту", "свиной гуляш"]
}
```

Канон готовых волокон: если нет id — `new_ingredients` с честными аллергенами, или `beef` + detail «уже томлёная, разобранная на волокна».

---

### 5. `lobio-iz-krasnoy-fasoli-bystroe`

```json
{
  "id": "lobio-iz-krasnoy-fasoli-bystroe",
  "title": "Лобио из красной фасоли (быстрое)",
  "recipe_family": "lobio",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "красная фасоль g, is_anchor (банка после откидывания)",
  "use_cases": ["fast", "easy", "pantry", "budget"],
  "situations": ["15 мин из банки", "хлеб/лаваш в шагах подачи"],
  "equipment_variants": [],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["substitution cilantro omission quality low"],
  "safety": {"target_note": "tree_nut на грецких; кинза не unknown"},
  "author_must": ["фасоль красная банка, грецкие орехи, чеснок, кинза, хмели-сунели или кориандр+уцхо-сунели если нет смеси", "кислота (уксус или гранат/лимон)", "лук, масло", "лаваш или хлеб в шаге подачи с граммами"],
  "author_free": ["гранатовый соус, перец чили"],
  "do_not": ["колбаса", "варка сухой фасоли 2 часа как база", "protein_base=vegetarian", "пустая фасоль с луком без орехов", "раздувать карточку салатом: овощной companion — в слоте"]
}
```

Уцхо-сунели в магазине РФ не всегда есть — база на хмели-сунели + кориандр, уцхо в notes «если есть».
