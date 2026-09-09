# Пачка 3 — тушение → казан / духовка / сковорода

Старт: **«стартуй оверлей осей 3»**. Правила: [OVERLAY-AXES.md](OVERLAY-AXES.md). Эталон: `svinoy-gulyash.json`, `tushenaya-kapusta.json`.

Волновые гуляши / плов / капуста **не** трогать.

---

### `baranya-lopatka-tushenaya-s-lukom-shalot`

```json
{
  "id": "baranya-lopatka-tushenaya-s-lukom-shalot",
  "stream": "overlay_expand",
  "protein_base": "lamb",
  "cook_method": "stew",
  "equipment": "pot",
  "allowed_cuts": ["shoulder"],
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["меньше жидкости", "стенки", "время"]
    },
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["крышка или фольга", "температура камеры ~160", "не бурлить на плите"]
    }
  ],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven"],
  "safety": {"target_note": "лопатка мягкая, не сырая жила; ориентир как в текущих шагах"}
}
```

---

### `govyadina-tushenaya-na-volokna-zamorozka`

Аддон голяшки сохранить.

```json
{
  "id": "govyadina-tushenaya-na-volokna-zamorozka",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "stew",
  "equipment": "pot",
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["жидкость", "томление от стенок"]
    },
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["крышка", "камера", "удобно для заморозки большой порции"]
    }
  ],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven"]
}
```

---

### `tushenaya-kuritsa-s-grechkoj-na-dni`

```json
{
  "id": "tushenaya-kuritsa-s-grechkoj-na-dni",
  "stream": "overlay_expand",
  "protein_base": "poultry",
  "cook_method": "stew",
  "equipment": "pot",
  "use_cases": ["batch"],
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["гречка не клейстерить", "жидкость", "крышка"]
    },
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["форма с крышкой", "минуты", "72 °C у кости"]
    }
  ],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven"],
  "safety": {"target_note": "птица ≥ 72 °C"},
  "do_not": ["новый slug 80 из CATALOG"]
}
```

---

### `tushenye-kurinye-bedra-s-tomatom`

```json
{
  "id": "tushenye-kurinye-bedra-s-tomatom",
  "stream": "overlay_expand",
  "protein_base": "poultry",
  "cook_method": "stew",
  "equipment": "pot",
  "allowed_cuts": ["thigh"],
  "equipment_variants": [
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["меньше жидкости", "крышка сковороды", "короче кастрюли"]
    },
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["форма", "камера", "72 °C"]
    }
  ],
  "adaptations_hint": ["method stew→pan_fry", "method stew→oven"],
  "safety": {"target_note": "птица ≥ 72 °C"}
}
```

---

### `bystroe-kurinoe-karri`

Аддоны овощей сохранить.

```json
{
  "id": "bystroe-kurinoe-karri",
  "stream": "overlay_expand",
  "protein_base": "poultry",
  "cook_method": "stew",
  "equipment": "pot",
  "equipment_variants": [
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["одна сковорода", "меньше жидкости", "не разбавлять до супа"]
    }
  ],
  "adaptations_hint": ["equipment pot→skillet"],
  "safety": {"target_note": "72 °C"},
  "do_not": ["казан ради квоты если цикл 20 минут"]
}
```

---

### `kurinoe-birjani-po-hajderabadski`

База сейчас `pot`. Бириани честно живёт в казане / толстой кастрюле + духовка dum.

```json
{
  "id": "kurinoe-birjani-po-hajderabadski",
  "stream": "overlay_expand",
  "protein_base": "poultry",
  "cook_method": "stew",
  "equipment": "pot",
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["слой риса", "dum", "огонь под дном"]
    },
    {
      "code": "oven",
      "title": "Dum в духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["герметика крышки/теста", "камера", "не мешать рис"]
    }
  ],
  "adaptations_hint": ["equipment pot→kazan", "method stew→oven"],
  "safety": {"target_note": "птица 72 °C; рис доведён"},
  "do_not": ["плов куриный как этот slug"]
}
```

---

### `govyazhi-golyashki-tomlenye-v-duhovke`

Аддоны грибов/чернослива сохранить. Добавить плиту.

```json
{
  "id": "govyazhi-golyashki-tomlenye-v-duhovke",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "oven",
  "equipment": "oven",
  "allowed_cuts": ["shank"],
  "equipment_variants": [
    {
      "code": "pot",
      "title": "На плите",
      "cook_method_override": "stew",
      "equipment": "pot",
      "must_differ": ["слабое бурление", "время длиннее/короче честно", "жидкость не выкипает"]
    }
  ],
  "adaptations_hint": ["method oven→stew"],
  "do_not": ["ужать до 40 минут"]
}
```

---

### `govyazhya-lopatka-zapishennaya-v-rukave`

Аддоны рукав vs фольга уже есть. Нужна **кастрюля/казан** только если цикл без рукава честный. Иначе не плодить.

```json
{
  "id": "govyazhya-lopatka-zapishennaya-v-rukave",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [
    {
      "code": "pot",
      "title": "Тушение в кастрюле",
      "cook_method_override": "stew",
      "equipment": "pot",
      "must_differ": ["без рукава", "жидкость", "крышка", "время"]
    }
  ],
  "adaptations_hint": ["method oven→stew"],
  "author_free": ["если без рукава блюдо другое — error и не портить файл"]
}
```
