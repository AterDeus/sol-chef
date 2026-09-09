# Волна 8 — 10 packet’ов (завтраки остаток + десерты + огурцы)

После волны 7. Terra не запускать. Автор → `import_draft --check`.

Не путать с `omlet`, `yaichnitsa-s-pomidorami`, `pshennaya-kasha`, `shokoladnyy-fondan`. `vegetarian` как protein_base запрещён. Переиспользовать каноны: `milk`, `apple`, `pumpkin`, `sour_cream`, `cream`, `cottage_cheese`, `sesame`, `sesame_oil`, `cucumber`, `soy_sauce`, `garlic`, `chili_flakes`, `cinnamon`, `honey`, `walnuts`, `dark_chocolate`.

---

### 1. `yaichnitsa-glazunya`

```json
{
  "id": "yaichnitsa-glazunya",
  "title": "Яичница-глазунья с кружевными краями",
  "recipe_family": "eggs",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "servings обязателен (яйца pcs)",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["раскалённое растительное масло, кружево белка, желток живой"],
  "equipment_variants": [],
  "addons": [
    {"code": "asian", "title": "Азиатская", "add": ["soy_sauce", "sesame_oil", "green_onion"]},
    {"code": "khai_dao", "title": "Тайская khai dao", "add": ["жареный лук-шалот", "chili oil"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "не raw_egg: белок готов, желток может быть жидким — caution не нужен если не сырое блюдо; не путать с омлетом"},
  "author_must": ["яйца 2–3 шт, раст. масло ~25 мл, соль", "не сливочное — нужна высокая температура дымления", "не yaichnitsa-s-pomidorami"],
  "author_free": [],
  "do_not": ["помидоры в базе", "сливочное масло как жир жарки"]
}
```

---

### 2. `ovsyanaya-kasha-bazovaya`

```json
{
  "id": "ovsyanaya-kasha-bazovaya",
  "title": "Овсяная каша долгой варки",
  "recipe_family": "kasha",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "boil",
  "dish_type": "breakfast",
  "equipment": "saucepan",
  "allowed_cuts": [],
  "anchor": "овсяные хлопья, g, is_anchor (~60 г на порцию или больше на кастрюлю)",
  "use_cases": ["easy", "pantry", "budget"],
  "situations": ["сотейник 15–20 мин, 1:3 жидкость, масло в конце с огня"],
  "equipment_variants": [],
  "addons": [
    {"code": "sweet_banana_berry", "title": "Ягодная с бананом", "add": ["банан", "замороженные ягоды", "honey"]},
    {"code": "savory_cheese", "title": "Солёная с сыром и пашотом", "add": ["hard_cheese", "яйцо пашот", "green_onion"], "remove": ["sugar"]},
    {"code": "congee", "title": "Конге-стиль", "replace": ["молоко → куриный бульон"], "add": ["яйцо всмятку", "soy_sauce", "shallot жареный"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["omission milk", "omission butter"],
  "safety": {"target_note": "пашот/всмятку — не raw_egg если белок схвачен; бульон магазинный — celery unknown на каноне бульона"},
  "author_must": ["геркулес, вода+молоко, масло в конце monter, соль, щепотка сахара", "energy light: убрать milk и butter, только вода", "не пшёнка"],
  "author_free": ["кастрюля vs сотейник — база saucepan"],
  "do_not": ["быстрая овсянка 3 мин как единственный способ", "protein_base=vegetarian"]
}
```

---

### 3. `bananovoe-ovsyanoe-pechene`

```json
{
  "id": "bananovoe-ovsyanoe-pechene",
  "title": "Банановое овсяное печенье",
  "recipe_family": "cookies",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "dessert",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "бананы, g, is_anchor",
  "use_cases": ["easy", "pantry", "budget"],
  "situations": ["противень; аэрогриль 6 шт 8–10 мин"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["порция ~6 шт", "8–10 мин"]}
  ],
  "addons": [
    {"code": "with_chocolate_nuts", "title": "С шоколадом и орехами", "add": ["dark_chocolate", "walnuts"]},
    {"code": "with_cranberry_coconut", "title": "С клюквой и кокосом", "add": ["сушёная клюква", "кокосовая стружка"]}
  ],
  "energy": [],
  "adaptations_hint": ["method oven→air_fryer"],
  "safety": {"target_note": "без яиц и пшеницы в базе — не вешать gluten/egg на канон овса зря; овёс may_contain gluten если не указано иначе — unknown gluten на овсяных хлопьях честно"},
  "author_must": ["спелые бананы с точками, хлопья быстрого/среднего, корица, щепотка соли", "без сахара и муки в базе"],
  "author_free": [],
  "do_not": ["пшеничная мука в базе", "яйцо в базе"]
}
```

---

### 4. `pirozhnoe-kartoshka`

```json
{
  "id": "pirozhnoe-kartoshka",
  "title": "Пирожное «Картошка»",
  "recipe_family": "no_bake_dessert",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "no_cook",
  "dish_type": "dessert",
  "equipment": "",
  "allowed_cuts": [],
  "anchor": "печенье, g, is_anchor (~300 г)",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["миска, холодильник 15+ мин"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_walnut_center", "title": "С орехом внутри", "add": ["walnuts половинки"]},
    {"code": "white_coconut", "title": "Белая в кокосе", "add": ["кокосовая стружка"], "remove": ["cocoa"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["omission cocoa"],
  "safety": {"target_note": "коньяк optional в notes, не обязателен; gluten+milk+egg с печенья — unknown egg если состав Юбилейного неизвестен, contains gluten milk с канона печенья"},
  "author_must": ["песочное печенье крошка с кусочками не пыль, сгущёнка, масло, какао, ваниль", "energy light: рикотта + банан вместо сгущёнки и части масла", "equipment пустой у no_cook"],
  "author_free": ["коньяк в notes"],
  "do_not": ["духовка", "equipment=pot"]
}
```

---

### 5. `limonnyy-ekspress-krem`

```json
{
  "id": "limonnyy-ekspress-krem",
  "title": "Лимонный экспресс-крем",
  "recipe_family": "no_bake_dessert",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "no_cook",
  "dish_type": "dessert",
  "equipment": "",
  "allowed_cuts": [],
  "anchor": "сгущённое молоко, g, is_anchor (~200 г или банка с граммовкой)",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["сок струйкой при взбивании, 3–5 мин"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_cookie_crust", "title": "В стаканчиках с крошкой", "add": ["песочное печенье на дно"]},
    {"code": "lime_twist", "title": "Лаймовый", "replace": ["лимон → лайм + мята"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["substitution lemon→lime"],
  "safety": {"target_note": "не желатин; сгущёнка не варёная"},
  "author_must": ["сгущёнка, сок и цедра лимона, сметана или сливки 33%", "сок тонкой струйкой иначе комки", "energy light: сливки 33% + мёд, без коагуляции казеина — другая текстура, честно в дельте"],
  "author_free": ["масло 30 г optional"],
  "do_not": ["варка", "желатин", "варёная сгущёнка"]
}
```

---

### 6. `yablochnyy-krambl`

```json
{
  "id": "yablochnyy-krambl",
  "title": "Яблочный крамбл",
  "recipe_family": "crumble",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "dessert",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "яблоки, g, is_anchor",
  "use_cases": ["easy", "one_pan", "budget"],
  "situations": ["форма; аэрогриль в рамекинах"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["рамекины", "меньше порция"]}
  ],
  "addons": [
    {"code": "with_berries", "title": "С ягодами", "add": ["вишня или чёрная смородина к яблокам"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method oven→air_fryer"],
  "safety": {"target_note": "эритрит/топинамбур в light — new_ingredients; масло −30%"},
  "author_must": ["кисло-сладкие яблоки, холодное масло, овсяные хлопья, мука, сахар или мёд, корица", "не месить тесто"],
  "author_free": [],
  "do_not": ["дрожжевое тесто", "пирог с решёткой как база"]
}
```

---

### 7. `pesochnoe-pechene`

```json
{
  "id": "pesochnoe-pechene",
  "title": "Песочное печенье",
  "recipe_family": "cookies",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "oven",
  "dish_type": "dessert",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "мука, g, is_anchor (300 г)",
  "use_cases": ["easy", "pantry", "batch"],
  "situations": ["противень, тесто охладить"],
  "equipment_variants": [],
  "addons": [
    {"code": "no_sugar_dates", "title": "Без сахара", "replace": ["пудра → финиковая паста ~100 г + корица"]},
    {"code": "matcha_white_choc", "title": "С матча и белым шоколадом", "add": ["матча часть муки", "белый шоколад"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution sugar→date paste"],
  "safety": {"target_note": "сода нет; не месить клейковину"},
  "author_must": ["мука:масло:пудра 3:2:1 по весу (300/200/100), соль, ваниль optional", "охладить тесто", "scale_mode муки linear, разрыхлителя нет"],
  "author_free": [],
  "do_not": ["долго месить", "яйцо если не нужно для 5 ингредиентов"]
}
```

---

### 8. `yabloki-zapechennye-s-myodom`

```json
{
  "id": "yabloki-zapechennye-s-myodom",
  "title": "Запечённые яблоки с мёдом и орехами",
  "recipe_family": "baked_fruit",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "dessert",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "яблоки, g или pcs+servings; якорь в g предпочтителен",
  "use_cases": ["easy", "one_pan", "light"],
  "situations": ["противень, мёд после выпечки"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_tvorog", "title": "С творогом внутри", "add": ["cottage_cheese", "яйцо в начинку"]},
    {"code": "asian", "title": "Анисово-имбирная", "replace": ["корица → бадьян и имбирь, кленовый + капля soy_sauce"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "мёд не до выпечки — подгорит"},
  "author_must": ["4 кисло-сладких, мёд 40 г после, грецкий 30 г, корица, масло 10 г"],
  "author_free": [],
  "do_not": ["мёд с начала выпечки", "крамбл в этом id"]
}
```

---

### 9. `finikovye-shariki`

```json
{
  "id": "finikovye-shariki",
  "title": "Финиковые шарики без выпечки",
  "recipe_family": "no_bake_dessert",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "no_cook",
  "dish_type": "dessert",
  "equipment": "",
  "allowed_cuts": [],
  "anchor": "финики, g, is_anchor (~200 г)",
  "use_cases": ["fast", "easy", "pantry", "light"],
  "situations": ["миска, без муки и яиц"],
  "equipment_variants": [],
  "addons": [
    {"code": "peanut_oats", "title": "С арахисовой пастой и овсянкой", "add": ["арахисовая паста", "овсяные хлопья"]},
    {"code": "tahini_miso", "title": "С тахини и мисо", "replace": ["какао → тахини + капля белого мисо"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "tree_nut; арахис peanut в addon; кунжут в тахини"},
  "author_must": ["финики без косточек 200 г, орехи 100 г, какао 20 г, кокос 30 г, соль", "equipment пустой"],
  "author_free": [],
  "do_not": ["духовка", "сахар в базе"]
}
```

---

### 10. `bitye-ogurtsy-po-aziatski`

```json
{
  "id": "bitye-ogurtsy-po-aziatski",
  "title": "«Битые» огурцы по-азиатски",
  "recipe_family": "asian_cold",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "no_cook",
  "dish_type": "salad",
  "equipment": "",
  "allowed_cuts": [],
  "anchor": "огурцы, g, is_anchor",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["плющить ножом/скалкой, маринад 10 мин"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_sesame_cilantro", "title": "С кунжутом и кинзой", "add": ["sesame", "cilantro"]},
    {"code": "with_peanuts", "title": "С арахисом", "add": ["жареный арахис дроблёный"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "soy, sesame в масле/кунжуте; peanut в addon; gluten с пшеничного соевого"},
  "author_must": ["пупырчатые огурцы, soy_sauce, чеснок, рисовый или яблочный уксус (apple_cider_vinegar есть), масло раст. или кунжутное, соль, chili_flakes", "не часами мариновать"],
  "author_free": [],
  "do_not": ["варёные огурцы", "equipment=bowl выдумывать — пустое поле"]
}
```
