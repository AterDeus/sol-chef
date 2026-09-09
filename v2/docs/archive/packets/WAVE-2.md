# Волна 2 — 10 packet’ов (птица остаток + свинина)

После волны 1. Автор: эталон `v2/docs/drafts/recipes/barhatnaya-govyadina-po-kitajski.json`. Куда: `v2/docs/drafts/recipes/<id>.json`. Общее: супермаркет РФ, якорь в г, заметки 3–10, `adaptations` на каждый переход способа, `editorial_tested` не ставить, без URL.

---

### 1. `kurinye-krylyshki`

```json
{
  "id": "kurinye-krylyshki",
  "title": "Куриные крылышки",
  "recipe_family": "wings",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "oven",
  "allowed_cuts": ["wing"],
  "anchor": "крылья, g, is_anchor",
  "use_cases": ["batch", "budget", "easy"],
  "situations": ["противень", "аэрогриль малая порция", "мангал летом"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше штук", "встряхивание", "время короче"]},
    {"code": "grill", "title": "На гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["решётка", "переворот", "не тот же таймер духовки"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method oven→air_fryer", "method oven→grill"],
  "safety": {"target_note": "крыло как тёмное мясо: 82 °C; poultry_temp"},
  "author_must": ["маринад или сухая панировка с количествами", "не перегружать противень"],
  "author_free": ["мёд+соя или паприка", "сковорода только если честная дельта партий — иначе не добавлять"],
  "do_not": ["второй slug крыльев", "сырая середина без температуры"]
}
```

---

### 2. `kurinyy-sup-s-lapshoy`

```json
{
  "id": "kurinyy-sup-s-lapshoy",
  "title": "Куриный суп с лапшой",
  "recipe_family": "chicken_soup",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "boil",
  "dish_type": "soup",
  "equipment": "pot",
  "allowed_cuts": ["thigh", "breast"],
  "anchor": "курица, g, is_anchor",
  "use_cases": ["easy", "budget", "batch"],
  "situations": ["есть бедро или грудка", "лапша vs картофель vs рис"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_potato", "title": "С картофелем", "must": ["картофель g", "лапшу убрать или оставить мало — честно в дельте"]},
    {"code": "with_rice", "title": "С рисом", "must": ["рис g"]},
    {"code": "with_vermicelli", "title": "С вермишелью", "must": ["вермишель, не путать с яичной лапшой базы"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission лаврового"],
  "safety": {"target_note": "бедро 82 °C, грудка 72 °C — в шаге по allowed_cuts"},
  "author_must": ["морковь лук в базе", "лапша в базе с количеством", "грудка/бедро = cuts не чипы"],
  "author_free": ["укроп, бульон vs вода"],
  "do_not": ["три slug супа", "protein_base=vegetables"]
}
```

---

### 3. `kurinaya-grudka-s-ovoshchami`

```json
{
  "id": "kurinaya-grudka-s-ovoshchami",
  "title": "Куриная грудка с овощами",
  "recipe_family": "chicken_veg",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["breast"],
  "anchor": "куриная грудка, g, is_anchor",
  "use_cases": ["fast", "one_pan", "easy"],
  "situations": ["нет сковороды → духовка", "тушение если грудка сухая"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма", "время", "овощи крупнее"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше порция"]},
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["жидкость", "крышка", "не сухая корочка"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer", "method pan_fry→stew"],
  "safety": {"target_note": "грудка 72 °C"},
  "author_must": ["овощи весом (перец/кабачок/морковь — супермаркет)", "не целая тушка"],
  "author_free": ["какие три овоща"],
  "do_not": ["slug бёдер с картофелем (уже волна 1)"]
}
```

---

### 4. `kurinye-bedra-v-smetannom-souse`

```json
{
  "id": "kurinye-bedra-v-smetannom-souse",
  "title": "Куриные бёдра в сметанном соусе",
  "recipe_family": "chicken_sour_cream",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["thigh"],
  "anchor": "бёдра, g, is_anchor",
  "use_cases": ["easy", "one_pan"],
  "situations": ["сковорода с крышкой", "духовка довести", "тушение"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["после обжарки или сразу в форме"]},
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["больше жидкости", "время"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→stew", "substitution sour_cream→yogurt"],
  "safety": {"target_note": "бедро 82 °C"},
  "author_must": ["сметана с количеством", "лук"],
  "author_free": ["грибы только whitelist сверх packet"],
  "do_not": ["путать с бёдрами+картофель волны 1"]
}
```

---

### 5. `kurinaya-grudka-v-slivochnom-souse`

```json
{
  "id": "kurinaya-grudka-v-slivochnom-souse",
  "title": "Куриная грудка в сливочном соусе",
  "recipe_family": "chicken_cream",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["breast"],
  "anchor": "грудка, g, is_anchor",
  "use_cases": ["fast", "easy"],
  "situations": ["сливки дома", "духовка довести"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["соус не сжечь", "время"]}
  ],
  "addons": [
    {"code": "with_mushrooms", "title": "С грибами", "must": ["шампиньоны/вешенки g", "whitelist"]},
    {"code": "with_cheese", "title": "С сыром", "must": ["сыр g", "allergen milk уже в сливках"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "substitution cream→milk осторожно quality"],
  "safety": {"target_note": "грудка 72 °C"},
  "author_must": ["сливки ml", "не паста (паста с курицей — другой slug)"],
  "author_free": ["чеснок, горчица щепотка"],
  "do_not": ["карбонара", "deep_fry"]
}
```

---

### 6. `svinina-s-kartofelem`

```json
{
  "id": "svinina-s-kartofelem",
  "title": "Свинина с картофелем",
  "recipe_family": "one_pan_potato",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": ["shoulder", "neck"],
  "anchor": "свинина, g, is_anchor",
  "use_cases": ["one_pan", "batch", "budget", "easy"],
  "situations": ["одна форма", "казан", "тушение", "сковорода мельче куски"],
  "equipment_variants": [
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["жидкость", "крышка"]},
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["стенки", "меньше жидкости чем кастрюля"]},
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["куски мельче", "партии картофеля"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method oven→stew", "equipment baking_dish→kazan", "method oven→pan_fry"],
  "safety": {"target_note": "свинина 63 °C + hold 180 или 71 °C"},
  "author_must": ["лук и картофель весом", "не шашлык"],
  "author_free": ["паприка, лавр"],
  "do_not": ["slug тушёной капусты"]
}
```

---

### 7. `svinina-s-lukom`

```json
{
  "id": "svinina-s-lukom",
  "title": "Свинина с луком на сковороде",
  "recipe_family": "pork_onion",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["shoulder", "neck"],
  "anchor": "свинина, g, is_anchor",
  "use_cases": ["fast", "easy", "one_pan"],
  "situations": ["быстро", "потом тушение если жёсткая"],
  "equipment_variants": [
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["жидкость", "время"]},
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["томление"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method pan_fry→stew", "equipment skillet→kazan"],
  "safety": {"target_note": "63+hold или 71"},
  "author_must": ["лука много, весом или pcs", "партии"],
  "author_free": ["сметана в конце optional"],
  "do_not": ["отбивные волны 1"]
}
```

---

### 8. `svinye-rebra`

```json
{
  "id": "svinye-rebra",
  "title": "Свиные рёбра в духовке",
  "recipe_family": "pork_ribs",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "oven",
  "allowed_cuts": ["ribs"],
  "anchor": "рёбра, g, is_anchor",
  "use_cases": ["batch", "easy"],
  "situations": ["духовка долго", "мангал"],
  "equipment_variants": [
    {"code": "grill", "title": "На гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["фольга сначала или сразу решётка — честно в шагах", "переворот"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method oven→grill"],
  "safety": {"target_note": "свинина у кости 63+hold или 71; не сырая у кости"},
  "author_must": ["маринад количества", "время стенки честное 1.5–2 ч духовка"],
  "author_free": ["мёд/соя/горчица — один канон"],
  "do_not": ["говяжьи рёбра V1"]
}
```

---

### 9. `svinoy-gulyash`

```json
{
  "id": "svinoy-gulyash",
  "title": "Свиной гуляш",
  "recipe_family": "gulyash",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": ["shoulder", "neck"],
  "anchor": "свинина, g, is_anchor",
  "use_cases": ["batch", "easy", "budget"],
  "situations": ["долго без внимания", "казан", "духовка"],
  "equipment_variants": [
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["нагрев стенок"]},
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["крышка кастрюли/утятницы", "время"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven"],
  "safety": {"target_note": "мягкость + 63/71"},
  "author_must": ["паприка, лук, жидкость ml", "не путать с говяжьим гуляшом"],
  "author_free": ["картофель в гуляше optional addon max 1"],
  "do_not": ["второй protein в addon"]
}
```

---

### 10. `svinye-kotlety`

```json
{
  "id": "svinye-kotlety",
  "title": "Домашние свиные котлеты",
  "recipe_family": "kotlety",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["mince"],
  "anchor": "свиной фарш, g, is_anchor",
  "use_cases": ["fast", "budget", "batch", "easy"],
  "situations": ["фарш", "духовка без жарки", "аэрогриль"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["противень"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["размер", "переворот"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer"],
  "safety": {"target_note": "фарш 71 °C; ground_meat"},
  "author_must": ["хлеб/сухари, лук, яйцо", "партии сковороды"],
  "author_free": ["чеснок"],
  "do_not": ["куриные котлеты волны 1", "говяжьи — волна 3"]
}
```
