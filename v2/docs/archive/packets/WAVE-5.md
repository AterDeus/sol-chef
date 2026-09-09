# Волна 5 — 10 packet’ов (овощи остаток, бобовые, крупы)

После волны 4.

---

### 1. `zapechennye-ovoshchi`

```json
{
  "id": "zapechennye-ovoshchi",
  "title": "Запечённые овощи",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "смесь овощей g (кабачок+перец+морковь) или один якорь кабачок",
  "use_cases": ["one_pan", "easy", "budget"],
  "situations": ["противень", "аэрогриль", "гриль"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше объём", "встряхивание"]},
    {"code": "grill", "title": "На гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["ломти толще", "переворот"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method oven→air_fryer", "method oven→grill"],
  "safety": {"target_note": "грибы только whitelist если добавите"},
  "author_must": ["масло количеством", "нарезка в detail", "не путать с рагу"],
  "author_free": ["баклажан в базе"],
  "do_not": ["мясо"]
}
```

---

### 2. `kartofel-s-gribami`

```json
{
  "id": "kartofel-s-gribami",
  "title": "Картофель с грибами",
  "recipe_family": "potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "pan_fry",
  "dish_type": "side",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "картофель, g, is_anchor",
  "use_cases": ["easy", "one_pan", "budget"],
  "situations": ["сковорода", "духовка", "аэрогриль"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше порция"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer"],
  "safety": {"target_note": "шампиньоны/вешенки; не лесные"},
  "author_must": ["грибы whitelist g, лук"],
  "author_free": ["сметана optional"],
  "do_not": ["protein_base=mushrooms если картофель основа блюда"]
}
```

---

### 3. `zharenaya-kartoshka-s-lukom`

```json
{
  "id": "zharenaya-kartoshka-s-lukom",
  "title": "Жареная картошка с луком",
  "recipe_family": "potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "pan_fry",
  "dish_type": "side",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "картофель, g, is_anchor",
  "use_cases": ["fast", "easy", "budget", "pantry"],
  "situations": ["сковорода партии"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_mushrooms", "title": "С грибами", "must": ["whitelist"]},
    {"code": "with_bacon", "title": "С беконом", "must": ["бекон g", "allergen нет типично", "protein не менять"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission лишнего масла"],
  "safety": {"target_note": "не сырая середина"},
  "author_must": ["лук, масло, партии, крышка затем без"],
  "author_free": ["укроп"],
  "do_not": ["деревенский в духовке волны 1"]
}
```

---

### 4. `tsvetnaya-kapusta-v-duhovke`

```json
{
  "id": "tsvetnaya-kapusta-v-duhovke",
  "title": "Цветная капуста в духовке",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "цветная капуста, g, is_anchor",
  "use_cases": ["easy", "one_pan"],
  "situations": ["форма", "аэрогриль"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["соцветия меньше партия"]}
  ],
  "addons": [
    {"code": "with_cheese", "title": "С сыром", "must": ["сыр g"]},
    {"code": "with_sour_cream", "title": "Со сметаной", "must": ["сметана"]}
  ],
  "energy": [],
  "adaptations_hint": ["method oven→air_fryer"],
  "safety": {"target_note": "—"},
  "author_must": ["соцветия, масло или сметана в базе"],
  "author_free": ["панировка сухари"],
  "do_not": ["тушёная белокочанная волны 1"]
}
```

---

### 5. `chechevitsa-s-ovoshchami`

```json
{
  "id": "chechevitsa-s-ovoshchami",
  "title": "Чечевица с овощами",
  "recipe_family": "legumes",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "boil",
  "dish_type": "pasta_grains",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "чечевица сухая, g, is_anchor",
  "use_cases": ["budget", "pantry", "easy", "batch"],
  "situations": ["кастрюля", "тушение гуще"],
  "equipment_variants": [
    {"code": "pot_stew", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["меньше воды", "овощи вместе"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method boil→stew"],
  "safety": {"target_note": "красная vs зелёная — указать в detail, время разное"},
  "author_must": ["лук морковь томат", "соотношение крупа/вода"],
  "author_free": ["красная чечевица проще для новичка"],
  "do_not": ["protein_base=vegetables", "мультиварка"]
}
```

---

### 6. `fasol-tushenaya-s-ovoshchami`

```json
{
  "id": "fasol-tushenaya-s-ovoshchami",
  "title": "Фасоль, тушённая с овощами",
  "recipe_family": "legumes",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "фасоль варёная или консервированная g — честно в detail; сухая потребует prep замачивание",
  "use_cases": ["budget", "batch", "pantry"],
  "situations": ["кастрюля", "казан"],
  "equipment_variants": [
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["стенки"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["equipment pot→kazan"],
  "safety": {"target_note": "сухая фасоль варить до мягкости; не сырая"},
  "author_must": ["лук морковь томат", "если сухая — prep замачивание"},
  "author_free": ["консервированная как база проще"],
  "do_not": ["лобио как второй slug"]
}
```

---

### 7. `gorohovoe-pyure`

```json
{
  "id": "gorohovoe-pyure",
  "title": "Гороховое пюре",
  "recipe_family": "legumes",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "boil",
  "dish_type": "side",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "горох колотый сухой, g, is_anchor",
  "use_cases": ["budget", "pantry", "easy"],
  "situations": ["кастрюля"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_smoked", "title": "С копчёностями", "must": ["копчёности g optional к гарниру", "не менять protein_base"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission копчёностей"],
  "safety": {"target_note": "разварить полностью"},
  "author_must": ["вода ml, соль gentle", "prep замачивание если нужно"],
  "author_free": ["масло в конце"],
  "do_not": ["мультиварка"]
}
```

---

### 8. `ris-na-garnir`

```json
{
  "id": "ris-na-garnir",
  "title": "Рис на гарнир",
  "recipe_family": "rice",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "boil",
  "dish_type": "side",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "рис сухой, g, is_anchor",
  "use_cases": ["easy", "pantry", "budget"],
  "situations": ["рассыпчатый", "с овощами", "под жареный рис"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_vegetables", "title": "С овощами", "must": ["морковь лук g"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "—"},
  "author_must": ["соотношение рис/вода, промыть", "notes: остывший для жареного риса V1"],
  "author_free": ["круглозёрный vs длинный в detail"],
  "do_not": ["ризотто V1", "рисоварка", "плов волны 1"]
}
```

Гарнир без мяса: `protein_base=vegetables` (крупа как гарнир, не `vegetarian` для новых).

---

### 9. `kartofelnoe-pyure`

```json
{
  "id": "kartofelnoe-pyure",
  "title": "Картофельное пюре",
  "recipe_family": "potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "boil",
  "dish_type": "side",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "картофель, g, is_anchor",
  "use_cases": ["easy", "budget"],
  "situations": ["молочное", "без молока", "с маслом", "с чесноком"],
  "equipment_variants": [],
  "addons": [
    {"code": "dairy_free", "title": "Без молока", "must": ["убрать молоко", "вода или бульон"]},
    {"code": "with_butter", "title": "Больше масла", "must": ["масло g"]},
    {"code": "with_roasted_garlic", "title": "С печёным чесноком", "must": ["чеснок запечь шаг"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["omission cow_milk", "substitution milk→water"],
  "safety": {"target_note": "—"},
  "author_must": ["молоко ml и масло в базе", "не комки в notes"],
  "author_free": ["желток optional"],
  "do_not": ["жареная картошка"]
}
```

База молочная. Addon `dairy_free` убирает молоко.

---

### 10. `pshennaya-kasha`

```json
{
  "id": "pshennaya-kasha",
  "title": "Пшённая каша",
  "recipe_family": "kasha",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "boil",
  "dish_type": "side",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "пшено, g, is_anchor",
  "use_cases": ["budget", "pantry", "easy"],
  "situations": ["гарнир на воде", "молочная", "с тыквой"],
  "equipment_variants": [],
  "addons": [
    {"code": "milk", "title": "Молочная", "must": ["молоко ml", "breakfast уместно в notes не dish_type обязателен side"]},
    {"code": "with_pumpkin", "title": "С тыквой", "must": ["тыква g"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "пшено промыть от горечи"},
  "author_must": ["вода ml база гарнир", "промыть в шаге"],
  "author_free": ["масло"],
  "do_not": ["гречка V1"]
}
```
