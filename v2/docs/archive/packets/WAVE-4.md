# Волна 4 — 10 packet’ов (рыба остаток, субпродукты, яйца, рагу)

После волны 3.

---

### 1. `mintay-v-klyare`

```json
{
  "id": "mintay-v-klyare",
  "title": "Минтай в кляре",
  "recipe_family": "white_fish",
  "stream": "wave",
  "protein_base": "fish_white_sea",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "филе минтая, g, is_anchor",
  "use_cases": ["fast", "budget"],
  "situations": ["жарка", "духовка меньше масла", "аэрогриль"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["противень", "кляр не стечёт — честный рецепт"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["тонкий слой масла"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer"],
  "safety": {"target_note": "63 °C; не deep_fry в этой волне"},
  "author_must": ["кляр: мука яйцо молоко/вода с количествами", "партии", "масло для жарки gentle"],
  "author_free": ["газировка в кляре"],
  "do_not": ["фритюрница", "mintay-v-duhovke волны 3"]
}
```

---

### 2. `ryba-v-smetannom-souse`

```json
{
  "id": "ryba-v-smetannom-souse",
  "title": "Рыба в сметанном соусе",
  "recipe_family": "white_fish",
  "stream": "wave",
  "protein_base": "fish_white_sea",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "филе, g, is_anchor; база хек или минтай",
  "use_cases": ["easy", "one_pan"],
  "situations": ["форма", "тушение"],
  "equipment_variants": [
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["крышка", "не кипятить сметану жёстко"]}
  ],
  "addons": [
    {"code": "pollock", "title": "Минтай", "must": ["replace если база хек"]},
    {"code": "cod", "title": "Треска", "must": ["replace"]}
  ],
  "energy": [],
  "adaptations_hint": ["method oven→stew"],
  "safety": {"target_note": "63 °C"},
  "author_must": ["сметана ml, лук", "choice_group в базе"],
  "author_free": ["сыр сверху"],
  "do_not": ["лосось"]
}
```

---

### 3. `kurinye-serdechki-v-smetane`

```json
{
  "id": "kurinye-serdechki-v-smetane",
  "title": "Куриные сердечки в сметанном соусе",
  "recipe_family": "offal_cream",
  "stream": "wave",
  "protein_base": "offal",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "куриные сердечки, g, is_anchor",
  "use_cases": ["budget", "easy"],
  "situations": ["тушение", "сковорода обжарка затем соус"],
  "equipment_variants": [
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["сначала обжарка партий", "сметана в конце"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method stew→pan_fry"],
  "safety": {"target_note": "птичьи субпродукты прожарить/протушить полностью, ориентир 74–82, не розовые"},
  "author_must": ["лук, сметана", "промыть/разрезать сгустки в шаге"],
  "author_free": ["лавр"],
  "do_not": ["protein_base=poultry"]
}
```

---

### 4. `pechen-po-stroganovski`

```json
{
  "id": "pechen-po-stroganovski",
  "title": "Печень по-строгановски",
  "recipe_family": "liver",
  "stream": "wave",
  "protein_base": "offal",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "говяжья печень, g, is_anchor",
  "use_cases": ["fast", "budget"],
  "situations": ["сковорода", "тушение в соусе"],
  "equipment_variants": [
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["не пересушить", "сметана"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method pan_fry→stew"],
  "safety": {"target_note": "печень прожарить без сырой крови; не путать с стейком medium"},
  "author_must": ["лук, сметана", "плёнку снять в шаге"],
  "author_free": ["мука обвалять"],
  "do_not": ["куриная печень addon (другой белок и время — не этот slug)", "protein_base=beef"]
}
```

---

### 5. `pechen-s-lukom`

```json
{
  "id": "pechen-s-lukom",
  "title": "Печень с луком",
  "recipe_family": "liver",
  "stream": "wave",
  "protein_base": "offal",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "печень говяжья или куриная choice_group, g, is_anchor — если choice ломает время, база говяжья",
  "use_cases": ["fast", "budget", "easy"],
  "situations": ["сковорода", "духовка довести"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["после обжарки лука"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method pan_fry→oven"],
  "safety": {"target_note": "не сырая"},
  "author_must": ["лука много", "не строганов (тот соседний slug)"],
  "author_free": ["сливочное масло"],
  "do_not": ["сливки обязательные как в строганове"]
}
```

---

### 6. `omlet`

```json
{
  "id": "omlet",
  "title": "Омлет",
  "recipe_family": "eggs",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "яйца, pcs; для масштаба лучше ещё молоко ml — яйца whole; можно servings 2 вместо якоря г",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["сковорода", "духовка пышный"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма", "без постоянного мешания"]}
  ],
  "addons": [
    {"code": "with_vegetables", "title": "С овощами", "must": ["перец/помидор g"]},
    {"code": "with_cheese", "title": "С сыром", "must": ["сыр g"]}
  ],
  "energy": [],
  "adaptations_hint": ["method pan_fry→oven"],
  "safety": {"target_note": "яйцо свернулось; не сырой центр если нет raw_egg"},
  "author_must": ["яйца количество, молоко или вода ml", "масло/жир"],
  "author_free": ["зелень"],
  "do_not": ["шакшука V1", "protein_base=vegetables"]
}
```

---

### 7. `syrniki`

```json
{
  "id": "syrniki",
  "title": "Сырники",
  "recipe_family": "syrniki",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "творог, g, is_anchor",
  "use_cases": ["fast", "easy", "budget"],
  "situations": ["сковорода", "духовка", "аэрогриль", "ленивые"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["без глубокой жарки"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["размер"]}
  ],
  "addons": [
    {"code": "lazy", "title": "Ленивые", "must": ["без лепки кружков: пласт или ложка", "другие шаги"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer"],
  "safety": {"target_note": "яйцо в тесте пропечь"},
  "author_must": ["творог жирность в detail, мука, яйцо, сахар", "не разваливаются — отжать влагу в notes"],
  "author_free": ["изюм optional"],
  "do_not": ["запеканка — соседний slug"]
}
```

---

### 8. `tvorozhnaya-zapekanka`

```json
{
  "id": "tvorozhnaya-zapekanka",
  "title": "Творожная запеканка",
  "recipe_family": "syrniki",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "oven",
  "dish_type": "breakfast",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "творог, g, is_anchor",
  "use_cases": ["easy", "batch", "budget"],
  "situations": ["форма", "аэрогриль малая"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше формы", "время"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method oven→air_fryer"],
  "safety": {"target_note": "центр схватился"},
  "author_must": ["яйца, манка или мука, сахар", "смазать форму"],
  "author_free": ["изюм, сметана сверху"],
  "do_not": ["сырники"]
}
```

---

### 9. `yaichnitsa-s-pomidorami`

```json
{
  "id": "yaichnitsa-s-pomidorami",
  "title": "Яичница с помидорами",
  "recipe_family": "eggs",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "яйца pcs + помидоры g; якорь помидоры g или servings",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["сковорода", "духовка"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method pan_fry→oven"],
  "safety": {"target_note": "без raw_egg если желток твёрдый; глазунья — осторожно"},
  "author_must": ["лук, помидоры весом, яйца", "не называть шакшукой (V1 другой slug)"],
  "author_free": ["перец"],
  "do_not": ["оверлей шакшуки"]
}
```

---

### 10. `ovoshchnoe-ragu`

```json
{
  "id": "ovoshchnoe-ragu",
  "title": "Овощное рагу",
  "recipe_family": "veg_stew",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "кабачок или смесь овощей: якорь кабачок g",
  "use_cases": ["budget", "batch", "one_pan", "easy"],
  "situations": ["кастрюля", "казан", "духовка", "сковорода глубокая"],
  "equipment_variants": [
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["меньше жидкости"]},
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма", "время"]},
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["партии", "крышка"]}
  ],
  "addons": [
    {"code": "with_potato", "title": "С картофелем", "must": ["картофель g"]},
    {"code": "with_eggplant", "title": "С баклажаном", "must": ["баклажан g"]},
    {"code": "with_mushrooms", "title": "С грибами", "must": ["whitelist"]}
  ],
  "energy": [],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven", "method stew→pan_fry"],
  "safety": {"target_note": "нет мяса в базе"},
  "author_must": ["кабачок перец лук томат в базе", "кабачок не отдельный slug"],
  "author_free": ["базилик"],
  "do_not": ["четыре addon сразу взаимоисключение — три addon ок как взаимоисключающие чипы"]
}
```
