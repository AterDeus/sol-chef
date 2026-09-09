# Волна 7 — 10 packet’ов (печёные овощи + завтраки)

Человек (чат 2026-09-07): новые slug, не оверлей. Terra не запускать — проверку человек берёт на себя. Автор → `import_draft --check`. Пачки по 10.

Не путать с `zapechennye-ovoshchi` (смесь), `yaichnitsa-s-pomidorami`, `omlet`. High-risk в эту десятку не класть. `editorial_tested` не ставить. Источник: редакция sol-chef, без URL.

Каноны уже в сиде или в `new_ingredients` других черновиков — **переиспользовать**, не плодить синонимы: `pumpkin`, `pumpkin_seeds`, `eggplant`, `beetroot`, `milk`, `feta`, `mozzarella`, `sour_cream`, `cream`, `cottage_cheese`, `eggs`/`egg`, `thyme_or_rosemary`, `balsamic_vinegar`, `bacon`, `yogurt`. Нет в реестре → `new_ingredients` с честными аллергенами. `vegetarian` как `protein_base` запрещён.

---

### 1. `zapechennaya-tykva-s-travami`

```json
{
  "id": "zapechennaya-tykva-s-travami",
  "title": "Запечённая тыква с травами и чесноком",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "тыква, g, is_anchor",
  "use_cases": ["easy", "one_pan", "budget"],
  "situations": ["противень 200 °C", "аэрогриль быстрее корочка", "сковорода: томление под крышкой + финишная обжарка"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше закладка", "время короче ~1.5×", "корочка быстрее"]},
    {"code": "skillet", "title": "На сковороде", "cook_method_override": "pan_fry", "equipment": "skillet", "must_differ": ["крышка", "томление", "финиш без крышки до румянца"]}
  ],
  "addons": [
    {"code": "sweet_honey", "title": "С мёдом и корицей", "add": ["honey", "cinnamon"], "remove": ["garlic", "black_pepper"], "must": ["мёд в последние 5–7 мин, иначе сгорит раньше карамели тыквы"]},
    {"code": "with_feta", "title": "С фетой и семечками", "add": ["feta (на горячую)", "pumpkin_seeds"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method oven→air_fryer", "method oven→pan_fry", "omission лишнего масла"],
  "safety": {"target_note": "нет мяса"},
  "author_must": ["баттернат или мускатная, куски; масло количеством; 200 °C; не путать со смесью zapechennye-ovoshchi"],
  "author_free": ["пикантная с чили и лаймом как 0–1 лишний addon", "бекон вместо сладкого — только если не ломает оси"],
  "do_not": ["второй slug тыквы", "мёд в базе с чесноком", "kcal"]
}
```

---

### 2. `baklazhany-zapechennye-s-syrom`

```json
{
  "id": "baklazhany-zapechennye-s-syrom",
  "title": "Баклажаны, запечённые с томатами и сыром",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "main",
  "equipment": "baking_dish",
  "allowed_cuts": [],
  "anchor": "баклажаны, g, is_anchor",
  "use_cases": ["easy", "one_pan", "budget"],
  "situations": ["форма в духовке, лодочки или веер", "аэрогриль"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["меньше штук", "время короче"]}
  ],
  "addons": [
    {"code": "with_mince", "title": "С мясным фаршем", "add": ["говяжий или куриный фарш, обжаренный"], "must": ["choice_group фарша; температуры SAFETY: говядина 71 °C, птица 74 °C; ground_meat"]},
    {"code": "with_walnuts", "title": "По-грузински с орехами", "add": ["walnuts", "cilantro", "хмели-сунели"], "remove": ["cheese/mozzarella"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method oven→air_fryer"],
  "safety": {"target_note": "фарш только в addon with_mince; база без мяса"},
  "author_must": ["половинки сеткой, чесночное масло, кружки томата, сыр моцарелла или сулугуни (choice_group)", "не путать с baklazhan-s-jogurtovym-sousom"],
  "author_free": ["базилик сушёный vs свежий"],
  "do_not": ["йогуртовый соус в этом id", "protein_base=pork из-за фарша-аддона"]
}
```

---

### 3. `baklazhan-s-jogurtovym-sousom`

```json
{
  "id": "baklazhan-s-jogurtovym-sousom",
  "title": "Баклажан, запечённый с чесночно-йогуртовым соусом",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "баклажаны, g, is_anchor (~500 г, 2 шт)",
  "use_cases": ["easy", "one_pan"],
  "situations": ["круги на противне", "соус отдельно"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_walnuts", "title": "По-грузински с орехами", "replace": ["йогурт → паста из грецкого ореха, чеснока, кинзы и уксуса"], "must": ["фаршируют запечённые круги, не запекают пасту до суха"]},
    {"code": "miso_glaze", "title": "Азиатская мисо-глазурь", "add": ["мисо", "мирин или замена мёд+вода", "soy_sauce"], "remove": ["yogurt"], "must": ["вдоль, сетка, довести под грилем духовки"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution yogurt→walnut paste"],
  "safety": {"target_note": "йогурт не запекать — свернётся"},
  "author_must": ["соль 15–20 мин до запекания (горечь и влага)", "соус отдельно", "зира, лимон, мята или петрушка", "не лодочки с сыром"],
  "author_free": ["аэрогриль 0–1 если честная дельта"],
  "do_not": ["смешивать с baklazhany-zapechennye-s-syrom", "йогурт в духовку"]
}
```

---

### 4. `bryusselskaya-kapusta-s-bekonom`

```json
{
  "id": "bryusselskaya-kapusta-s-bekonom",
  "title": "Брюссельская капуста с беконом и бальзамиком",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "брюссельская капуста, g, is_anchor (~400 г)",
  "use_cases": ["easy", "one_pan"],
  "situations": ["противень, половинки срезом вниз"],
  "equipment_variants": [],
  "addons": [
    {"code": "lenten_nuts", "title": "Постная, с орехами", "remove": ["bacon"], "add": ["walnuts", "honey или кленовый сироп"]},
    {"code": "asian_glaze", "title": "Азиатская глазурь", "add": ["soy_sauce", "honey", "sesame_oil", "sesame"], "must": ["бальзамик убрать или сильно урезать — не два сладких уксуса"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission bacon"],
  "safety": {"target_note": "бекон в базе; не raw_meat"},
  "author_must": ["половинки срезом вниз для Майяра", "бекон ~100 г в базе", "бальзамик 15 мл, чеснок, масло 20 мл"],
  "author_free": ["аэрогриль если честно"],
  "do_not": ["protein_base=pork", "капуста целиком без разреза как единственный способ"]
}
```

---

### 5. `svekla-zapechennaya-s-orehom`

```json
{
  "id": "svekla-zapechennaya-s-orehom",
  "title": "Свёкла, запечённая целиком, с орехом и сыром",
  "recipe_family": "roast_veg",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "свёкла, g, is_anchor (canonical_id beetroot)",
  "use_cases": ["easy", "batch"],
  "situations": ["фольга, целиком, тёплая подача как блюдо"],
  "equipment_variants": [],
  "addons": [
    {"code": "goat_cheese", "title": "С козьим сыром", "replace": ["твёрдый сыр/фета → мягкий козий", "бальзамик → мёд"]},
    {"code": "asian", "title": "Азиатская", "replace": ["орех и сыр → кунжутное масло, соевый соус, зелёный лук"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution cheese"],
  "safety": {"target_note": "tree_nut на базе из-за грецкого"},
  "author_must": ["canonical beetroot; фольга; кожица снимается руками после; не сырой салат и не борщ", "грецкий 40 г, фета или твёрдый 60 г, оливковое, бальзамик, мёд, тимьян"],
  "author_free": ["порции"],
  "do_not": ["свекольный салат без запекания", "борщ"]
}
```

---

### 6. `kartofel-garmoshka`

```json
{
  "id": "kartofel-garmoshka",
  "title": "Картофель «гармошка» с чесночным маслом",
  "recipe_family": "potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "oven",
  "dish_type": "side",
  "equipment": "oven",
  "allowed_cuts": [],
  "anchor": "картофель, g, is_anchor (~600 г, 4 шт)",
  "use_cases": ["easy", "one_pan", "budget"],
  "situations": ["противень, надрезы не до конца на палочках-ограничителях"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_parmesan", "title": "С пармезаном", "add": ["parmesan"], "must": ["сыр в последние ~10 мин"]},
    {"code": "asian_chili", "title": "Острая азиатская", "replace": ["сливочное масло и тимьян → чили-масло + soy_sauce"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution butter→chili oil"],
  "safety": {"target_note": "нет мяса"},
  "author_must": ["hasselback: тонкие надрезы, масло между «страницами»", "чеснок 3 зубчика, слив. масло 40 г, тимьян, соль", "не путать с kartofel-po-derevenski"],
  "author_free": ["аэрогриль на 1–2 клубня если честно"],
  "do_not": ["ломтики деревенского картофеля", "второй slug"]
}
```

---

### 7. `blinchiki-na-moloke`

```json
{
  "id": "blinchiki-na-moloke",
  "title": "Тонкие блинчики на молоке",
  "recipe_family": "blini",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "молоко, ml, is_anchor (~500 мл) либо мука g — один якорь",
  "use_cases": ["fast", "easy", "pantry", "budget"],
  "situations": ["сковорода; первый блин — калибровка"],
  "equipment_variants": [],
  "addons": [
    {"code": "on_kefir", "title": "На кефире", "replace": ["часть молока → кефир + сода"]},
    {"code": "savory_herbs", "title": "Несладкие с зеленью и сыром", "add": ["dill", "hard_cheese в тесто"], "remove": ["sugar"]},
    {"code": "boiling_water", "title": "Заварные ажурные", "replace": ["часть молока → кипяток в замес"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["substitution milk→kefir", "omission sugar"],
  "safety": {"target_note": "сода в выпечке/тесте — scale_mode manual, не gentle"},
  "author_must": ["молоко, мука, яйца, сахар, соль, масло в тесто, сливочное для смазывания стопки", "первый блин пробный", "не перегружать сковороду — по одному"],
  "author_free": ["начинка сёмга/творог — notes, не отдельный slug"],
  "do_not": ["оладьи в этом id", "стакан как unit"]
}
```

---

### 8. `oladi-na-kefire`

```json
{
  "id": "oladi-na-kefire",
  "title": "Пышные оладьи на кефире",
  "recipe_family": "oladi",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "кефир, ml, is_anchor (~300 мл)",
  "use_cases": ["fast", "easy", "budget", "pantry"],
  "situations": ["сковорода под крышкой", "полегче в духовке без масла сковороды"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_apple", "title": "С яблочным припёком", "add": ["apple кубик или тёртые"]},
    {"code": "with_green_onion", "title": "Несладкие с зелёным луком", "add": ["green_onion"], "remove": ["sugar"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven"],
  "safety": {"target_note": "сода manual; жарить сразу после замеса"},
  "author_must": ["тёплый кефир, сода в последний момент, не мешать после подхода, жарить под крышкой", "мука ~250 г, яйцо, сахар ~30 г, сода 0.5 ч.л.", "energy light = духовка на пергаменте, cook_method_override=oven, без масла сковороды"],
  "author_free": ["тыквенное пюре без сахара как 0–1 addon"],
  "do_not": ["блины в этом id", "перемешивать подошедшее тесто"]
}
```

---

### 9. `draniki`

```json
{
  "id": "draniki",
  "title": "Драники",
  "recipe_family": "potato",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "картофель, g, is_anchor (~500 г)",
  "use_cases": ["easy", "budget", "one_pan"],
  "situations": ["сковорода, тёртая масса"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_mushrooms", "title": "С грибами внутри", "add": ["champignons обжаренные в середину"]},
    {"code": "with_meat", "title": "Белорусские с мясом", "add": ["тушёный фарш между двумя тонкими слоями"], "must": ["ground_meat; фарш говядина/свинина 71 °C"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission mushrooms"],
  "safety": {"target_note": "грибы whitelist шампиньоны; фарш только addon"},
  "author_must": ["отжать жидкость из тёртого картофеля", "лук ~100 г, яйцо, мука 2 ст.л., сметана к подаче optional", "не путать с zharenaya-kartoshka-s-lukom (там ломтики)"],
  "author_free": ["порции"],
  "do_not": ["ломтевая жареная картошка", "лесные грибы"]
}
```

---

### 10. `skrembl-na-slivochnom-masle`

```json
{
  "id": "skrembl-na-slivochnom-masle",
  "title": "Идеальный кремовый скрэмбл",
  "recipe_family": "eggs",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "dish_type": "breakfast",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "яйца, pcs — servings обязателен если якорь не в г/мл",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["слабый огонь, сдвигать лопаткой, снять полуглянцевыми"],
  "equipment_variants": [],
  "addons": [
    {"code": "extra_creamy", "title": "Сливочный", "add": ["cottage_cheese или жирная сметана в конце"]},
    {"code": "with_spinach_tomato", "title": "С томатами и шпинатом", "add": ["шпинат свежий", "помидоры черри"]}
  ],
  "energy": ["rich"],
  "adaptations_hint": ["omission pepper"],
  "safety": {"target_note": "яйца полностью снимать до резины, но не сырой желток как блюдо; не raw_egg"},
  "author_must": ["яйца, сливочное масло, соль, перец", "вилкой без пены, слабый огонь, остаточное тепло на тарелке", "energy rich: бекон или слабосолёный лосось (choice_group)", "не омлет и не яичница с помидорами"],
  "author_free": ["порции 2"],
  "do_not": ["взбивать в пену как омлет", "высокий огонь"]
}
```
