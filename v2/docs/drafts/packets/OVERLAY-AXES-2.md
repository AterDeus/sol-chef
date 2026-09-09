# Пачка 2 — сковорода → духовка / аэрогриль / гриль

Старт: **«стартуй оверлей осей 2»**. Правила: [OVERLAY-AXES.md](OVERLAY-AXES.md). Эталон: `kurinaya-grudka-s-ovoshchami.json`, `svinye-otbivnye.json`.

Не трогать: бархат, вок-рис, альо/качо, бастинг, луковый соус, тост пашот, салат с орехами.

---

### `kurinaya-grudka-na-skovorode-s-paprikoy`

```json
{
  "id": "kurinaya-grudka-na-skovorode-s-paprikoy",
  "stream": "overlay_expand",
  "protein_base": "poultry",
  "cook_method": "pan_fry",
  "equipment": "skillet",
  "allowed_cuts": ["breast"],
  "equipment_variants": [
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["форма или решётка", "температура камеры", "время до 72 °C в центре"]
    },
    {
      "code": "air_fryer",
      "title": "В аэрогриле",
      "cook_method_override": "air_fryer",
      "must_differ": ["партия по размеру чаши", "короче духовки", "не перегружать корзину"]
    }
  ],
  "adaptations_hint": ["method pan_fry→oven", "method pan_fry→air_fryer"],
  "safety": {"target_note": "птица ≥ 72 °C в центре (SAFETY)"},
  "do_not": ["целая курица", "сырая грудка толстым пластом без партий на сковороде"]
}
```

---

### `frittata-s-kabachkami-i-bekonom`

Сейчас аддон `no_oven`. База, скорее всего, уже со сковородой + духовкой. Нужен **видимый** ряд посуды: база `skillet` (вся на плите) **или** база духовка + вариант сковорода. Не два одинаковых `skillet`.

```json
{
  "id": "frittata-s-kabachkami-i-bekonom",
  "stream": "overlay_expand",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "equipment": "skillet",
  "equipment_variants": [
    {
      "code": "oven",
      "title": "Дойти в духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["низ на плите, верх в камере", "минуты камеры", "сковорода с жаропрочной ручкой"]
    }
  ],
  "adaptations_hint": ["method pan_fry→oven"],
  "do_not": ["удалить вкусные addon", "микроволновка"]
}
```

Если база уже «сковорода + духовка в одном цикле», вариант «только плита» = `code=skillet` нельзя (совпадёт с базой). Тогда addon `stovetop_only` с дельтой шагов, **не** equipment.

---

### `shakshuka-s-tomatami-i-bazilikom`

Аддоны сыр/кабачок/бекон сохранить.

```json
{
  "id": "shakshuka-s-tomatami-i-bazilikom",
  "stream": "overlay_expand",
  "protein_base": "eggs_dairy",
  "cook_method": "pan_fry",
  "equipment": "skillet",
  "equipment_variants": [
    {
      "code": "oven",
      "title": "Яйца в духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["соус на плите, яйца доходят в камере", "минуты", "форма или жаропрочная сковорода"]
    }
  ],
  "adaptations_hint": ["method pan_fry→oven"],
  "do_not": ["переименовать в яичницу", "удалить addon"]
}
```

---

### `losos-v-duhovke-s-limonom-i-ukropom`

Аддон пергамент сохранить.

```json
{
  "id": "losos-v-duhovke-s-limonom-i-ukropom",
  "stream": "overlay_expand",
  "protein_base": "fish_red_sea",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["кожа вниз", "короче духовки", "не разваливать"]
    },
    {
      "code": "grill",
      "title": "На гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["решётка смазана", "фольга или корзинка если тонкий стейк"]
    }
  ],
  "adaptations_hint": ["method oven→pan_fry", "method oven→grill"],
  "safety": {"target_note": "рыба 63 °C или явный хлопьями сок"},
  "do_not": ["сырой тартар"]
}
```

---

### `sudak-v-duhovke-s-limonom`

Аддон форели сохранить.

```json
{
  "id": "sudak-v-duhovke-s-limonom",
  "stream": "overlay_expand",
  "protein_base": "fish_river",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [
    {
      "code": "skillet",
      "title": "На сковороде",
      "cook_method_override": "pan_fry",
      "equipment": "skillet",
      "must_differ": ["партии", "короче", "не ломать филе"]
    }
  ],
  "adaptations_hint": ["method oven→pan_fry"],
  "safety": {"target_note": "63 °C или готовые хлопья"}
}
```

---

### `govyazhij-oguzok-rostbif-v-duhovke`

Только если есть честный второй сосуд. Гриль для ростбифа — не обязателен.

```json
{
  "id": "govyazhij-oguzok-rostbif-v-duhovke",
  "stream": "overlay_expand",
  "protein_base": "beef",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [],
  "author_must": ["если нет честной другой посуды — не выдумывать; оставить аддоны сэндвича/горчицы"],
  "do_not": ["казан", "сковорода well-done куска 1+ кг"]
}
```

Разрешён `{ "error": "ростбиф только камера" }` — тогда файл не портить.

---

Пропуск этой пачки (не открывать автору): бархат, вок-рис, пасты эмульсии, тост, салаты, масла.
