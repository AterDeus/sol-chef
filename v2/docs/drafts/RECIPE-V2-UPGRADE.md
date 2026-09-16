# Рецепты 2.0 — бриф для улучшения генерации

Это **не канон** и не волна. Канон: [RECIPE.md](../RECIPE.md), [VOCAB.md](../VOCAB.md), [SAFETY.md](../SAFETY.md), [DATA-MODEL.md](../DATA-MODEL.md), калькулятор: [CALCULATOR.md](../CALCULATOR.md). Этот файл — пакет для анализа: какой JSON ждать от автора.

Две работы автора, не одна. §2–§4 и §5 — валидная карточка (оси, каноны, SAFETY). **§4A — пространство решений**, из которого Django собирает `CookingSolution`. Часть §4A уже в каноне (DEC-020: профиль, use_cases, adaptations). Без полного пространства ролей на строке калькулятор всё ещё слабее книги с чипами.

Не класть результат анализа в корневой `data/recipes/`. Черновики волн — `v2/docs/drafts/recipes/<slug>.json`. Волну не стартовать без фразы «стартуй волну 1».

---

## 1. Две эпохи одного каталога

| | Сейчас (V1, 43 рецепта) | Надо (2.0) |
|--|-------------------------|------------|
| Где лежит | `data/recipes/<папка>/*.json` | Postgres после ETL; новые — черновик JSON по контракту DATA-MODEL |
| Промпт автора | [ADD_RECIPE.md](../../../docs/ADD_RECIPE.md) + старые `RECIPE_AI_*` | [RECIPE.md](../RECIPE.md) |
| Способ готовки | папка `duhovka` / `skovoroda` / `tushenie`… | `cook_method`: `oven` `pan_fry` `stew` `boil` `grill` `steam` `no_cook` |
| Основа блюда | свободный `category`: «говядина», «крупы» | `protein_base` из VOCAB (`beef`, `poultry`, `vegetables`…) |
| Роль на столе | часто смешана с методом (`pan_fry` как тип) | `dish_type`: `main` `soup` `salad`… |
| Посуда | тег «казан» или намёк в тексте | поле `equipment` + ось варианта, если путь другой |
| Ингредиент | `{ "name": "говядина" }` | `{ "canonical_id": "beef", "display_name": "…" }` |
| Единицы | `г`, `ст. л.`, `стакана`, `банка` | только enum: `g` `ml` `tsp` `tbsp`… Стакан запрещён |
| Сода / дрожжи | V1-промпт учил `gentle` | **`manual`**. `gentle` = соль/специи, формула `ratio^0.7` |
| Вариации | `{ "title", "text" }` — абзац | **вариант** (редакция подготовила) ≠ **адаптация** (правило для калькулятора). Аддон «с грибами» — второстепенно |
| Заметки | один blob-текст | список `{ "title", "text" }`, 3–10 пунктов у **новых** |
| Температура | в `notes` / `timer_note` («82 °C») | поля шага `target_internal_temperature_c` (+ `pull_` / `hold_`) |
| Отрубы | в `detail` («лопатка или огузок») | `allowed_cuts`: коды VOCAB (`shoulder`, `rump`) |
| Аллергены | нет / эвристика по подстроке | флаг на каноне; `unknown` ≠ «нет» |
| Источник | часто `https://sol-chef.ru` | циклический URL — **Critical**; editorial — без этой ссылки |
| `editorial_tested` | нет / путают с `tried` | ставит только человек |

ETL уже импортирует 43 как есть: вариации → `has_delta=false` + `legacy_text`, заметки режутся по `\n\n` без заголовков, `allowed_cuts=[]`, температуры из сида, а не из JSON. Это **не** целевой формат новых рецептов. Улучшать существующие — отдельным проходом автора/модератора, не «дописать ETL».

---

## 2. Пример: как есть (V1)

Взят рецепт `barhatnaya-govyadina-po-kitajski` из `data/recipes/skovoroda/govyadina.json`. Типичный «личный повар»: русские единицы, вариации абзацем, сода с `gentle`, источник на свой же домен, отрубы спрятаны в `detail`.

```json
{
  "id": "barhatnaya-govyadina-po-kitajski",
  "title": "Бархатная говядина по-китайски",
  "source_type": "article",
  "source_url": "https://sol-chef.ru",
  "source_name": "Личный повар",
  "category": "говядина",
  "tags": ["стир-фрай", "азиатская кухня", "быстро", "ужин"],
  "summary": "Азиатская техника «бархатования» (velveting) позволяет сделать недорогой и жесткий отруб говядины чрезвычайно нежным и сочным. Кратковременное воздействие пищевой соды размягчает мясные волокна, а маринад из крахмала, яичного белка и масла запечатывает соки при молниеносной обжарке на раскаленной сковороде.",
  "ingredients": [
    { "name": "говядина", "amount": 500, "unit": "г", "detail": "лопатка, огузок или бедро", "scalable": true },
    { "name": "пищевая сода", "amount": 0.5, "unit": "ч. л.", "scalable": true, "scale_mode": "gentle" },
    { "name": "яичный белок", "amount": 1, "unit": "шт", "scalable": true, "scale_mode": "whole" },
    { "name": "кукурузный крахмал", "amount": 1, "unit": "ст. л.", "detail": "(10 г)", "scalable": true },
    { "name": "соевый соус", "amount": 2, "unit": "ст. л.", "detail": "(30 мл)", "scalable": true },
    { "name": "растительное масло", "amount": 1, "unit": "ст. л.", "detail": "в маринад", "scalable": true },
    { "name": "растительное масло", "amount": 3, "unit": "ст. л.", "detail": "для жарки", "scalable": true }
  ],
  "steps": [
    "Нарезать говядину тонкими пластинами толщиной около 3 мм строго поперек волокон.",
    "Посыпать мясо содой, тщательно перемешать и оставить на 15 минут при комнатной температуре.",
    "Тщательно промыть говядину в холодной проточной воде, чтобы полностью удалить остатки соды, и хорошо отжать от лишней влаги.",
    "Замариновать мясо: добавить соевый соус, яичный белок и крахмал, перемешать до гладкости, затем влить 1 ст. л. растительного масла.",
    "Сильно разогреть сковороду или вок с растительным маслом на максимальном огне.",
    "Выложить говядину небольшими партиями в один слой и быстро обжаривать в течение 1.5–2 минут, постоянно помешивая, до изменения цвета."
  ],
  "variations": [
    {
      "title": "С болгарским перцем и луком",
      "text": "После обжарки мяса отдельно обжарить на сильном огне 1 репчатый лук и 1 болгарский перец (2 минуты), затем вернуть говядину и прогреть вместе 30 секунд."
    },
    {
      "title": "В черном перечном соусе",
      "text": "В конце приготовления добавить к мясу 1 ч. л. крупно смолотого черного перца, 2 измельченных зубчика чеснока и 1 ст. л. соевого соуса, быстро перемешать."
    },
    {
      "title": "С брокколи в имбирном соусе",
      "text": "Отварить 200 г брокколи 1 минуту в кипятке. Добавить к обжаренной говядине вместе с 0.5 ч. л. натертого имбиря и 50 мл бульона, смешанного с 0.5 ч. л. крахмала."
    }
  ],
  "notes": "Главные секреты техники: нарезка исключительно ПОПЕРЕК волокон и строгое соблюдение времени выдержки в соде (не более 15–20 минут, иначе мясо потеряет текстуру). Добавление растительного масла в конце маринуса не дает ломтикам слипаться при обжарке.",
  "added": "2026-07-22"
}
```

### Разбор дыр (этот рецепт)

| Что | Почему это ломает 2.0 |
|-----|------------------------|
| Нет `protein_base` / `cook_method` / `dish_type` / `equipment` | Фильтры книги и калькулятор читают VOCAB, не папку `skovoroda` и не `category` |
| `tags` + `category` | Не словари 2.0. «Стир-фрай» — не `dish_type`. Теги в целевой JSON не писать |
| `source_url: https://sol-chef.ru` | Critical: циклическая ссылка на себя. Editorial → URL убрать, не подменять выдуманным |
| `unit: "г"` / `"ч. л."` / `"ст. л."` | Только коды `g` `tsp` `tbsp` |
| Сода `scale_mode: "gentle"` | Прямо противоречит SAFETY/VOCAB. Сода, разрыхлитель, дрожжи, желатин — **`manual`**. Старый ADD_RECIPE.md здесь врёт |
| Масло «для жарки» `linear` | Масло для сковороды — `gentle`. Масло **в маринаде** — `linear` (это часть состава, не смазка сосуда) |
| Две строки с одним именем «растительное масло» | Ок как две строки, но у обеих должен быть один `canonical_id`; `replace`/`remove` в дельте — по `position`, не по id |
| Отрубы только в `detail` | `allowed_cuts: ["shoulder", "rump"]`. Слово «бедро» для говядины **не** код VOCAB (`thigh` = птица). Не выдумывать cut |
| Нет `is_anchor` | Якорь «У меня» — первая весовая строка: говядина 500 g |
| Нет `canonical_id` | Аллергены висят на каноне: `egg_white` → `egg`; `soy_sauce` → `soy`+`gluten`. Без канона карточка врёт «аллергенов нет» |
| Шаги — строки | Объекты `{ "text" }`. У жарки — `timer_seconds` + `equipment_note` (не перегружать сковороду). `timer_min` V1 → секунды |
| Вариации `title`+`text` | Состав меняется → **Major**, если оставить абзацем. Нужны три аддона с `ingredient_delta` / `step_delta` / `allergen_delta` |
| Вариация с бульоном | Магазинный бульон → `unknown: celery`, если это не «бульон или вода». Дельта обязана нести `allergen_delta` |
| `notes` blob | Список пунктов с заголовками. Квоты 3/6/10 — при переработке, не пустые абзацы |
| `added`, `tags` | Служебное V1. В черновик 2.0 не копировать |
| Нет `servings` | Не выдумывать «4 порции». Масштаб от якоря 500 g |

Другие дыры каталога (не в этом JSON, но генератор их плодит):

- Птица/свинина/рыба: температура только в тексте («не ниже 82 °C») — валидатор смотрит **поле** `target_internal_temperature_c`.
- `classic-roast-chicken`: `id` английский перевод, в шаге 62 °C в бедре — ниже минимума SAFETY (бедро птицы 82 °C).
- «A или B» в одном `name` («красное вино или бальзамический уксус») — два ингредиента с одним `choice_group`.
- «Для подачи» / йогурт к карри — `optional: true`, в аллергенах блюда не участвует.
- Единица `стакана` (карри) — запрещена; 1 стакан = 250 ml **только** как конвертация ETL, в новых JSON сразу `ml`.
- `dish_type` нельзя ставить `pan_fry` / `stew`.
- Второй slug вместо дельты («то же жаркое в казане») — запрещён.

---

## 3. Тот же рецепт — как надо (контракт автора 2.0)

Это **целевой черновик для анализа**, не импорт в `data/` и не готовая публикация. Факты те же, что в V1; новые каноны (`bell_pepper`, `broccoli`) автор обязан объявить, а не оставить русской строкой.

Позиции ингредиентов и шагов с **1**. `insert.after_position`: `0` = перед первым шагом.

```json
{
  "id": "barhatnaya-govyadina-po-kitajski",
  "title": "Бархатная говядина по-китайски",
  "summary": "Недорогой отруб нарезают поперёк волокон, коротко обрабатывают содой и обжаривают порциями на сильном огне. Крахмал, яичный белок и масло в маринаде держат сок внутри.",
  "protein_base": "beef",
  "cook_method": "pan_fry",
  "dish_type": "main",
  "equipment": "skillet",
  "energy_profile": "standard",
  "allowed_cuts": ["shoulder", "rump"],
  "scale_mode": "linear",
  "scalable": true,
  "servings": null,
  "source_type": "article",
  "source_name": "Редакция sol-chef",
  "source_url": null,
  "editorial_tested": false,
  "high_risk_flags": [],
  "caution_text": null,
  "prep": [],
  "new_ingredients": [
    {
      "canonical_id": "bell_pepper",
      "title": "болгарский перец",
      "aliases": ["перец болгарский", "сладкий перец"],
      "allergens_contains": [],
      "allergens_may_contain": [],
      "allergens_unknown": []
    },
    {
      "canonical_id": "broccoli",
      "title": "брокколи",
      "aliases": [],
      "allergens_contains": [],
      "allergens_may_contain": [],
      "allergens_unknown": []
    }
  ],
  "ingredients": [
    {
      "position": 1,
      "canonical_id": "beef",
      "display_name": "говядина",
      "amount": 500,
      "amount_max": null,
      "unit": "g",
      "detail": "лопатка или огузок, тонкими пластинами 3 мм поперёк волокон",
      "scale_mode": "linear",
      "scalable": true,
      "is_anchor": true,
      "optional": false,
      "choice_group": null
    },
    {
      "position": 2,
      "canonical_id": "baking_soda",
      "display_name": "пищевая сода",
      "amount": 0.5,
      "unit": "tsp",
      "detail": null,
      "scale_mode": "manual",
      "scalable": true,
      "is_anchor": false,
      "optional": false,
      "choice_group": null
    },
    {
      "position": 3,
      "canonical_id": "egg_white",
      "display_name": "яичный белок",
      "amount": 1,
      "unit": "pcs",
      "detail": null,
      "scale_mode": "whole",
      "scalable": true,
      "is_anchor": false,
      "optional": false,
      "choice_group": null
    },
    {
      "position": 4,
      "canonical_id": "corn_starch",
      "display_name": "кукурузный крахмал",
      "amount": 1,
      "unit": "tbsp",
      "detail": "около 10 г",
      "scale_mode": "linear",
      "scalable": true,
      "is_anchor": false,
      "optional": false,
      "choice_group": null
    },
    {
      "position": 5,
      "canonical_id": "soy_sauce",
      "display_name": "соевый соус",
      "amount": 2,
      "unit": "tbsp",
      "detail": "около 30 мл, обычный пшеничный",
      "scale_mode": "linear",
      "scalable": true,
      "is_anchor": false,
      "optional": false,
      "choice_group": null
    },
    {
      "position": 6,
      "canonical_id": "vegetable_oil",
      "display_name": "растительное масло",
      "amount": 1,
      "unit": "tbsp",
      "detail": "в маринад",
      "scale_mode": "linear",
      "scalable": true,
      "is_anchor": false,
      "optional": false,
      "choice_group": null
    },
    {
      "position": 7,
      "canonical_id": "vegetable_oil",
      "display_name": "растительное масло",
      "amount": 3,
      "unit": "tbsp",
      "detail": "для жарки",
      "scale_mode": "gentle",
      "scalable": true,
      "is_anchor": false,
      "optional": false,
      "choice_group": null
    }
  ],
  "steps": [
    {
      "position": 1,
      "text": "Нарезать говядину тонкими пластинами около 3 мм строго поперёк волокон."
    },
    {
      "position": 2,
      "text": "Посыпать мясо содой, тщательно перемешать и оставить при комнатной температуре.",
      "timer_seconds": 900,
      "timer_label": "Сода",
      "timer_note": "Не дольше 15–20 минут, иначе текстура развалится"
    },
    {
      "position": 3,
      "text": "Промыть говядину в холодной проточной воде до полного удаления соды и хорошо отжать."
    },
    {
      "position": 4,
      "text": "Замариновать: соевый соус, яичный белок и крахмал перемешать до гладкости, затем влить 1 ст. л. масла."
    },
    {
      "position": 5,
      "text": "Сильно разогреть сковороду с маслом для жарки на максимальном огне."
    },
    {
      "position": 6,
      "text": "Выложить говядину небольшими партиями в один слой и обжаривать, постоянно помешивая, до изменения цвета.",
      "timer_seconds": 90,
      "timer_label": "Обжарка партии",
      "timer_note": "1.5–2 минуты на партию; ориентир — цвет, не таймер",
      "equipment_note": "Не перегружать сковороду: в один слой, порциями, иначе мясо тушится в соку."
    }
  ],
  "variants": [
    {
      "axis": "addon",
      "code": "with_pepper_onion",
      "title": "С перцем и луком",
      "has_delta": true,
      "ingredient_delta": {
        "add": [
          {
            "canonical_id": "onion",
            "display_name": "лук",
            "amount": 1,
            "unit": "pcs",
            "detail": "репчатый",
            "scale_mode": "whole",
            "scalable": true
          },
          {
            "canonical_id": "bell_pepper",
            "display_name": "болгарский перец",
            "amount": 1,
            "unit": "pcs",
            "scale_mode": "whole",
            "scalable": true
          }
        ]
      },
      "step_delta": {
        "insert": [
          {
            "after_position": 6,
            "text": "Мясо снять. На сильном огне обжарить лук и болгарский перец 2 минуты, вернуть говядину и прогреть вместе 30 секунд.",
            "timer_seconds": 120,
            "timer_label": "Овощи"
          }
        ]
      },
      "allergen_delta": {
        "contains_add": [],
        "contains_remove": [],
        "may_contain_add": [],
        "may_contain_remove": [],
        "unknown_add": [],
        "unknown_remove": []
      },
      "high_risk_delta": { "add": [], "remove": [] }
    },
    {
      "axis": "addon",
      "code": "with_black_pepper_sauce",
      "title": "В перечном соусе",
      "has_delta": true,
      "ingredient_delta": {
        "add": [
          {
            "canonical_id": "black_pepper",
            "display_name": "чёрный перец",
            "amount": 1,
            "unit": "tsp",
            "detail": "крупно смолотый",
            "scale_mode": "gentle",
            "scalable": true
          },
          {
            "canonical_id": "garlic",
            "display_name": "чеснок",
            "amount": 2,
            "unit": "clove",
            "detail": "измельчить",
            "scale_mode": "whole",
            "scalable": true
          },
          {
            "canonical_id": "soy_sauce",
            "display_name": "соевый соус",
            "amount": 1,
            "unit": "tbsp",
            "detail": "дополнительно в соус",
            "scale_mode": "linear",
            "scalable": true
          }
        ]
      },
      "step_delta": {
        "insert": [
          {
            "after_position": 6,
            "text": "В конце добавить к мясу перец, чеснок и ещё 1 ст. л. соевого соуса, быстро перемешать."
          }
        ]
      },
      "allergen_delta": {
        "contains_add": [],
        "contains_remove": [],
        "may_contain_add": [],
        "may_contain_remove": [],
        "unknown_add": [],
        "unknown_remove": []
      },
      "high_risk_delta": { "add": [], "remove": [] }
    },
    {
      "axis": "addon",
      "code": "with_broccoli_ginger",
      "title": "С брокколи и имбирём",
      "has_delta": true,
      "ingredient_delta": {
        "add": [
          {
            "canonical_id": "broccoli",
            "display_name": "брокколи",
            "amount": 200,
            "unit": "g",
            "scale_mode": "linear",
            "scalable": true
          },
          {
            "canonical_id": "ginger",
            "display_name": "имбирь",
            "amount": 0.5,
            "unit": "tsp",
            "detail": "свежий, натёртый",
            "scale_mode": "gentle",
            "scalable": true
          },
          {
            "canonical_id": "stock",
            "display_name": "бульон",
            "amount": 50,
            "unit": "ml",
            "detail": "говяжий или куриный; вода допустима — см. заметку",
            "scale_mode": "linear",
            "scalable": true
          },
          {
            "canonical_id": "corn_starch",
            "display_name": "кукурузный крахмал",
            "amount": 0.5,
            "unit": "tsp",
            "detail": "развести в бульоне",
            "scale_mode": "linear",
            "scalable": true
          }
        ]
      },
      "step_delta": {
        "insert": [
          {
            "after_position": 6,
            "text": "Брокколи отварить 1 минуту в кипятке. Добавить к обжаренной говядине с имбирём и 50 мл бульона, смешанного с 0.5 ч. л. крахмала.",
            "timer_seconds": 60,
            "timer_label": "Брокколи"
          }
        ]
      },
      "allergen_delta": {
        "contains_add": [],
        "contains_remove": [],
        "may_contain_add": [],
        "may_contain_remove": [],
        "unknown_add": ["celery"],
        "unknown_remove": []
      },
      "high_risk_delta": { "add": [], "remove": [] }
    }
  ],
  "notes": [
    {
      "title": "Нарезка",
      "text": "Только поперёк волокон и не толще 3 мм. Вдоль волокон даже сода не спасёт жёсткость."
    },
    {
      "title": "Сода",
      "text": "15 минут достаточно. Дольше 20 — каша. Соду масштабировать вручную: лишняя даёт мыльный вкус. После выдержки мясо промыть начисто."
    },
    {
      "title": "Отруб",
      "text": "Лопатка или огузок. Постное «бедро» из старого текста в словарь отрубов не входит — брать огузок, не вырезку."
    },
    {
      "title": "Сковорода",
      "text": "Партии в один слой. Полная сковорода = тушение в соку, бархат пропадает."
    },
    {
      "title": "Бульон в вариации",
      "text": "Вода допустима. Магазинный бульон часто с сельдереем — на карточке варианта стоит unknown, не «аллергенов нет»."
    },
    {
      "title": "Соевый соус",
      "text": "Обычный содержит пшеницу. Безглютеновый соус — другая строка канона, не молчаливая замена."
    }
  ]
}
```

Почему три аддона, а не `light` и не казан: в исходнике нет другого жира и нет другого сосуда. Не выдумывать **варианты**. Вок в шаге V1 = та же сковорода (`skillet`), не вторая посуда.

Этот JSON уже годится для книги. Для калькулятора его всё ещё мало: нет ролей ингредиентов, нет «можно заменить / можно убрать», нет профиля времени и закупки, нет разрешённых смен белка и посуды. Калькулятор увидит «совпало 5 из 7» и аддоны с перцем — но не ответит «нет сковороды / есть только грудка / не хочу 15 минут ждать соду». Добор — §4A, не новые slug.

Бульон в третьем аддоне — единственное место, где появляется сельдерей как `unknown`. База без бульона сельдерей не содержит. «Бульон или вода» как **одна** строка базы (`stock_or_water`) unknown не вешает — здесь бульон добавлен вариацией, поэтому `unknown_add: ["celery"]`.

---

## 4. Правила улучшения существующих (43 → контракт 2.0)

Цель прохода: тот же блюдо, тот же `id`/`slug`, без новых фактов. Не второй рецепт.

1. **Словарь осей.** Выставить `protein_base`, `cook_method`, `dish_type`, `equipment` по VOCAB и таблицам маппинга. Папку не копировать: `skovoroda` → `pan_fry` + `skillet`, не код `skovoroda`. `category: говядина` → `protein_base: beef` + `dish_type: main` (если это горячее).
2. **`id` не переименовывать** у уже опубликованных, даже если это английский `classic-roast-chicken`. Правило транслита — для **новых**.
3. **Источник.** Стереть `https://sol-chef.ru`. Editorial: `source_name` редакции, `source_url` пустой. Чужой текст: имя + живой URL. Без атрибуции — Critical, не «улучшать».
4. **Ингредиенты → каноны.** `name` V1 резолвить через сид (`v1_ingredient_map.json`). Нет ключа — завести `new_ingredients[]`, не оставлять голую строку. Аллергены с канона, не из слова «молоко».
5. **Единицы.** Таблица V1→VOCAB. `стакана` → `ml` (×250) в существующих; в переписанном JSON сразу `ml`. `банка` томатов → `pcs` + detail, не выдумывать граммы, если в V1 их не было.
6. **`scale_mode` переписать, не копировать.** Соль/перец/специи/масло для сковороды → `gentle`. Сода/разрыхлитель/дрожжи/желатин → `manual` **даже если в V1 стояло `gentle`**. Яйца/`pcs` белок → `whole`. `to_taste` / `pinch` → `amount: null`, `scalable: false`.
7. **Якорь.** Ровно одна строка `is_anchor: true` — белок/крупа с г/мл/кг/л. Нет такой строки и нет `servings` → масштаб выключен, **не** ставить 4 порции.
8. **«A или B».** Разрезать на две строки с общим `choice_group`. «Бульон или вода» → канон `stock_or_water` **без** `unknown: celery`. Чистый «бульон» → `stock` + unknown сельдерей.
9. **Опциональное.** «Для подачи», «по желанию» → `optional: true`. Йогурт к карри не вешает `milk` на базу.
10. **Отрубы.** Заполнить `allowed_cuts` кодами VOCAB по смыслу блюда. Рыба/овощи → `[]`. Неизвестное слово («бедро» говядины) не маппить на `thigh`.
11. **Шаги.** Все — объекты. `timer_min` × 60 = `timer_seconds`. Птица/свинина/фарш/готовая рыба: `target_internal_temperature_c` из SAFETY, не из старого текста, если текст ниже минимума (62 °C в бедре курицы — исправить до 82, не «сохранить факт источника», если источник небезопасен). `pull` без `target` нельзя. `pan_fry` мяса/котлет — `equipment_note` про партии.
12. **Вариации с новым составом** → `variants[]` с `has_delta: true`. Абзац `legacy_text` оставить только если состав **не** меняется и дельту честно не собрать. Меняется состав без дельты — Major.
13. **Посуда.** «А в казане иначе» из notes → ось `equipment`, не заметка. Тот же сосуд, другое предостережение → `equipment_note`.
14. **Калораж.** `light`/`rich` только если в исходнике реально другой жир/сахар того же блюда. Не выдумывать ккал и не подменять стейк курицей.
15. **Заметки.** Blob нарезать на `{title,text}`. Выкинуть мета «Пилот sol-chef: B05… оценка 4.71» из пользовательских заметок. Не копировать шаг дословно. Цель 3–6 сильных; пустые ради квоты — Minor. ETL сам это **не** делает.
16. **Не трогать.** `editorial_tested`, `tried`, `tags` как замена словарей, high-risk без блока «Осторожно» и без человека.
17. **Не плодить slug.** Четыре почти одинаковых целых курицы — не «улучшать» в четыре дельты одной, пока человек не сказал слить семейство. Улучшение = поля и дельты **этого** id.
18. **Адаптации не выдумывать из молчания V1.** Нет в тексте «можно грудку вместо бедра» — не писать правило. Есть факт («лопатка или огузок») — `allowed_cuts` + при необходимости substitution. Соду в бархатовании не помечать `removable`. Профили времени/усилия — по шагам, не «45 минут» из головы.

---

## 4A. Контракт адаптивного рецепта

Предложение в канон (RECIPE / DATA-MODEL / CALCULATOR), не текущая схема Postgres. Сейчас в движке: оси `addon` \| `equipment` \| `energy`, глобальный/рецептный `SubstitutionRule`, `optional`, `intent=` как вес. Этого мало, чтобы из одного JSON собрать персональное решение.

### Зачем

Структурированный рецепт закрывает книгу:

```
карточка → поиск / фильтры → чипы-добавки
```

Калькулятор ([CALCULATOR.md](../CALCULATOR.md)) собирает **CookingSolution**: что приготовить из ситуации человека, как адаптировать, при каких условиях, какой вариант лучше. Цепочка другая:

```
карточка
  → что из неё можно приготовить
  → как её можно адаптировать
  → при каких условиях
  → какой вариант лучше этому человеку
```

Философия генерации не «напиши рецепт», а **опиши пространство допустимых решений вокруг блюда**. Runtime LLM нет: калькулятор применяет только правила, которые автор/модератор заранее разрешили.

Пользователю важнее не «с брокколи», а:

- не хочу покупать сливки;
- есть только сковорода;
- есть 20 минут;
- есть филе, не бедро;
- сразу на несколько дней;
- нет одного ингредиента.

Аддоны остаются, но это **второстепенный** слой.

### Вариант ≠ адаптация

| | Вариант (`variants`) | Адаптация (`adaptation_rules`) |
|--|----------------------|--------------------------------|
| Кто готовит | Автор считает полноценной версией блюда | Движок применяет правило, если ситуация совпала |
| Пример | `standard` / `light` / `one_pan` | нет сливок → сметана; нет петрушки → убрать; нет духовки → сковорода, **если разрешено** |
| Объём | Конечное число (типично 0–4 на тип) | Конечный список правил, не комбинаторный взрыв карточек |
| UI | Чип на странице рецепта | Человеку — «заменить сметаной», не отдельный slug |

```
Recipe
 ├── Variants          ← редакция подготовила display
 │    ├── content        addon: грибы, перец
 │    ├── execution      one_pan, oven, fast
 │    └── profile        light, batch
 └── Adaptations       ← способности, не чипы
      ├── substitutions
      ├── omissions
      └── method / equipment / protein
```

Не плодить десяток `VARIANT_AXIS` как пользовательских чипов. `substitution`, `time`, `effort`, `portion` — **способности** рецепта. В чипы попадают только те варианты, которые автор реально собрал дельтой.

Порции и «без лука × без моркови × на 3 человек» **не** варианты. Масштаб — Django (`servings` / якорь). Вариативность = конечные редакционные правила + детерминированные преобразования.

### Роль ингредиента (`ingredient_role`)

Сейчас на строке: `optional`, `choice_group`, `is_anchor`, `scale_mode`. Для замен этого мало: движок не знает, *зачем* сливки в этом блюде.

```text
INGREDIENT_ROLE = protein | vegetable | grain | legume | fat | liquid
                 | sauce_base | thickener | acid | sweetener
                 | seasoning | aromatic | garnish | binder
```

Примеры на строке: курица → `protein`; лук/чеснок → `aromatic`; сливки → `sauce_base`; масло → `fat`; мука → `thickener`; лимон → `acid`; соль → `seasoning`.

Тогда «сливки ↔ сметана» имеет смысл, потому что **в этом рецепте** оба — `sauce_base`, а не потому что в глобальной таблице 400 пар. В десерте та же пара может быть запрещена (`forbidden` или нет правила).

`choice_group` («вино или уксус») — явный выбор автора в базе. Роль — чтобы калькулятор подставил *другую* канон-пару по правилу, которого в списке ингредиентов нет.

### Доступность строки

`optional` недостаточно. На каждой позиции:

```json
{
  "required": true,
  "substitutable": true,
  "removable": false
}
```

| | required | substitutable | removable |
|--|----------|---------------|-----------|
| Курица (якорь) | да | да (грудка↔бедро, если правило есть) | нет |
| Петрушка | нет | да | да |
| Сода в бархатовании | да | нет | нет |
| Йогурт «для подачи» | нет | да | да (`optional` сегодня) |

Движок оценивает **последствия отсутствия**, не «совпало 7 из 10». Нет соды → рецепт бархатной говядины не подходит. Нет петрушки → штраф ~0, блюдо живо.

Совместимость с текущим `optional`: `optional: true` ≈ `required: false` и обычно `removable: true`. Ядро блюда: `required: true`, `removable: false`.

### Профили рецепта (не таймер шага)

Таймер шага ≠ «сколько это займёт у человека» и ≠ «надо ли стоять у плиты». Для `intent=fast|easy|batch` нужны агрегаты. Минуты 15/30 в UI 43 врать нельзя — **новые** рецепты поле обязаны нести, иначе сценарий «быстро» остаётся эвристикой по числу шагов.

```json
"time_profile": {
  "total_minutes": 45,
  "active_minutes": 15,
  "waiting_minutes": 30
},
"effort": {
  "active_cooking": 2,
  "prep": 3,
  "washing": 1
},
"batch_friendly": true
```

`effort` 1–5 внутри полей, не одна цифра «сложность = время». Паста 25 мин с постоянным помешиванием может быть тяжелее тушения 90 мин / 10 мин работы.

Посуда богаче скаляра `equipment: skillet`:

```json
"equipment_profile": {
  "required": ["skillet"],
  "preferred": ["skillet"],
  "alternatives": []
}
```

`alternatives` заполняются **только** если есть `adaptation_rule` или variant `execution` с дельтой. Калькулятор не додумывает «наверное, можно в кастрюле».

Закупка — не «7 из 10 совпало»:

```json
"shopping_profile": {
  "core": ["beef", "egg_white", "soy_sauce"],
  "common": ["vegetable_oil", "corn_starch"],
  "special": ["baking_soda"],
  "one_recipe_only": []
}
```

`PANTRY_ASSUMED` (соль, масло, вода…) в `core` не класть. `PANTRY_COMMON` (паприка…) — `common`, отсутствие не убивает. Редкое / «только для этого блюда» — `special` / `one_recipe_only` → трение докупки выше. Счёт `required_purchase_count` движок может вывести из профиля + `have=`; автору достаточно разметки корзин.

### `adaptation_rule`

Ядро калькулятора. Не второй рецепт и не аддон «с грибами».

```json
{
  "type": "substitution",
  "from": "cream",
  "to": "sour_cream",
  "quality": 0.90,
  "conditions": { "ingredient_role": "sauce_base" },
  "ingredient_delta": null,
  "step_delta": null,
  "allergen_delta": {
    "contains_add": [],
    "contains_remove": [],
    "may_contain_add": [],
    "may_contain_remove": [],
    "unknown_add": [],
    "unknown_remove": []
  }
}
```

Контекст обязателен: `cream → sour_cream` в соусе — да; в супе — возможно (`quality` ниже); в десерте — нет правила или `forbidden`. Глобальный сид `substitution_rules.json` остаётся запасным; **рецептное правило бьёт глобальное** (это уже DATA-MODEL). Новые рецепты должны нести свои правила, а не надеяться на справочник.

Типы:

| `type` | Когда | Пример |
|--------|--------|--------|
| `substitution` | нет `from`, в `have` есть `to` | сливки → сметана / йогурт без сахара; бедро → грудка |
| `omission` | нет ингредиента и `removable` | убрать петрушку, `quality` 0.98 |
| `equipment` | нет требуемой посуды, есть альтернатива | `oven` → `skillet`, только если автор разрешил |
| `method` | смена `cook_method` | `oven` → `pan_fry`, `quality` 0.78, дельты шагов |

Смена метода/посуды — не догадка движка:

```json
{
  "type": "method",
  "from_method": "oven",
  "to_method": "pan_fry",
  "quality": 0.78,
  "cook_method_override": "pan_fry",
  "step_delta": { "replace": [] },
  "allergen_delta": {
    "contains_add": [], "contains_remove": [],
    "may_contain_add": [], "may_contain_remove": [],
    "unknown_add": [], "unknown_remove": []
  }
}
```

Белок/отруб — тот же механизм, не только `allowed_cuts` как фильтр книги:

```json
{
  "type": "substitution",
  "from": "chicken_thighs",
  "to": "chicken_breast",
  "quality": 0.89,
  "step_delta": {
    "replace": [
      {
        "position": 4,
        "text": "Тушить грудку на 5–7 минут меньше бедра; target 72 °C, не 82.",
        "target_internal_temperature_c": 72
      }
    ]
  }
}
```

Человек пишет «есть грудка» — калькулятор не отсекает блюдо из бёдер, а собирает решение: «подойдёт, время и температура другие».

У каждой адаптации `quality` 0.00–1.00. Ниже порога DEFAULTS (сейчас 0.50) — как нет правила. `forbidden: true` — никогда. Состав меняется → те же инварианты, что у варианта: `allergen_delta`, SAFETY target, не больше одного якоря после сборки.

### Типы вариантов (если автор готовит display)

Текущее `VARIANT_AXIS = {addon, equipment, energy}` смешивает разные уровни: состав, исполнение, предпочтение по результату. Для генератора лучше не раздувать axis, а разметить **назначение**:

| Класс | Коды-примеры | Чип на странице | Калькулятор |
|-------|----------------|-----------------|-------------|
| `content` (бывший addon) | `with_mushrooms`, `with_pepper_onion` | да | вторично: закрыть «есть перец» |
| `execution` | `one_pan`, `fast`, `oven` | да, если есть дельта | `intent=fast\|oven`, `equipment=` |
| `profile` | `light`, `rich`, `batch` | да | `intent=light\|batch` |

```json
{
  "variant_class": "execution",
  "code": "fast",
  "title": "Быстрый вариант",
  "when": { "max_total_minutes": 25 },
  "has_delta": true
}
```

`energy` / `light` не ставить в один ряд с «добавить грибы». Аддон без `when` — бонус вкуса, не ответ на ситуацию.

### Что автор выдаёт (полный пакет)

```
BASE RECIPE          оси, каноны, шаги, SAFETY
+ VARIANTS           конечные полноценные версии
+ ADAPTATION RULES   замены, исключения, смена метода/посуды/белка
+ PROFILES           time, effort, equipment, shopping, batch
```

Один рецепт обслуживает десятки ситуаций, не становясь десятками slug.

Эскиз (не полный JSON) для «курица в сливочном соусе»:

```text
База: chicken_thighs, cream, onion, garlic
Замены: thighs→breast; cream→sour_cream; cream→yogurt (без сахара, role=sauce_base)
Исключение: garlic removable
Метод: pan_fry → oven (quality 0.8, дельта шагов)
Режимы: fast / light / one_pan
Профиль: 20 min active, 35 total, effort 2, washing 1
```

Добор к бархатной говядине из §3 (адаптации, не новые аддоны):

```json
{
  "ingredient_roles": {
    "1": "protein",
    "2": "binder",
    "3": "binder",
    "4": "thickener",
    "5": "seasoning",
    "6": "fat",
    "7": "fat"
  },
  "availability": {
    "2": { "required": true, "substitutable": false, "removable": false }
  },
  "time_profile": { "total_minutes": 25, "active_minutes": 12, "waiting_minutes": 15 },
  "effort": { "active_cooking": 3, "prep": 3, "washing": 2 },
  "batch_friendly": false,
  "equipment_profile": {
    "required": ["skillet"],
    "preferred": ["skillet"],
    "alternatives": []
  },
  "shopping_profile": {
    "core": ["beef"],
    "common": ["soy_sauce", "vegetable_oil", "corn_starch", "egg_white"],
    "special": ["baking_soda"],
    "one_recipe_only": []
  },
  "adaptation_rules": [
    {
      "type": "substitution",
      "from": "soy_sauce",
      "to": "tamari",
      "quality": 0.88,
      "conditions": { "ingredient_role": "seasoning" },
      "note": "безглютеновая ветка; allergen_delta снимает gluten, если канон tamari без пшеницы"
    }
  ]
}
```

Нет правила «говядина → курица»: это другое блюдо. Нет `oven` в `alternatives`: автор не разрешил. Сода не `removable`. Аддоны с перцем остаются content-вариантами.

### Сборка в runtime

```
Recipe (база + профили + правила)
        ↓
ситуация человека (have, intent, equipment, without)
        ↓
кандидаты (slug; не отсекать только из-за missing from, если есть substitution)
        ↓
adaptation engine (только разрешённые правила)
        ↓
scoring (покрытие core, трение замен и докупки, time/effort vs intent)
        ↓
CookingSolution (featured + alternatives)
```

Это стык с уже написанным `solve.py`: оси семейства → граф замен → корзина → `why[]`. Новые поля дают чем заполнять `intent=fast` без лжи, чем отличать «нет петрушки» от «нет соды», чем предложить грудку вместо отсева.

### Покрытие каталога

Валидность одной карточки ≠ полезность калькулятора. Десять идеальных JSON про «курица + духовка + сливки» оставят пустым «сковорода / без молока / 20 минут».

[RECIPE-INVENTORY.md](../RECIPE-INVENTORY.md) в будущем — не только ниши VOCAB, а **матрица ситуаций**: быстро; из базовой корзины; одна посуда; без молочного; конкретный белок; конкретная крупа; batch. Волна закрывает дыры матрицы, не плодит четвёртую целую курицу.

При переработке 43 не заполнять адаптации «чтобы было». Пустой `adaptation_rules` честнее выдуманного `oven → pan_fry`.

### Чего не делать

- Вариант на 1/2/3/4 персоны и «без каждого optional» — взрыв данных.
- Runtime-догадка «наверное пожарить». Нет правила — нет перехода.
- Глобальная замена без `conditions` / роли («сливки всегда = сметана»).
- Десять новых axis в UI.
- `quality` без модерации как «вкуснее».
- Профили времени, которых нет в шагах (для 43 — не врать; для новых — обязательны).

---

## 5. Правила генерации новых

Вход: **input packet** (ниша, белок, метод, диета, ограничения, **какие ситуации закрыть**: быстро / одна посуда / без молока / batch…). Нет packet — вернуть `{ "error": "чего не хватает" }`, не выдумывать бриф. Факты только из packet. Не выдумывать URL, таймкоды, бренды, редкие продукты, адаптации и минуты.

Конвейер: автор (один JSON: карточка **и** пространство адаптаций) → скрипт-валидатор → модератор (accept / полный revise / reject). Автор не ставит `editorial_tested`. Runtime не дописывает правила.

### 5.1 Карточка

- `id` = транслит русского `title`, не перевод (`kurinaya-grudka-…`, не `classic-roast-chicken`).
- Оси только из VOCAB. Не писать `duhovka`, `skovoroda`, `kastryulya`, `tushenie`. Жапка не живёт в `dish_type`.
- `protein_base`: омлет → `eggs_dairy`; креветки → `seafood`; печень → `offal`; рагу из кабачков → `vegetables`; нут как основа → `legumes`. Код `vegetarian` — не для новых (оставлен ETL V1).
- Одно блюдо = один `id`. Добавки — `content`-вариант. Другая посуда / быстрее / полегче — `execution` / `profile` **или** `adaptation_rule`, не второй файл.
- `energy_profile` базы = `standard`. `light`/`rich` — profile-вариант, не сосед аддона «с грибами». Без ккал. Не подменять блюдо.
- High-risk: флаги из SAFETY + `caution_text`. Без человека в каталог нельзя. Сырой белок при `no_cook` без `raw_*` — ошибка.

### 5.2 Ингредиенты

- Объект с `canonical_id`. Нет канона в сиде — блок `new_ingredients` (title, aliases, три списка аллергенов). Regex по падежам запрещён.
- Единицы только enum. Стакан не писать. `tsp`=5 ml, `tbsp`=15 ml в уме, в JSON — ложки, не дублировать мл, кроме пояснения в `detail`.
- Primary (основа блюда) — с количеством. Нет граммов у якоря и нет `servings` → масштаб выключен; лучше дать граммы белку, чем выдумать порции.
- `choice_group` для явного «A или B» в базе. Остальные замены — `adaptation_rule` + `ingredient_role`.
- На каждой строке: `ingredient_role`; `required` / `substitutable` / `removable` (см. §4A). «Для подачи» → не required, removable.
- Соль/специи: `gentle`. Сода/химия: `manual`, обычно `substitutable: false`, `removable: false`. Штучные яйца/лавр/чеснок: `whole`.
- Один `is_anchor`. Добавки и адаптации якорь не ставят, пока не заменяют якорный продукт.

### 5.3 Шаги

- Только объекты `{ "text": "…" }`. Единый стиль: инфинитив **или** повелительное, не смесь.
- Таймер — `timer_seconds`, не `timer_min`.
- Птица: грудка 72 °C, бедро/голень 82 °C, фарш птицы 74 °C. Рыба готовая 63 °C. Фарш млекопитающих 71 °C. Свинина цельным куском: 63 °C + `hold_seconds` ≥ 180 **или** 71 °C. Валидатор смотрит `target`, не `pull`.
- `pan_fry`: в шаге жарки — не перегружать сковороду (`equipment_note` или явная фраза).

### 5.4 Варианты и адаптации

- Сначала пространство адаптаций (§4A), потом аддоны. Нет сливок / нет духовки / филе вместо бедра — правила, не чип «с перцем».
- `content` (addon): 0–4 чипа, взаимоисключающие. Состав меняется → `has_delta: true` + дельты + **обязательный** `allergen_delta`.
- `execution` / `profile`: только если автор собрал полноценную версию (`fast`, `one_pan`, `light`) с дельтой и `when`.
- `step_delta`: `replace` по `position`, `insert` после `after_position`. **`remove` шага нет.**
- Смена посуды или метода без чипа на странице — `adaptation_rule` type `equipment` \| `method`, не абзац в notes. Нет правила — калькулятор переход не предлагает.
- Грибы: только whitelist (шампиньоны, вешенки, шиитаке, эринги). Иное → `wild_mushrooms` + человек.
- Текст `variations[].text` для новых **запрещён**, если меняется состав.
- Обязательны у новых: `time_profile`, `effort`, `equipment_profile`, `shopping_profile`, хотя бы ядро `adaptation_rules` (пустой массив допустим, если честно нечего разрешить — не выдумывать).

### 5.5 Заметки и provenance

- `notes`: min 3, цель 6, max 10. Сложное тушение — к верхней границе. Не вода ради числа.
- Класть: подготовка белка, обжарка да/нет, бульон vs вода, специи «можно», типичная ошибка. Не дублировать шаги. Посуду — только если это не ось варианта.
- Чужой текст: `source_name` + `source_url`. Выдуманный URL/таймкод — Critical.

### 5.6 Чего не делать

- Runtime-советы «а ещё можно с грибами» без дельты и «наверное пожарить» без `adaptation_rule`.
- Второй slug «в казане» / «диетическая версия» / «на 2 порции» / «без чеснока».
- Глобальные замены без роли и условий.
- `unknown` объявить «нет».
- Вешать `milk`/`gluten` на «бульон или вода».
- Креветку кодировать как `fish`.
- `scale_mode: "fixed"` / поле `scalable_rule` — их нет; фиксированное = `scalable: false`.
- `gentle` по формуле V1 JS `1+(ratio-1)*0.5`.
- Писать в корневой `data/recipes/` и стартовать волну без команды человека.

---

## 6. Ворота качества (для ревьюера)

| Уровень | Пример |
|---------|--------|
| **Critical** | температура птицы/фарша ниже SAFETY; `unknown` → «нет»; выдуманный URL; `sol-chef.ru` как внешний источник; чужой текст без ссылки; high-risk без «Осторожно» |
| **Major** | нет количеств у primary; сломана диета packet; пропущен ключевой шаг; вариация текстом при смене состава; второй slug; посуда только в notes; сода `gentle`; нет `canonical_id`; стакан в JSON; у нового нет `time_profile` / ролей; замена без `allergen_delta`; `removable` на соде/химии бархатования; выдуманный `oven→pan_fry` |
| **Minor** | смесь инфинитива и императива; пустые заметки ради квоты; notes = копия шага; лишний тег; английщина в UI-подписях отрубов; аддоны есть, а правил замен нет при очевидном packet «без сливок» |

Неисправленный Critical = не принимать. Средняя оценка воспроизводимости ≥ 4.0.

---

## 7. Что улучшить в самом генераторе (запрос к анализу)

Имеющийся конвейер V1 (`docs/ADD_RECIPE.md`) учит вредному: `gentle` для соды, вариации абзацем, русские единицы, папки вместо VOCAB, температура в прозе, `tags` вместо осей, `timer_min`. Текущий RECIPE.md учит валидной карточке, но не кулинарной **модели для подбора**.

Просьба к анализу — не пересказывать этот файл, а предложить:

1. **Схему JSON автора** (один объект, jsonschema): обязательные поля, запрещённые ключи V1 (`tags`, `category`, `timer_min`, `variations[].text` при смене состава), enum из VOCAB **и** поля §4A (`ingredient_role`, availability, профили, `adaptation_rules`).
2. **Системный промпт автора** (Grok) и **промпт модератора** (Luna) так, чтобы пример §2 без правок не проходил, пример §3 проходил как карточка, а без §4A модератор требовал revise («нет пространства адаптаций»).
3. **Чеклист валидатора** (скрипт, не модель): оси, единицы, сода=`manual`, якорь ≤ 1, target у птицы/свинины/рыбы, `allergen_delta` если есть `ingredient_delta` или substitution, нет `duhovka`, нет стакана, нет `sol-chef.ru`; у новых — роли, `time_profile`, не `removable` на химии; `quality` в диапазоне; adaptation `method`/`equipment` только с override и дельтой шагов.
4. **Packet**: минимальные поля, без которых автор обязан вернуть `error`. В том числе какие **ситуации** рецепт должен закрыть (fast / pantry / one pan / dairy-free…).
5. **Правило `new_ingredients`**: как регистрировать канон, которого ещё нет в сиде, чтобы не разъехались аллергены.
6. Где генератор должен **отказаться** (мало данных, high-risk без допуска, лесные грибы, сырая рыба без проморозки в тексте, адаптация без опоры в packet).
7. Стык с текущим `SubstitutionRule` + `solve.py`: что остаётся глобальным сидом, что обязано жить на рецепте, как не сломать порог `quality` и `forbidden`.
8. Автор описывает **не только рецепт, но и пространство допустимых адаптаций**: что заменить, что убрать, какие методы/посуду/белок можно сменить, какие режимы исполнения есть и **при каких условиях** (`when`, `conditions`, `quality`).
9. **Адаптация не придумывается в runtime.** Калькулятор использует только заранее разрешённые автором и модератором правила. Нет правила — нет перехода, даже если «похоже».

Философия RECIPE.md, к которой сдвинуть канон после анализа:

не «генерируем рецепты»,  
а «генерируем структурированные кулинарные модели, из которых калькулятор безопасно собирает персональные решения».

Покрытие каталога (позже, RECIPE-INVENTORY): матрица пользовательских ситуаций, не только ниши VOCAB.

Канон при конфликте с этим брифом: RECIPE → SAFETY → VOCAB → DATA-MODEL → CALCULATOR. Пустая ячейка HUMAN ≠ «да». В канон уже вошли: `time_profile`, effort/washing, `use_cases`, `adaptations[]`, реестр Ingredient (DEC-020). Роли `ingredient_role` / `required` на каждой строке из этого §4A — ещё бриф, не Postgres.
