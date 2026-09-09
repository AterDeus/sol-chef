# Волна 9 — 10 packet’ов (азия, грибы, морепродукты)

После волны 8. Terra не запускать. Автор → `import_draft --check`.

Закрывает пустые чипы `mushrooms` и `seafood`. Другой белок ≠ addon: том ям — курица; креветки том яма не этот slug. Гюдон (говядина) не addon оякодона. `vegetarian` запрещён. Каноны: `chicken_thighs`, `chicken_breast`, `pork_neck`, `champignons`, `soy_sauce`, `sesame`, `sesame_oil`, `ginger`, `garlic`, `rice`, `corn_starch`, `egg`, `bell_pepper`, `green_onion`, `honey`, `chili`, `chili_flakes`, `lemon`, `cilantro`, `cream`, `tomato`.

---

### 1. `yajtsa-mayak-po-korejski`

```json
{
  "id": "yajtsa-mayak-po-korejski",
  "title": "Яйца «Маяк» по-корейски",
  "recipe_family": "asian_eggs",
  "stream": "wave",
  "protein_base": "eggs_dairy",
  "cook_method": "boil",
  "dish_type": "appetizer",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "servings обязателен (яйца pcs)",
  "use_cases": ["batch", "pantry", "easy"],
  "situations": ["варка 6 мин, лёд, маринад в контейнере 4–6 ч"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_ginger", "title": "С имбирём и кинзой", "add": ["ginger", "cilantro"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "всмятку, не raw_egg; не флаг preservation — холодильник на дни, не банка"},
  "author_must": ["яйца, soy_sauce, вода, сахар или мёд, green_onion, garlic, sesame, перец по вкусу", "соус без варки"],
  "author_free": ["рис к подаче в notes"],
  "do_not": ["high_risk preservation", "вкрутую как база"]
}
```

---

### 2. `zharenyy-tofu-v-souse`

```json
{
  "id": "zharenyy-tofu-v-souse",
  "title": "Жареный тофу в кисло-сладком соевом соусе",
  "recipe_family": "tofu",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "тофу, g, is_anchor",
  "use_cases": ["fast", "easy", "budget", "one_pan"],
  "situations": ["отжать, крахмал, глазурь; аэрогриль без масла"],
  "equipment_variants": [
    {"code": "air_fryer", "title": "В аэрогриле", "cook_method_override": "air_fryer", "must_differ": ["без масла жарки", "хруст от воздуха"]}
  ],
  "addons": [
    {"code": "with_vegetables", "title": "С овощами", "add": ["bell_pepper", "стручковая фасоль"]}
  ],
  "energy": [],
  "adaptations_hint": ["method pan_fry→air_fryer"],
  "safety": {"target_note": "soy; не перегружать сковороду"},
  "author_must": ["плотный тофу, corn_starch, масло, soy, honey/сахар, garlic, green_onion"],
  "author_free": [],
  "do_not": ["protein_base=vegetarian", "мягкий тофу как база"]
}
```

---

### 3. `oyakodon`

```json
{
  "id": "oyakodon",
  "title": "Оякодон",
  "recipe_family": "donburi",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["thigh"],
  "anchor": "куриное бедро, g, is_anchor (~200 г)",
  "use_cases": ["fast", "easy", "one_pan"],
  "situations": ["соево-мириновый бульон, яйцо с остаточным теплом на рис"],
  "equipment_variants": [],
  "addons": [
    {"code": "vegetarian_tofu", "title": "С тофу и шиитаке", "replace": ["курица → тофу + шиитаке"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution chicken→tofu"],
  "safety": {"target_note": "бедро 82 °C до яйца; poultry_temp; яйцо кремовое не raw_egg"},
  "author_must": ["бедро 200 г, лук, яйца 2–3, soy 30 мл, мирин или мёд+вода, рис 300 г, green_onion", "снять раньше полного схватывания"],
  "author_free": [],
  "do_not": ["addon с говядиной (другой protein_base)", "грудка вместо бедра в базе"]
}
```

---

### 4. `kuritsa-teriyaki-na-skovorode`

```json
{
  "id": "kuritsa-teriyaki-na-skovorode",
  "title": "Курица терияки на сковороде",
  "recipe_family": "teriyaki",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["thigh"],
  "anchor": "куриные бёдра с кожей, g, is_anchor (~400 г)",
  "use_cases": ["fast", "easy", "one_pan"],
  "situations": ["кожа вниз, соус nappe отдельно, глазурь в последнюю минуту"],
  "equipment_variants": [],
  "addons": [
    {"code": "mala", "title": "Мала-терияки", "add": ["сычуаньский перец", "чили в глазури"]},
    {"code": "honey_mustard", "title": "Медово-горчичная", "replace": ["соевый профиль → дижон + мёд, та же техника глазури"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "бедро 82 °C у кости; poultry_temp; сахар не раньше мяса"},
  "author_must": ["бёдра 400 г, soy 60 мл, мирин 40 мл, сахар 10 г, garlic, ginger, sesame", "не перегружать сковороду"],
  "author_free": [],
  "do_not": ["глазурь с начала жарки", "грудка как база"]
}
```

---

### 5. `svinina-v-kislo-sladkom-souse`

```json
{
  "id": "svinina-v-kislo-sladkom-souse",
  "title": "Свинина в кисло-сладком соусе",
  "recipe_family": "sweet_sour",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["neck", "shoulder"],
  "anchor": "свинина, g, is_anchor (~350 г)",
  "use_cases": ["fast", "easy", "one_pan"],
  "situations": ["крахмал, корочка, соус отдельно, смешать перед подачей"],
  "equipment_variants": [],
  "addons": [
    {"code": "spicy", "title": "Острая без ананаса", "add": ["chili_flakes", "garlic"], "must": ["сладость ниже"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "цельный кусок 63 °C + hold 180 или 71 °C; не перегружать сковороду"},
  "author_must": ["свинина 350 г, corn_starch 40 г, яйцо, bell_pepper, кетчуп 60 г, рисовый уксус 20 мл, сахар 20 г, soy 15 мл", "только addon spicy; курица — не этот id"],
  "author_free": ["ананас не обязателен"],
  "do_not": ["addon с курицей", "смешивать соус с корочкой заранее"]
}
```

---

### 6. `miso-sup-s-tofu`

```json
{
  "id": "miso-sup-s-tofu",
  "title": "Мисо-суп с тофу и вакаме",
  "recipe_family": "miso_soup",
  "stream": "wave",
  "protein_base": "legumes",
  "cook_method": "boil",
  "dish_type": "soup",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "вода или даси, ml, is_anchor (~500 мл) либо тофу g — один якорь",
  "use_cases": ["fast", "easy", "pantry"],
  "situations": ["мисо не кипятить"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_chicken_mushrooms", "title": "С курицей и грибами", "add": ["chicken_breast", "шиитаке"], "must": ["грудь 72 °C"]},
    {"code": "la_yu", "title": "Острый, ла-ю", "add": ["чили-масло в конце"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "soy; шиитаке whitelist; бульон даси — рыба unknown/contains на каноне если рыбный"},
  "author_must": ["мисо 40 г, вода/даси 500 мл, тофу 100 г, вакаме 5 г, green_onion", "мисо развести тёплым и вмешать вне огня"],
  "author_free": [],
  "do_not": ["кипятить мисо", "казан ради ряда"]
}
```

---

### 7. `tom-yam-s-kuritsey`

```json
{
  "id": "tom-yam-s-kuritsey",
  "title": "Том ям с курицей",
  "recipe_family": "tom_yam",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "boil",
  "dish_type": "soup",
  "equipment": "pot",
  "allowed_cuts": ["breast", "thigh"],
  "anchor": "курица, g, is_anchor (~250 г)",
  "use_cases": ["easy"],
  "situations": ["лемонграсс/галангал/чили выварить и вынуть"],
  "equipment_variants": [],
  "addons": [
    {"code": "tom_kha", "title": "Том кха", "add": ["кокосовое молоко в конце"], "must": ["не кипятить после молока"]},
    {"code": "with_tofu", "title": "Постная с тофу", "replace": ["курица → тофу", "бульон овощной", "шиитаке"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution chicken→tofu"],
  "safety": {"target_note": "грудь 72 / бедро 82; fish sauce = fish; креветки не addon (seafood = другой slug)"},
  "author_must": ["курица 250 г, бульон 600 мл, лемонграсс, лайм, рыбный соус 30 мл, чили, champignons 100 г, кинза", "ароматические стебли вынуть"],
  "author_free": ["галангал или имбирь"],
  "do_not": ["креветки в этом id", "кипятить кокос в tom_kha"]
}
```

---

### 8. `mapo-tofu`

```json
{
  "id": "mapo-tofu",
  "title": "Мапо тофу",
  "recipe_family": "mapo",
  "stream": "wave",
  "protein_base": "pork",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": ["mince"],
  "anchor": "тофу мягкий, g, is_anchor (~300 г) — если якорь тофу, фарш тоже в граммах",
  "use_cases": ["fast", "one_pan"],
  "situations": ["доубаньцзян и сычуань в масле первыми; тофу не мешать ложкой"],
  "equipment_variants": [],
  "addons": [
    {"code": "vegetarian_mushrooms", "title": "Вегетарианская", "replace": ["фарш → рубленые шиитаке, вода замачивания в бульон"]},
    {"code": "no_mala", "title": "Без мала", "remove": ["сычуаньский перец"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission sichuan pepper", "substitution pork mince→shiitake"],
  "safety": {"target_note": "фарш 71 °C; ground_meat; шиитаке whitelist"},
  "author_must": ["мягкий тофу 300 г, свиной фарш 150 г, доубаньцзян 30 г, сычуань 2 г, garlic, ginger, corn_starch, бульон 150 мл", "покачивать сковороду"],
  "author_free": [],
  "do_not": ["мешать тофу ложкой", "лесные грибы"]
}
```

---

### 9. `zharenye-shampinony-s-chesnokom`

```json
{
  "id": "zharenye-shampinony-s-chesnokom",
  "title": "Жареные шампиньоны с чесноком и петрушкой",
  "recipe_family": "mushrooms",
  "stream": "wave",
  "protein_base": "mushrooms",
  "cook_method": "pan_fry",
  "dish_type": "side",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "шампиньоны, g, is_anchor",
  "use_cases": ["fast", "easy", "one_pan", "pantry"],
  "situations": ["сухая раскалённая сковорода до румянца, потом масло"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_sour_cream_cheese", "title": "А-ля жульен на сковороде", "add": ["sour_cream", "hard_cheese"]},
    {"code": "with_soy_thyme", "title": "С соевым и тимьяном", "add": ["soy_sauce", "thyme"]}
  ],
  "energy": [],
  "adaptations_hint": [],
  "safety": {"target_note": "только шампиньоны whitelist; не wild_mushrooms"},
  "author_must": ["champignons, butter + vegetable_oil, garlic, parsley, salt, pepper", "сначала без масла в один слой, не перегружать"],
  "author_free": [],
  "do_not": ["лесные грибы", "protein_base=vegetables"]
}
```

---

### 10. `krevetki-v-chesnochnom-masle`

```json
{
  "id": "krevetki-v-chesnochnom-masle",
  "title": "Чесночные креветки на сковороде",
  "recipe_family": "shrimp",
  "stream": "wave",
  "protein_base": "seafood",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "allowed_cuts": [],
  "anchor": "креветки, g, is_anchor",
  "use_cases": ["fast", "easy", "one_pan"],
  "situations": ["1–1.5 мин сторона, лимон в конце"],
  "equipment_variants": [
    {"code": "grill", "title": "На шпажках на гриле", "cook_method_override": "grill", "equipment": "grill", "must_differ": ["шпажки", "переворот", "не таймер сковороды"]}
  ],
  "addons": [
    {"code": "creamy_tomato", "title": "В сливочно-томатном соусе", "add": ["cream 20%", "томаты в с/с"]}
  ],
  "energy": [],
  "adaptations_hint": ["method pan_fry→grill", "equipment skillet→grill"],
  "safety": {"target_note": "crustacean; варёно-мороженые только прогреть, сыромороженые до непрозрачности; не fish"},
  "author_must": ["креветки, butter, olive_oil, garlic, лимон сок+цедра, parsley, chili_flakes", "порции на сковороде"],
  "author_free": [],
  "do_not": ["protein_base=fish_white_sea", "варить 10 минут"]
}
```
