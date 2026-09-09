# Пачка 5 — крупы, фикс чечевицы, завтраки

Старт: **«стартуй оверлей осей 5»**. Правила: [OVERLAY-AXES.md](OVERLAY-AXES.md).

Супы волн и пюре/рис/пшено с `eq: —` **не** открывать.

---

### `chechevitsa-s-ovoshchami` (фикс)

Сейчас `variants` `code=pot_stew` + `equipment=pot` = как база. Ряда «Посуда» нет. Заменить на казан **или** addon «Тушение».

```json
{
  "id": "chechevitsa-s-ovoshchami",
  "stream": "overlay_expand",
  "protein_base": "legumes",
  "cook_method": "boil",
  "equipment": "pot",
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["пассеровка на дне", "меньше воды чем варка", "крышка"]
    }
  ],
  "adaptations_hint": ["method boil→stew", "equipment pot→kazan"],
  "do_not": ["оставить equipment=pot у варианта"]
}
```

Удалить старый `pot_stew`. Дельту жидкости/шагов перенести.

---

### `rizotto-bazovyy-parmezan`

Аддоны сохранить. Печёное ризотто — честный oven.

```json
{
  "id": "rizotto-bazovyy-parmezan",
  "stream": "overlay_expand",
  "protein_base": "vegetarian",
  "cook_method": "boil",
  "equipment": "saucepan",
  "equipment_variants": [
    {
      "code": "oven",
      "title": "В духовке",
      "cook_method_override": "oven",
      "equipment": "oven",
      "must_differ": ["почти вся жидкость сразу", "камера", "меньше помешивания", "не копировать 18 подач половника"]
    }
  ],
  "adaptations_hint": ["method boil→oven", "equipment saucepan→oven"],
  "do_not": ["удалить addon грибов/тыквы", "рисоварка"]
}
```

---

### `grechka-na-garnir-s-lukom`

Только если есть дельта казана. Иначе пропуск — в OVERLAY-AXES таблица пропуска.

```json
{
  "id": "grechka-na-garnir-s-lukom",
  "stream": "overlay_expand",
  "equipment_variants": [
    {
      "code": "kazan",
      "title": "В казане",
      "cook_method_override": "stew",
      "equipment": "kazan",
      "must_differ": ["обжарка лука на дне", "соотношение воды"]
    }
  ],
  "author_free": ["error если это та же кастрюля"]
}
```

---

Остальные slug каталога (волны с осью, масла, супы `eq: —`) в пачку 5 **не входят**.
