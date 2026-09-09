# Пачка 1 — гриль, стейки, шашлык, рёбра

Старт: **«стартуй оверлей осей 1»**. Правила: [OVERLAY-AXES.md](OVERLAY-AXES.md). Эталон дельты гриль↔духовка: `svinye-rebra.json`.

Источник: текущий `drafts/recipes/<id>.json`. Базу не ломать, кроме шашлыка (там смена базы по WAVE-1).

---

### `govyazhi-rebra-mangal-bez-folgi-perets`

Черновик **уже** содержит `equipment` oven + три addon-соуса `has_delta=false`. Автор: **переписать соусы в addon с дельтой** (ингредиенты соуса + шаг подачи) или убрать legacy. Духовку проверить: 150 °C, решётка над водой, без гриль-режима на финале, 90–94 °C.

```json
{
  "id": "govyazhi-rebra-mangal-bez-folgi-perets",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "grill",
  "equipment": "grill",
  "allowed_cuts": ["ribs"],
  "equipment_variants": [
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["150 °C", "решётка над противнем с водой", "без фольги на цикле", "не режим гриль на финале", "сбрызгивание чаще"]
    }
  ],
  "addons": [
    {"code": "mustard_sauce", "title": "Горчичный соус", "has_delta": true, "must": "соус в ингредиентах и шаге подачи, не мазать до готовки"},
    {"code": "herb_oil", "title": "Зелёное масло", "has_delta": true},
    {"code": "pickle_relish", "title": "Огуречный релиш", "has_delta": true}
  ],
  "adaptations_hint": ["equipment grill→oven", "method grill→oven"],
  "safety": {"target_note": "говяжьи рёбра 90–94 °C, кость шатается"},
  "do_not": ["legacy_text", "сахар в натир", "прямой жар"]
}
```

---

### `govyazhi-rebra-mangal-folga-soja-med`

```json
{
  "id": "govyazhi-rebra-mangal-folga-soja-med",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "grill",
  "equipment": "grill",
  "allowed_cuts": ["ribs"],
  "equipment_variants": [
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["фольга в форме", "температура камеры", "глазурь мёд/соя только на финише открытыми", "время стенки ≠ мангал"]
    }
  ],
  "addons": [],
  "adaptations_hint": ["equipment grill→oven", "method grill→oven"],
  "safety": {"target_note": "мягкость + шатающаяся кость; мёд не жечь"},
  "do_not": ["открытый гриль на весь цикл", "второй slug"]
}
```

---

### `svinoj-shashlyk-v-duhovke-na-shpazhkah`

Как [WAVE-1.md](WAVE-1.md) § оверлей. Сейчас база — духовка. **Сделать базу `grill` + `equipment=grill`**, духовку и сковороду — вариантами. `id` не менять. Title можно «Шашлык из свинины», если уже так.

```json
{
  "id": "svinoj-shashlyk-v-duhovke-na-shpazhkah",
  "stream": "overlay_expand",
  "protein_base": "pork",
  "cook_method": "grill",
  "equipment": "grill",
  "allowed_cuts": ["neck", "shoulder"],
  "equipment_variants": [
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["шпажки над противнем или решётка", "верхний нагрев в конце", "время"]
    },
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["куски мельче", "партии", "не перегружать"]
    }
  ],
  "adaptations_hint": ["method grill→oven", "method grill→pan_fry"],
  "safety": {"target_note": "свинина 63 °C + hold 180 или 71 °C"},
  "do_not": ["новый slug", "курица addon", "оставить только духовку как базу", "мангал и электрогриль как два метода"]
}
```

---

### `stejk-na-grile`

```json
{
  "id": "stejk-na-grile",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "grill",
  "equipment": "grill",
  "allowed_cuts": ["ribeye", "striploin", "tenderloin"],
  "equipment_variants": [
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["раскалённая сковорода", "бастинг по желанию коротко", "не копировать решётку"]
    }
  ],
  "addons": [],
  "adaptations_hint": ["method grill→pan_fry", "equipment grill→skillet"],
  "safety": {"target_note": "как в текущих шагах/заметках стейка; не well-done по умолчанию"},
  "do_not": ["слить с reverse-sear в один slug", "духовка как замена гриля без честной дельты"]
}
```

---

### `stejk-na-skovorode-pan-searing`

Аддоны масла/перца **сохранить**. Добавить гриль.

```json
{
  "id": "stejk-na-skovorode-pan-searing",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "equipment": "skillet",
  "equipment_variants": [
    {
      "code": "grill",
      "title": "На гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["решётка", "переворот", "без сливочного бастинга на углях как на сковороде"]
    }
  ],
  "adaptations_hint": ["method pan_fry→grill", "equipment skillet→grill"],
  "do_not": ["удалить существующие addon", "второй slug стейка"]
}
```

---

### `stejk-reverse-sear`

База духовка + финиш сковороды в шагах. Вариант: финиш на гриле.

```json
{
  "id": "stejk-reverse-sear",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [
    {
      "code": "grill",
      "title": "Финиш на гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["низкая камера как база или короткая пометка что низ — духовка, корочка — гриль", "время корочки короче сковороды", "не сырой стейк сразу на гриль на весь цикл"]
    }
  ],
  "adaptations_hint": ["equipment oven→grill"],
  "do_not": ["выкинуть существующие addon финиша", "сделать это копией stejk-na-grile"]
}
```

Автор: если честный гриль-финиш не укладывается без ломки базы — `{ "error": "финиш гриля лучше оставить addon" }` и **не** плодить пустой equipment.

---

### `ribaj-na-skovorode-s-timyanom`

```json
{
  "id": "ribaj-na-skovorode-s-timyanom",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "equipment": "skillet",
  "allowed_cuts": ["ribeye"],
  "equipment_variants": [
    {
      "code": "grill",
      "title": "На гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["решётка", "тимьян не сыпать на угли", "масло — после съёма"]
    }
  ],
  "adaptations_hint": ["method pan_fry→grill"],
  "do_not": ["духовка well-done", "слить со стейком pan-sear"]
}
```
