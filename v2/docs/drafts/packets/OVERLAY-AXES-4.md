# Пачка 4 — духовка: птица, крупные куски

Старт: **«стартуй оверлей осей 4»**. Правила: [OVERLAY-AXES.md](OVERLAY-AXES.md). **Не сливать** четыре целых курицы в один slug (CATALOG).

Эталон мелкой птицы в аэрогриле: `kurinye-krylyshki.json`. Целую тушку в аэрогриль **не** обещать.

---

Общее для целых кур (`classic-roast-chicken`, `kuritsa-tselikom-limonnoe-maslo-bazovyy`, `kuritsa-maslo-limon-zapechennaya`, `kuritsa-s-yablokami-zapechennaya`):

- База остаётся `oven`.
- Вариант `grill`: непрямой жар, грудка не сжечь, 72 °C в бедре.
- Казан / утятница: только если дельта крышки и сока реальна; иначе не писать.
- Не копировать шаги одной курицы в другую (масло-лимон ≠ яблоки).

---

### `classic-roast-chicken`

```json
{
  "id": "classic-roast-chicken",
  "stream": "overlay_expand",
  "protein_base": "poultry",
  "cook_method": "oven",
  "equipment": "oven",
  "allowed_cuts": ["whole"],
  "equipment_variants": [
    {
      "code": "grill",
      "title": "На гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["непрямой жар", "поворот", "72 °C в бедре", "не аэрогриль"]
    }
  ],
  "adaptations_hint": ["method oven→grill"],
  "safety": {"target_note": "птица ≥ 72 °C в самой толстой части бедра"}
}
```

---

### `kuritsa-tselikom-limonnoe-maslo-bazovyy`

Тот же каркас, что classic-roast, **свои** лимон/масло. Не копипаст classic.

```json
{
  "id": "kuritsa-tselikom-limonnoe-maslo-bazovyy",
  "stream": "overlay_expand",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [
    {
      "code": "grill",
      "title": "На гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["непрямой жар", "лимонное масло не капать на угли стаканом"]
    }
  ],
  "adaptations_hint": ["method oven→grill"],
  "safety": {"target_note": "72 °C бедро"}
}
```

---

### `kuritsa-maslo-limon-zapechennaya`

Как предыдущая, если это не дубль. Если после чтения JSON это тот же цикл — `{ "error": "дубль classic/bazovyy, ось не плодить" }` и файл не портить.

---

### `kuritsa-s-yablokami-zapechennaya`

```json
{
  "id": "kuritsa-s-yablokami-zapechennaya",
  "stream": "overlay_expand",
  "cook_method": "oven",
  "equipment": "oven",
  "equipment_variants": [
    {
      "code": "grill",
      "title": "На гриле",
      "cook_method_override": "grill",
      "equipment": "grill",
      "must_differ": ["яблоки в противне не над прямым жаром", "непрямой", "72 °C"]
    }
  ],
  "adaptations_hint": ["method oven→grill"],
  "do_not": ["аэрогриль на целую тушку"]
}
```

---

### `svinnaya-sheya-zapechennaya-s-paprikoj`

```json
{
  "id": "svinnaya-sheya-zapechennaya-s-paprikoj",
  "stream": "overlay_expand",
  "protein_base": "pork",
  "cook_method": "oven",
  "equipment": "oven",
  "allowed_cuts": ["neck"],
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["жидкость или жир шеи", "крышка", "63+hold или 71"]
    }
  ],
  "adaptations_hint": ["method oven→stew"],
  "safety": {"target_note": "свинина 63 °C + hold 180 или 71 °C"}
}
```

---

### `rassypchataya-grechka-suhoj-obzharki-s-lukom-i-gribami`

CATALOG: ось посуды, если отличается. Обжарка крупы + варка.

```json
{
  "id": "rassypchataya-grechka-suhoj-obzharki-s-lukom-i-gribami",
  "stream": "overlay_expand",
  "protein_base": "vegetarian",
  "cook_method": "boil",
  "equipment": "pot",
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["обжарка на дне", "меньше воды", "не мешать до конца"]
    }
  ],
  "adaptations_hint": ["equipment pot→kazan"],
  "author_free": ["если казан = та же кастрюля без дельты — error, не портить"]
}
```

---

Пропуск пачки 4: `buzhenina` (addons), `shokoladnyy-fondan`, `govyazhij-oguzok` (решение в пачке 2).
