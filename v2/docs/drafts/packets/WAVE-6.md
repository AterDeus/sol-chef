# Волна 6 — 5 packet’ов (крупы/паста остаток, щи, салат)

Последняя пачка новых slug. После волны 5. Всего с волнами 1–6: **55**.

---

### 1. `perlovka-s-gribami`

```json
{
  "id": "perlovka-s-gribami",
  "title": "Перловка с грибами и луком",
  "recipe_family": "kasha",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "boil",
  "dish_type": "pasta_grains",
  "equipment": "pot",
  "allowed_cuts": [],
  "anchor": "перловка, g, is_anchor",
  "use_cases": ["budget", "batch", "pantry"],
  "situations": ["кастрюля долго", "духовка довести", "казан"],
  "equipment_variants": [
    {"code": "oven", "title": "В духовке", "cook_method_override": "oven", "equipment": "oven", "must_differ": ["после закипания на плите или запекание с жидкостью"]},
    {"code": "kazan", "title": "В казане", "cook_method_override": "stew", "equipment": "kazan", "must_differ": ["томление"]}
  ],
  "addons": [],
  "energy": [],
  "adaptations_hint": ["method boil→oven", "equipment pot→kazan"],
  "safety": {"target_note": "грибы whitelist"},
  "author_must": ["замачивание prep или долгая варка", "шампиньоны лук"],
  "author_free": ["морковь"],
  "do_not": ["гречка V1"]
}
```

---

### 2. `pasta-s-kuritsey-v-slivkah`

```json
{
  "id": "pasta-s-kuritsey-v-slivkah",
  "title": "Паста с курицей в сливочном соусе",
  "recipe_family": "pasta",
  "stream": "wave",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "dish_type": "pasta_grains",
  "equipment": "skillet",
  "allowed_cuts": ["breast"],
  "anchor": "куриная грудка, g, is_anchor — или паста g; один якорь, лучше курица",
  "use_cases": ["fast", "easy"],
  "situations": ["сковорода + кастрюля для пасты", "запеканка"],
  "equipment_variants": [
    {"code": "oven", "title": "Запеканка", "cook_method_override": "oven", "equipment": "baking_dish", "must_differ": ["собрать отваренную пасту в форму", "сыр"]}
  ],
  "addons": [
    {"code": "with_mushrooms", "title": "С грибами", "must": ["whitelist"]},
    {"code": "tomato", "title": "С томатным соусом", "must": ["сливки убрать или уменьшить", "томат"]}
  ],
  "energy": ["light"],
  "adaptations_hint": ["method pan_fry→oven", "omission mushrooms"],
  "safety": {"target_note": "грудка 72 °C"},
  "author_must": ["паста g, сливки ml", "не флотские и не болоньезе"],
  "author_free": ["пармезан optional"},
  "do_not": ["aglio e olio V1"]
}
```

---

### 3. `makarony-s-myasnym-sousom`

```json
{
  "id": "makarony-s-myasnym-sousom",
  "title": "Макароны с мясным соусом",
  "recipe_family": "pasta_mince",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "stew",
  "dish_type": "pasta_grains",
  "equipment": "pot",
  "allowed_cuts": ["mince"],
  "anchor": "говяжий фарш, g, is_anchor",
  "use_cases": ["budget", "easy", "batch"],
  "situations": ["соус в кастрюле", "свинина", "без мяса"],
  "equipment_variants": [],
  "addons": [
    {"code": "pork", "title": "Со свининой", "must": ["replace фарша", "71 °C"]},
    {"code": "mixed", "title": "Смешанный фарш", "must": ["две строки или replace mix"]},
    {"code": "vegetarian", "title": "Без мяса", "must": ["убрать фарш", "якорь паста или чечевица/овощи", "не оставлять beef"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution beef_mince→pork_mince", "omission мяса"],
  "safety": {"target_note": "фарш 71 °C; ground_meat на мясных addon"},
  "author_must": ["томат ml, лук, паста g", "не флотские (жареные макароны с фаршем — волна 1)"],
  "author_free": ["морковь сельдерей — сельдерей unknown если магазинный"],
  "do_not": ["название болоньезе обязательно", "три slug"]
}
```

---

### 4. `shchi-iz-svezhey-kapusty`

```json
{
  "id": "shchi-iz-svezhey-kapusty",
  "title": "Щи из свежей капусты",
  "recipe_family": "shchi",
  "stream": "wave",
  "protein_base": "beef",
  "cook_method": "boil",
  "dish_type": "soup",
  "equipment": "pot",
  "allowed_cuts": ["shank", "brisket", "shoulder"],
  "anchor": "говядина, g, is_anchor",
  "use_cases": ["batch", "budget", "easy"],
  "situations": ["мясные", "без мяса"],
  "equipment_variants": [],
  "addons": [
    {"code": "vegetarian", "title": "Без мяса", "must": ["убрать говядину", "якорь капуста", "грибы optional whitelist"]}
  ],
  "energy": [],
  "adaptations_hint": ["omission мяса"],
  "safety": {"target_note": "мясо сварить до мягкости"},
  "author_must": ["капуста картофель морковь томат", "сметана optional", "не борщ волны 1"],
  "author_free": ["лавровый"],
  "do_not": ["квашеная как обязательная база — свежая в title"]
}
```

---

### 5. `ovoshchnoy-salat`

```json
{
  "id": "ovoshchnoy-salat",
  "title": "Овощной салат с огурцами и помидорами",
  "recipe_family": "salad",
  "stream": "wave",
  "protein_base": "vegetables",
  "cook_method": "no_cook",
  "dish_type": "salad",
  "equipment": null,
  "allowed_cuts": [],
  "anchor": "помидоры или огурцы g — один якорь, второй linear",
  "use_cases": ["fast", "easy", "pantry", "light"],
  "situations": ["без огня", "сыр", "яйцо", "сметана или масло"],
  "equipment_variants": [],
  "addons": [
    {"code": "with_cheese", "title": "С сыром", "must": ["сыр g"]},
    {"code": "with_egg", "title": "С яйцом", "must": ["яйца варёные pcs — варка яйца в prep или шаг без плиты салата: сварить отдельно в шаге ок"]},
    {"code": "sour_cream", "title": "Со сметаной", "must": ["если база масло — заменить/добавить"]}
  ],
  "energy": [],
  "adaptations_hint": ["substitution oil→sour_cream осторожно"],
  "safety": {"target_note": "яйцо в addon варёное; не raw_egg"},
  "author_must": ["огурец помидор лук, масло в базе", "соль gentle"],
  "author_free": ["укроп"],
  "do_not": ["салат с грецкими орехами V1", "винегрет"]
}
```

`equipment` пустой у `no_cook`. Ключ не писать или `null` — как примет валидатор (часто ключа нет).
