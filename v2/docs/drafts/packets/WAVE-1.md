# Волна 1 — 10 packet’ов

После волны 1 сразу [WAVE-2.md](WAVE-2.md). Не ждать отдельной фразы на каждую пачку, если человек сказал волны подряд.

Старт пачки — фраза **«стартуй волну 1»** (или «волны одна за одной»). Автор: один JSON на packet, эталон `v2/docs/drafts/recipes/barhatnaya-govyadina-po-kitajski.json`.

Оверлей шашлыка — не в эту десятку (тот же V1 id). Packet для него — внизу, делать в потоке оверлея 43.

High-risk в волну 1 не класть. `editorial_tested` не ставить. Источник: редакция sol-chef, без URL.

Общее для всех десяти: супермаркет РФ; якорь в г; заметки 3–10; `adaptations` на каждый обязательный переход способа; минуты базы в `time_profile`; в дельте способа — другие шаги и другая стенка времени.

---

### 1. `kurinye-bedra-s-kartofelem`

```json
{
  "id": "kurinye-bedra-s-kartofelem",
  "title": "Куриные бёдра с картофелем",
  "recipe_family": "one_pan_potato",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": ["thigh", "drumstick"],
  "anchor": "куриные бёдра, g, is_anchor",
  "use_cases": ["one_pan", "budget", "easy", "batch"],
  "situations": ["одна форма", "нет духовки → сковорода или казан", "мало порции → аэрогриль"],
  "equipment_variants": [
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["партии", "крышка", "картофель кубиком мельче"]},
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["жидкость", "томление", "не сухая корочка духовки"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше штук", "время короче", "не перегружать чашу"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method oven→pan_fry", "method oven→stew", "method oven→air_fryer", "omission лишнего масла"],
  "safety": {"target_note": "бедро/голень 82 °C; флаг poultry_temp если уместно"},
  "author_must": ["лук в базе (одна форма)", "картофель как весовая строка", "не превращать в целую курицу"],
  "author_free": ["специи", "паприка/чеснок", "нужен ли розмарин"],
  "do_not": ["отдельный slug голеней", "гриль без дельты"]
}
```

---

### 2. `kurinye-kotlety`

```json
{
  "id": "kurinye-kotlety",
  "title": "Куриные котлеты",
  "recipe_family": "kotlety",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["mince"],
  "anchor": "куриный фарш, g, is_anchor",
  "use_cases": ["fast", "budget", "easy", "batch"],
  "situations": ["фарш в магазине", "без сковороды → духовка/аэрогриль", "под крупу → тефтели в соусе"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["противень", "без глубокой жарки"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["размер котлет", "переворот"]},
    {"code": "pot", "title": "Тефтели в соусе", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["форма шариков", "томат или сметана", "время томления"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer", "method pan_fry→stew"],
  "safety": {"target_note": "фарш птицы 74 °C; high_risk ground_meat"},
  "author_must": ["хлеб/сухари с количеством", "не перегружать сковороду"},
  "author_free": ["лук, яйцо, травки", "какой соус у тефтелей"],
  "do_not": ["отдельный slug тефтелей", "говяжий фарш в этом id"]
}
```

---

### 3. `svinye-otbivnye`

```json
{
  "id": "svinye-otbivnye",
  "title": "Свиные отбивные",
  "recipe_family": "otbivnye",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["loin", "neck"],
  "anchor": "свинина, g, is_anchor",
  "use_cases": ["fast", "easy"],
  "situations": ["нет сковороды → духовка", "мангал летом", "аэрогриль на 1–2 штуки"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["толщина", "доведение после корочки или сразу"]},
    {"code": "grill", "title": "На гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["решётка", "переворот", "не тот же таймер сковороды"]},
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["одна партия"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→grill", "method pan_fry→air_fryer"],
  "safety": {"target_note": "цельный кусок 63 °C + hold 180 или 71 °C"},
  "author_must": ["отбить в шаге", "соль gentle"},
  "author_free": ["панировка да/нет; если есть — light без панировки"],
  "do_not": ["шашлык", "фарш"]
}
```

---

### 4. `tushenaya-kapusta`

```json
{
  "id": "tushenaya-kapusta",
  "title": "Тушёная капуста",
  "recipe_family": "kapusta",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "капуста белокочанная, g, is_anchor",
  "use_cases": ["budget", "batch", "pantry", "one_pan"],
  "situations": ["без мяса из базы", "есть свинина / курица → addon", "казан", "духовка в форме"],
  "equipment_variants": [
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["нагрев стенок", "меньше жидкости"]},
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["крышка/фольга", "время"]}
  ],
  "addons": [
    {"code": "with_pork", "title": "Со свининой", "must": ["весовая свинина", "allergen_delta пустой если нет новых аллергенов"]},
    {"code": "with_chicken", "title": "С курицей", "must": ["бедро или голень", "82 °C в шаге addon"]}
  ],
  "energy": [],
  "adaptations_hint": ["equipment pot→kazan", "equipment pot→baking_dish", "omission томатной пасты"],
  "safety": {"target_note": "addon с курицей — 82 °C; свинина в addon — как цельный или кусок по SAFETY"},
  "author_must": ["база вегетарианская", "грибы только whitelist если добавите сверх packet"],
  "author_free": ["томат, лавр, уксус/сахар", "нужна ли морковь в базе"],
  "do_not": ["три slug капусты", "protein_base=pork у этого id"]
}
```

---

### 5. `rybnye-kotlety`

```json
{
  "id": "rybnye-kotlety",
  "title": "Рыбные котлеты",
  "recipe_family": "kotlety",
  "stream": "wave",
  "protein_base": "fish_white_sea",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "филе минтая или хека, g, is_anchor; choice_group=white_fish",
  "use_cases": ["budget", "fast", "easy"],
  "situations": ["дешёвая белая рыба", "без жарки → духовка или пар"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["противень", "масло меньше"]},
    {"code": "steam", "title": "На пару", "cook_method_override": "steam", "must_differ": ["без корочки", "время", "форма чтобы не развалились"]}
  ],
  "addons": [
    {"code": "tefteli", "title": "Тефтели", "optional": true, "must": ["только если шаги и соус реально другие; иначе не плодить"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→steam", "substitution mintay↔hake"],
  "safety": {"target_note": "рыба 63 °C; аллерген fish на каноне"},
  "author_must": ["choice_group минтай/хек", "не лосось"],
  "author_free": ["картофель vs хлеб в фарше", "укроп"],
  "do_not": ["отдельные slug минтая и хека", "raw_fish"]
}
```

---

### 6. `farshirovannye-pertsy`

```json
{
  "id": "farshirovannye-pertsy",
  "title": "Фаршированные перцы",
  "recipe_family": "pertsy",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "stew",
  "dish_type": "main",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "болгарский перец, pcs или g, is_anchor",
  "use_cases": ["batch", "budget", "one_pan"],
  "situations": ["на несколько дней", "духовка вместо плиты", "казан", "без мяса"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["форма", "жидкость снизу", "время"]},
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["слой, крышка"]}
  ],
  "addons": [
    {"code": "beef", "title": "С говядиной", "must": ["фарш g", "71 °C", "ground_meat"]},
    {"code": "pork", "title": "Со свининой", "must": ["фарш", "71 °C"]},
    {"code": "chicken", "title": "С курицей", "must": ["фарш птицы 74 °C"]},
    {"code": "rice_vegetable", "title": "С рисом, без мяса", "must": ["убрать фарш", "аллергены мяса не оставлять"]}
  ],
  "energy": [],
  "adaptations_hint": ["equipment pot→baking_dish", "equipment pot→kazan"],
  "safety": {"target_note": "температура по addon фарша; база без мяса — не ground_meat"},
  "author_must": ["рис в начинке базы или в мясных addon", "томатная жидкость с количеством"},
  "author_free": ["морковь/лук в зажарке"],
  "do_not": ["четыре slug перцев", "protein_base=beef у этого id"]
}
```

База: перец + рис + овощи (чтобы `rice_vegetable` был близок к телу). Мясные addon **добавляют** фарш, не требуют выбрать мясо обязательно.

---

### 7. `kurinyy-plov`

```json
{
  "id": "kurinyy-plov",
  "title": "Куриный плов",
  "recipe_family": "plov",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "stew",
  "dish_type": "pasta_grains",
  "equipment": "kazan",
  "allowed_cuts": ["thigh", "drumstick"],
  "anchor": "рис, g, is_anchor — или курица, если якорь честнее; один якорь",
  "use_cases": ["batch", "one_pan", "budget"],
  "situations": ["нет казана → кастрюля с толстым дном", "духовка довести"],
  "equipment_variants": [
    {"code": "pot", "title": "В кастрюле", "cook_method_override": "stew", "equipment": "pot", "must_differ": ["риск пригорания", "огонь", "не мешать зря"]},
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["после зирвака или вся сборка"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["equipment kazan→pot", "method stew→oven"],
  "safety": {"target_note": "курица 82 °C в куске"},
  "author_must": ["зирвак отдельным шагом", "соотношение рис/жидкость", "не путать с рассыпчатым гарниром"],
  "author_free": ["зира, барбарис — только если обычный супермаркет; иначе без"],
  "do_not": ["говядина addon (это другой slug семьи plov)", "мультиварка"]
}
```

---

### 8. `makarony-po-flotski`

```json
{
  "id": "makarony-po-flotski",
  "title": "Макароны по-флотски",
  "recipe_family": "pasta_mince",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "dish_type": "pasta_grains",
  "equipment": "skillet",
  "allowed_cuts": ["mince"],
  "anchor": "говяжий фарш, g, is_anchor",
  "use_cases": ["fast", "budget", "easy", "pantry"],
  "situations": ["фарш дома", "свинина вместо говядины", "кастрюля если сковорода мала"],
  "equipment_variants": [
    {"code": "pot", "title": "В кастрюле", "cook_method_override": "pan_fry", "equipment": "pot", "must_differ": ["обжарка фарша в той же кастрюле", "не вторая плита без нужды"]}
  ],
  "addons": [
    {"code": "pork", "title": "Со свининой", "must": ["замена фарша", "71 °C"]},
    {"code": "mixed", "title": "Смешанный фарш", "must": ["говядина+свинина в дельте"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution beef_mince→pork_mince", "equipment skillet→pot"],
  "safety": {"target_note": "фарш 71 °C; high_risk ground_meat"},
  "author_must": ["макароны с количеством", "лук", "не путать с болоньезе (тот — другой slug)"],
  "author_free": ["томатная паста да/нет"],
  "do_not": ["три slug по виду фарша", "сливочный соус из пасты с курицей"]
}
```

---

### 9. `borshch`

```json
{
  "id": "borshch",
  "title": "Борщ",
  "recipe_family": "borshch",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "boil",
  "dish_type": "soup",
  "equipment": "pot",
  "allowed_cuts": ["shank", "brisket", "shoulder"],
  "anchor": "говядина, g, is_anchor",
  "use_cases": ["batch", "budget", "easy"],
  "situations": ["на несколько дней", "есть курица вместо говядины", "без мяса"],
  "equipment_variants": [],
  "addons": [
    {"code": "chicken", "title": "С курицей", "must": ["замена якоря на птицу", "82 °C в куске", "allergen_delta"]},
    {"code": "vegetarian", "title": "Постный", "must": ["убрать мясо", "якорь — свёкла или капуста", "не оставлять beef в составе"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution beef→chicken", "omission мяса"],
  "safety": {"target_note": "говядина варка до мягкости; курица в addon — 82 °C"},
  "author_must": ["свёкла, капуста, томат", "сметана optional true", "не выдумывать «секретный» уксусный градус"],
  "author_free": ["сало/зажарка", "чеснок в конце", "картофель в базе"],
  "do_not": ["три slug борща", "protein_base=vegetables у этого id"]
}
```

Чип книги «птица» этот slug не поймает — это принято: `have=` курица соберёт addon. Отдельный куриный борщ не плодить в волне 1.

---

### 10. `kartofel-po-derevenski`

```json
{
  "id": "kartofel-po-derevenski",
  "title": "Картофель по-деревенски",
  "recipe_family": "roast_potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "картофель, g, is_anchor",
  "use_cases": ["easy", "one_pan", "budget", "fast"],
  "situations": ["гарнир", "нет духовки → сковорода", "аэрогриль на малую порцию"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше грамм", "встряхивание", "время"]},
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["партии", "корочка без сырой середины"]}
  ],
  "addons": [],
  "energy": ["light"],
  "adaptations_hint": ["method oven→air_fryer", "method oven→pan_fry", "omission лишнего масла"],
  "safety": {"target_note": "нет внутренней температуры мяса"},
  "author_must": ["кожура да/нет в шаге", "масло с количеством", "не путать с пюре"],
  "author_free": ["паприка, чеснок, розмарин"],
  "do_not": ["глубокая жарка deep_fry", "мясо в этом slug"]
}
```

---

## Оверлей, не волна: шашлык

Тот же V1 id. Делать, когда оверлей 43 дойдёт до этого файла. Не создавать `shashlyk-iz-svininy`.

```json
{
  "id": "svinoj-shashlyk-v-duhovke-na-shpazhkah",
  "title": "Шашлык из свинины",
  "recipe_family": "shashlyk",
  "stream": "overlay_expand",
  "protein_base": "pork",
  "cook_method": "grill",
  "dish_type": "main",
  "equipment": "grill",
  "allowed_cuts": ["neck", "shoulder"],
  "anchor": "свинина, g, is_anchor",
  "use_cases": ["batch", "budget"],
  "situations": ["мангал = база", "нет мангала → духовка", "мало кусков → сковорода"],
  "equipment_variants": [
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["шпажки над противнем или решётка", "верхний нагрев в конце", "время ~45 мин", "активное меньше, чем на мангале"]
    },
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["куски мельче", "партии", "не перегружать", "стенка короче"]
    }
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method grill→oven", "method grill→pan_fry"],
  "safety": {"target_note": "свинина 63 °C + hold 180 или 71 °C; не 50–55"},
  "author_must": [
    "маринад с количествами в базе",
    "в каждой дельте: размер куска, переворот, режим нагрева",
    "мангал и электрогриль — один grill, разница в notes"
  ],
  "author_free": ["кислота маринада (лук/кефир/уксус) — один канон, не три slug"],
  "do_not": ["второй id духовки", "курица addon", "оставить только духовку как базу"]
}
```

Курица и овощи на шампурах — следующие волны, отдельные slug семьи `shashlyk`.