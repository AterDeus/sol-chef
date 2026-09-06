# Волна 3 — 10 packet’ов (буженина, говядина, рыба)

После волны 2. Эталон бархатной говядины. Якорь в г, заметки 3–10, адаптации на переходы способа.

---

### 1. `buzhenina`

```json
{
  "id": "buzhenina",
  "title": "Буженина",
  "recipe_family": "roast_pork",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "oven",
  "allowed_cuts": ["neck", "shoulder"],
  "anchor": "свинина цельным куском, g, is_anchor",
  "use_cases": ["batch", "easy"],
  "situations": ["запекание", "на нарезку"],
  "equipment_variants": [],
  "addons": [
    {"code": "sleeve", "title": "В рукаве", "must": ["шаги рукава", "другое время/сочность"]},
    {"code": "foil", "title": "В фольге", "must": ["развернуть в конце для корочки"]},
    {"code": "slow", "title": "Медленно", "must": ["ниже температура камеры", "дольше стенка"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "63 °C + hold 180 или 71 °C в центре"},
  "author_must": ["чеснок в надрезы с количеством", "соль, время отдыха"],
  "author_free": ["горчица/паприка маринад"],
  "do_not": ["три slug рукав/фольга", "фарш"]
}
```

---

### 2. `kotlety-iz-govyadiny`

```json
{
  "id": "kotlety-iz-govyadiny",
  "title": "Котлеты из говядины",
  "recipe_family": "kotlety",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["mince"],
  "anchor": "говяжий фарш, g, is_anchor",
  "use_cases": ["fast", "budget", "batch", "easy"],
  "situations": ["сковорода", "духовка", "гриль летом", "в соусе"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["противень"]},
    {"code": "grill", "title": "На гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["толщина", "переворот"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["размер"]},
    {"code": "pot", "title": "В соусе", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["томат/сметана", "томление"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→grill", "method pan_fry→air_fryer", "method pan_fry→stew"],
  "safety": {"target_note": "фарш 71 °C; ground_meat; rare запрещён"},
  "author_must": ["лук, хлеб, яйцо", "партии"],
  "author_free": ["свинина 10–20% в базе можно как detail, не второй protein_base"],
  "do_not": ["slug тефтелей (тот ниже отдельно)"]
}
```

---

### 3. `befstroganov`

```json
{
  "id": "befstroganov",
  "title": "Бефстроганов",
  "recipe_family": "stroganoff",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["rump", "tenderloin"],
  "anchor": "говядина, g, is_anchor",
  "use_cases": ["fast", "easy"],
  "situations": ["со сметаной", "полегче йогурт", "с грибами"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_sour_cream", "title": "Со сметаной", "must": ["если сметана не в базе — добавить; если база уже со сметаной — этот addon не плодить"]},
    {"code": "with_mushrooms", "title": "С грибами", "must": ["whitelist g"]},
    {"code": "light", "axis_note": "energy light", "must": ["меньше масла, йогурт вместо сливок/жирной сметаны"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["substitution sour_cream→yogurt"],
  "safety": {"target_note": "полоски до серого, не тартар"},
  "author_must": ["лук, сметана или сливки в базе с количеством", "нарезка поперёк"],
  "author_free": ["горчица, бульон 50–100 ml"],
  "do_not": ["печень строганов — другой slug", "стейк"]
}
```

База уже со сметаной. Addon `with_sour_cream` не делать. `light` = axis energy. Грибы = addon.

---

### 4. `gulyash-iz-govyadiny`

```json
{
  "id": "gulyash-iz-govyadiny",
  "title": "Гуляш из говядины",
  "recipe_family": "gulyash",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": ["shoulder", "shank"],
  "anchor": "говядина, g, is_anchor",
  "use_cases": ["batch", "easy", "budget"],
  "situations": ["долго почти без внимания", "казан", "духовка"],
  "equipment_variants": [
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["стенки"]},
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["утятница/крышка", "время"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven"],
  "safety": {"target_note": "до мягкости, не rare"},
  "author_must": ["паприка, лук, жидкость", "не свиной гуляш волны 2"],
  "author_free": ["томатная паста"],
  "do_not": ["стейк"]
}
```

---

### 5. `tefteli-iz-govyadiny`

```json
{
  "id": "tefteli-iz-govyadiny",
  "title": "Тефтели из говядины в соусе",
  "recipe_family": "kotlety",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": ["mince"],
  "anchor": "говяжий фарш, g, is_anchor",
  "use_cases": ["batch", "easy", "budget"],
  "situations": ["соус", "духовка в форме"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма", "соус снизу"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method stew→oven"],
  "safety": {"target_note": "фарш 71 °C; ground_meat"},
  "author_must": ["рис в фарше или без — честно; томатный соус ml", "не плоские котлеты волны 3.2"],
  "author_free": ["сметана в соусе"],
  "do_not": ["куриные тефтели как отдельный slug"]
}
```

---

### 6. `govyadina-s-kartofelem`

```json
{
  "id": "govyadina-s-kartofelem",
  "title": "Говядина с картофелем",
  "recipe_family": "one_pan_potato",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": ["shoulder", "shank"],
  "anchor": "говядина, g, is_anchor",
  "use_cases": ["one_pan", "batch", "budget"],
  "situations": ["форма", "казан", "тушение"],
  "equipment_variants": [
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["жидкость", "время"]},
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["крышка"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method oven→stew", "equipment baking_dish→kazan"],
  "safety": {"target_note": "лопатка/голяшка до мягкости"},
  "author_must": ["картофель и лук весом", "не стейк с картошкой фри"],
  "author_free": ["морковь"],
  "do_not": ["свинина с картофелем волны 2"]
}
```

---

### 7. `mintay-v-duhovke`

```json
{
  "id": "mintay-v-duhovke",
  "title": "Минтай в духовке",
  "recipe_family": "white_fish",
  "stream": "wave",
  "protein_base": "fish_white_sea",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "филе минтая, g, is_anchor",
  "use_cases": ["budget", "easy", "fast", "one_pan"],
  "situations": ["дешёвая рыба", "сковорода", "пар", "аэрогриль"],
  "equipment_variants": [
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["корочка", "не развалить"]},
    {"code": "steam", "title": "На пару", "cook_method_override": "steam", "must_differ": ["без масла почти", "время"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше порция"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method oven→pan_fry", "method oven→steam", "method oven→air_fryer"],
  "safety": {"target_note": "рыба 63 °C"},
  "author_must": ["лимон, лук или масло в базе", "не лосось"],
  "author_free": ["укроп"],
  "do_not": ["кляр — другой slug волны 4"]
}
```

---

### 8. `hek-s-ovoshchami`

```json
{
  "id": "hek-s-ovoshchami",
  "title": "Хек с овощами",
  "recipe_family": "white_fish",
  "stream": "wave",
  "protein_base": "fish_white_sea",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "хек, g, is_anchor",
  "use_cases": ["one_pan", "budget", "easy"],
  "situations": ["форма с овощами", "тушение", "пар", "сковорода"],
  "equipment_variants": [
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["морковь лук слой", "жидкость"]},
    {"code": "steam", "title": "На пару", "cook_method_override": "steam", "must_differ": ["овощи отдельно или ниже"]},
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["сначала овощи"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method oven→stew", "method oven→steam", "method oven→pan_fry"],
  "safety": {"target_note": "63 °C"},
  "author_must": ["лук морковь весом", "не три slug хека"],
  "author_free": ["томат"],
  "do_not": ["минтай в кляре"]
}
```

---

### 9. `skumbriya-v-duhovke`

```json
{
  "id": "skumbriya-v-duhovke",
  "title": "Скумбрия в духовке",
  "recipe_family": "mackerel",
  "stream": "wave",
  "protein_base": "fish_red_sea",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "скумбрия, g или pcs с весом, is_anchor в g",
  "use_cases": ["budget", "easy", "one_pan"],
  "situations": ["духовка", "гриль", "фольга"],
  "equipment_variants": [
    {"code": "grill", "title": "На гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["решётка", "переворот", "жир капает"]}
  ],
  "addons": [
    {"code": "foil", "title": "В фольге", "must": ["шаги фольги", "открыть в конце optional"]}
  ],
  "energy": [],
  "adaptations_hint": ["method oven→grill"],
  "safety": {"target_note": "63 °C; не сырая у кости"},
  "author_must": ["лук лимон в базе", "потрошёная скумбрия магазина"},
  "author_free": ["перец горошек"],
  "do_not": ["лосось V1", "protein_base=fish_white_sea"]
}
```

Скумбрия в VOCAB ближе к красной жирной рыбе (`fish_red_sea`), не минтай.

---

### 10. `ryba-s-kartofelem`

```json
{
  "id": "ryba-s-kartofelem",
  "title": "Рыба с картофелем в одной форме",
  "recipe_family": "one_pan_potato",
  "stream": "wave",
  "protein_base": "fish_white_sea",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "филе белой рыбы, g, is_anchor; choice_group mintay/hek/cod",
  "use_cases": ["one_pan", "budget", "easy"],
  "situations": ["один противень", "тушение"],
  "equipment_variants": [
    {"code": "pot", "title": "Тушение", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["слои", "жидкость"]}
  ],
  "addons": [
    {"code": "hake", "title": "Хек", "must": ["replace канона рыбы если база минтай"]},
    {"code": "cod", "title": "Треска", "must": ["replace"]}
  ],
  "energy": [],
  "adaptations_hint": ["method oven→stew", "substitution pollock↔hake"],
  "safety": {"target_note": "63 °C"},
  "author_must": ["картофель весом, база минтай", "лук"],
  "author_free": ["сливки optional"],
  "do_not": ["четыре slug по виду рыбы", "лосось"]
}
```
