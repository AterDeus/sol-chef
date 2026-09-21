# Бэкенд sol-chef 2.0 — приложение recipes — дамп для аудита

Снимок кода на 2026-09-20.
Источник: `v2/backend/apps/recipes/`.
Каталог, карточка, поиск, солвер калькулятора, ETL, масштабирование порций, аллергены, КБЖУ.

Правило раскладки: **один файл = содержимое одного исходного `.py`**.
Заголовок блока — путь относительно `v2/`. Ниже — классы и функции верхнего уровня и полный исходник.
Не входят: `migrations/`, `__pycache__/`, пустые `__init__.py`.

## Оглавление

| # | Файл | Классы и функции | Строк |
|---|------|------------------|------:|
| 1 | `backend/apps/recipes/admin.py` | `RecipeIngredientInline`, `RecipeStepInline`, `RecipeVariantInline`, `RecipeAdmin`, `IngredientAdmin`, `RecipeVariantAdmin`, `SubstitutionRuleAdmin`, `RecipeRevisionAdmin` | 71 |
| 2 | `backend/apps/recipes/apps.py` | `RecipesConfig` | 8 |
| 3 | `backend/apps/recipes/constants.py` | `label_equipment_axis`, `slugify_ru` | 401 |
| 4 | `backend/apps/recipes/etl/__init__.py` | — | 1 |
| 5 | `backend/apps/recipes/etl/_gen_ingredient_map.py` | `e`, `main` | 182 |
| 6 | `backend/apps/recipes/etl/draft.py` | `DraftError`, `load_json`, `validate_draft`, `parse_draft`, `known_from_v1_map`, `load_review`, `review_allows_import` | 782 |
| 7 | `backend/apps/recipes/etl/ingredients.py` | `parse_amount`, `map_unit_and_amount`, `infer_scale_mode`, `is_anchor_candidate`, `is_optional_line` | 95 |
| 8 | `backend/apps/recipes/etl/load.py` | `V1ImportError`, `resolve_v1_root`, `read_index`, `load_recipe_objects`, `folder_from_rel` | 62 |
| 9 | `backend/apps/recipes/etl/nutrition.py` | `seed_path`, `load_seed`, `load_ingredient_nutrition` | 82 |
| 10 | `backend/apps/recipes/etl/serialize.py` | `recipe_to_draft` | 129 |
| 11 | `backend/apps/recipes/etl/taxonomy.py` | — | 105 |
| 12 | `backend/apps/recipes/etl/upsert.py` | `upsert_recipe` | 148 |
| 13 | `backend/apps/recipes/exceptions.py` | `api_exception_handler` | 13 |
| 14 | `backend/apps/recipes/management/commands/audit_core_ids.py` | `Command` | 35 |
| 15 | `backend/apps/recipes/management/commands/export_draft.py` | `Command` | 42 |
| 16 | `backend/apps/recipes/management/commands/import_draft.py` | `Command`, `drafts_root`, `v1_map_path` | 123 |
| 17 | `backend/apps/recipes/management/commands/import_v1.py` | `Command`, `run_import` | 359 |
| 18 | `backend/apps/recipes/management/commands/rebuild_axis_snapshots.py` | `Command` | 20 |
| 19 | `backend/apps/recipes/models.py` | `NormalizeRu`, `ToTsVector`, `Recipe`, `RecipeVariant`, `RecipeRevision`, `Ingredient`, `RecipeIngredient`, `SubstitutionRule`, `RecipeStep` | 383 |
| 20 | `backend/apps/recipes/pantry_vocab.py` | `shopping_ids`, `shopping_label`, `likely_items_for_have_group`, `items_for_have_group`, `groups_to_expand`, `availability_class` | 729 |
| 21 | `backend/apps/recipes/query.py` | `BadQuery`, `split_query_values`, `parse_codes`, `parse_optional_code`, `parse_have`, `parse_have_groups`, `parse_intent`, `parse_without_allergens`, `parse_sample`, `parse_optional_decimal` | 157 |
| 22 | `backend/apps/recipes/serializers.py` | `catalog_scaling`, `serialize_recipe_list_item`, `serialize_display_line`, `serialize_display_step`, `serialize_recipe_detail` | 185 |
| 23 | `backend/apps/recipes/services/__init__.py` | — | 1 |
| 24 | `backend/apps/recipes/services/allergens.py` | `merge_allergen_lists`, `recipe_allergens_from_ingredients`, `normalize_ru` | 41 |
| 25 | `backend/apps/recipes/services/assemble.py` | `VariantError`, `AssembledRecipe`, `lines_from_recipe`, `allergen_lines_from_recipe`, `steps_from_recipe`, `apply_ingredient_delta`, `apply_step_delta`, `apply_allergen_delta`, `allergens_from_lines`, `apply_high_risk`, `count_anchors`, `pick_anchor`, `available_equipment_codes`, `resolve_axes`, `assemble_display`, `assemble_recipe`, `catalog_allergens`, `catalog_protein_bases`, `catalog_protein_variants` | 572 |
| 26 | `backend/apps/recipes/services/notes.py` | `split_notes_blob`, `normalize_notes` | 36 |
| 27 | `backend/apps/recipes/services/nutrition.py` | `line_skipped`, `nutrition_skip_hint`, `has_full_macros`, `grams_per_unit`, `line_nutrition_factor`, `nutrition_line_projection`, `compute_recipe_nutrition`, `enrich_lines_from_db` | 241 |
| 28 | `backend/apps/recipes/services/pantry.py` | `norm_ru`, `split_pantry_text`, `expand_have_group`, `pantry_universe`, `resolve_token`, `resolve_pantry_text` | 92 |
| 29 | `backend/apps/recipes/services/ranking.py` | `score_and_why` | 45 |
| 30 | `backend/apps/recipes/services/scale.py` | `ScaleConflict`, `ScaleResult`, `round_scaled`, `apply_mode`, `format_display_amount`, `base_anchor_amount`, `resolve_scale`, `scale_line` | 216 |
| 31 | `backend/apps/recipes/services/search.py` | `PgNormalizeRu`, `Similarity`, `apply_catalog_search` | 35 |
| 32 | `backend/apps/recipes/services/snapshots.py` | `snapshot_from_assembled`, `snapshot_fits`, `refresh_axis_snapshots` | 78 |
| 33 | `backend/apps/recipes/services/solve.py` | `CookingSolution`, `is_core_line`, `is_desirable_line`, `combo_method_equipment`, `combo_time_minutes`, `intent_adjust`, `combo_protein_bases`, `combo_fits`, `axis_combos`, `match_pantry`, `pantry_score`, `pantry_why`, `protein_from_pantry`, `axes_why`, `solve_recipe`, `is_standalone_dish`, `assign_buckets`, `build_board`, `serialize_solution` | 701 |
| 34 | `backend/apps/recipes/services/substitutions.py` | `SubRule`, `load_seed_rows`, `upsert_substitution_rules`, `rules_for_recipe`, `stored_rules_from_db`, `cover_need` | 104 |
| 35 | `backend/apps/recipes/urls.py` | — | 15 |
| 36 | `backend/apps/recipes/views.py` | `CatalogPagination`, `RecipeListView`, `RecipeDetailView`, `IngredientListView`, `RecommendationListView` | 439 |

Всего файлов: **36**. Строк исходников: **6728**.

---

## 1. `backend/apps/recipes/admin.py`

- Путь: `v2/backend/apps/recipes/admin.py`
- Классы и функции: RecipeIngredientInline, RecipeStepInline, RecipeVariantInline, RecipeAdmin, IngredientAdmin, RecipeVariantAdmin, SubstitutionRuleAdmin, RecipeRevisionAdmin
- Строк: 71

```python
from django.contrib import admin

from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRevision,
    RecipeStep,
    RecipeVariant,
    SubstitutionRule,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 0


class RecipeVariantInline(admin.TabularInline):
    model = RecipeVariant
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
        "protein_base",
        "cook_method",
        "dish_type",
        "equipment",
        "status",
        "editorial_tested",
    )
    list_filter = ("protein_base", "cook_method", "dish_type", "equipment", "status")
    search_fields = ("slug", "title")
    inlines = [RecipeIngredientInline, RecipeStepInline, RecipeVariantInline]
    readonly_fields = ("search_vector", "updated_at")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("canonical_id", "title")
    search_fields = ("canonical_id", "title")


@admin.register(RecipeVariant)
class RecipeVariantAdmin(admin.ModelAdmin):
    list_display = ("recipe", "axis", "code", "has_delta")
    list_filter = ("axis", "has_delta")


@admin.register(SubstitutionRule)
class SubstitutionRuleAdmin(admin.ModelAdmin):
    list_display = ("from_ingredient", "to_ingredient", "quality", "forbidden", "recipe")
    list_filter = ("forbidden",)
    search_fields = (
        "from_ingredient__canonical_id",
        "to_ingredient__canonical_id",
    )


@admin.register(RecipeRevision)
class RecipeRevisionAdmin(admin.ModelAdmin):
    list_display = ("recipe", "status", "created_at")
```

---

## 2. `backend/apps/recipes/apps.py`

- Путь: `v2/backend/apps/recipes/apps.py`
- Классы и функции: RecipesConfig
- Строк: 8

```python
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.recipes"
    label = "recipes"
    verbose_name = "Recipes"
```

---

## 3. `backend/apps/recipes/constants.py`

- Путь: `v2/backend/apps/recipes/constants.py`
- Классы и функции: label_equipment_axis, slugify_ru
- Строк: 401

```python
"""VOCAB codes and display labels (API UI strings in Russian)."""

from __future__ import annotations

PROTEIN_BASE = frozenset(
    {
        "beef",
        "pork",
        "poultry",
        "lamb",
        "fish_white_sea",
        "fish_red_sea",
        "fish_river",
        "fish_canned",
        "seafood",
        "offal",
        "eggs_dairy",
        "vegetarian",
        "vegetables",
        "mushrooms",
        "legumes",
        "fruits",
    }
)

COOK_METHOD = frozenset(
    {
        "oven",
        "pan_fry",
        "stew",
        "boil",
        "grill",
        "steam",
        "no_cook",
        "air_fryer",
        "deep_fry",
    }
)

DISH_TYPE = frozenset(
    {
        "main",
        "soup",
        "salad",
        "appetizer",
        "breakfast",
        "side",
        "pasta_grains",
        "bakery",
        "dessert",
        "sauce",
        "drink",
        "preserve",
    }
)

# Not a plate of food: compound butter, flavored oil, fried onions, jam.
# Calculator "what should I cook" skips these while a standalone dish exists.
COMPONENT_DISH_TYPES = frozenset({"sauce", "preserve"})

SCALE_MODE = frozenset({"linear", "gentle", "whole", "manual"})

UNIT = frozenset(
    {
        "g",
        "kg",
        "ml",
        "l",
        "pcs",
        "tsp",
        "tbsp",
        "pinch",
        "clove",
        "bunch",
        "slice",
        "to_taste",
    }
)

ALLERGEN = frozenset(
    {
        "gluten",
        "milk",
        "egg",
        "fish",
        "crustacean",
        "mollusc",
        "peanut",
        "tree_nut",
        "soy",
        "sesame",
        "mustard",
        "celery",
        "sulfite",
        "lupin",
    }
)

HIGH_RISK = frozenset(
    {
        "raw_egg",
        "raw_meat",
        "raw_fish",
        "raw_milk",
        "wild_mushrooms",
        "ground_meat",
        "preservation",
        "fermentation",
        "child_food",
        "fire_hazard",
        "poultry_temp",
    }
)

ENERGY_PROFILE = frozenset({"standard", "light", "rich"})

NUTRITION_BASIS = frozenset({"raw_100g"})

YIELD_KIND = frozenset({"estimated", "exact"})

NUTRITION_SOURCE = frozenset(
    {"fooddata_central", "ru_table", "packaging_typical", "editorial"}
)

EQUIPMENT = frozenset(
    {
        "pot",
        "oven",
        "kazan",
        "skillet",
        "saucepan",
        "baking_dish",
        "grill",
    }
)

CUT = frozenset(
    {
        "shank",
        "shoulder",
        "neck",
        "rump",
        "brisket",
        "thick_rib",
        "tenderloin",
        "loin",
        "belly",
        "ribs",
        "mince",
        "breast",
        "thigh",
        "drumstick",
        "wing",
        "whole_bird",
    }
)

VARIANT_AXIS = frozenset({"addon", "equipment", "energy"})

USE_CASE = frozenset(
    {
        "fast",
        "easy",
        "pantry",
        "one_pan",
        "batch",
        "budget",
        "light",
    }
)

ADAPTATION_TYPE = frozenset({"substitution", "omission", "equipment", "method"})

USE_CASE_LABEL_RU = {
    "fast": "быстро",
    "easy": "просто",
    "pantry": "из запасов",
    "one_pan": "одна посуда",
    "batch": "заготовка",
    "budget": "дешевле",
    "light": "полегче",
}

MAX_VARIANTS = 10

RECIPE_STATUS = frozenset({"draft", "in_review", "approved", "published"})

PROTEIN_BASE_LABEL_RU = {
    "beef": "говядина",
    "pork": "свинина",
    "poultry": "птица",
    "lamb": "баранина",
    "fish_white_sea": "белая морская рыба",
    "fish_red_sea": "красная рыба",
    "fish_river": "речная рыба",
    "fish_canned": "консервированная рыба",
    "seafood": "морепродукты",
    "offal": "субпродукты",
    "eggs_dairy": "яйца и молочные",
    "vegetarian": "растительная",
    "vegetables": "овощи",
    "mushrooms": "грибы",
    "legumes": "бобовые",
    "fruits": "фрукты",
}

COOK_METHOD_LABEL_RU = {
    "oven": "духовка",
    "pan_fry": "сковорода",
    "stew": "тушение",
    "boil": "варка",
    "grill": "гриль",
    "steam": "пар",
    "no_cook": "без термообработки",
    "air_fryer": "аэрогриль",
    "deep_fry": "фритюр",
}

EQUIPMENT_LABEL_RU = {
    "pot": "кастрюля",
    "oven": "духовка",
    "kazan": "казан",
    "skillet": "сковорода",
    "saucepan": "сотейник",
    "baking_dish": "форма",
    "grill": "гриль",
}


def label_equipment_axis(code: str) -> str:
    """Vessel label, or cook_method for method-only family codes (air_fryer, steam)."""
    return EQUIPMENT_LABEL_RU.get(code) or COOK_METHOD_LABEL_RU.get(code, code)

CUT_LABEL_RU = {
    "shank": "голяшка",
    "shoulder": "лопатка",
    "neck": "шея",
    "rump": "огузок",
    "brisket": "грудинка",
    "thick_rib": "толстый край",
    "tenderloin": "вырезка",
    "loin": "корейка",
    "belly": "брюшина",
    "ribs": "рёбра",
    "mince": "фарш",
    "breast": "грудка",
    "thigh": "бедро",
    "drumstick": "голень",
    "wing": "крыло",
    "whole_bird": "целиком",
}

_CYR_TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "i",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def slugify_ru(title: str, *, used: set[str] | None = None) -> str:
    """ASCII slug from a Russian title (RecipeVariant.code)."""
    from django.utils.text import slugify

    mapped = "".join(_CYR_TRANSLIT.get(ch.lower(), ch) for ch in title or "")
    code = slugify(mapped, allow_unicode=False)[:80] or "variant"
    if used is None:
        return code
    base = code
    n = 2
    while code in used:
        suffix = f"-{n}"
        code = f"{base[: 80 - len(suffix)]}{suffix}"
        n += 1
    used.add(code)
    return code


UNIT_LABEL_RU = {
    "g": "г",
    "kg": "кг",
    "ml": "мл",
    "l": "л",
    "pcs": "шт",
    "tsp": "ч. л.",
    "tbsp": "ст. л.",
    "pinch": "щепотка",
    "clove": "зубчик",
    "bunch": "пучок",
    "slice": "ломтик",
    "to_taste": "по вкусу",
}

V1_FOLDER_TO_COOK_METHOD = {
    "duhovka": "oven",
    "skovoroda": "pan_fry",
    "tushenie": "stew",
    "kastryulya": "boil",
    "grill": "grill",
}

V1_FOLDER_TO_EQUIPMENT = {
    "duhovka": "oven",
    "skovoroda": "skillet",
    "tushenie": "pot",
    "kastryulya": "pot",
    "grill": "grill",
}

# V1 Russian unit string → VOCAB. Extra countable units map to pcs.
# «стакана» is converted to ml (×250) in the importer, not stored as cup.
V1_UNIT_TO_VOCAB = {
    "г": "g",
    "кг": "kg",
    "мл": "ml",
    "л": "l",
    "шт": "pcs",
    "ч. л.": "tsp",
    "ст. л.": "tbsp",
    "зубчик": "clove",
    "зубчика": "clove",
    "зубчиков": "clove",
    "ломтика": "slice",
    "пучок": "bunch",
    "щепотка": "pinch",
    "по вкусу": "to_taste",
    "банка": "pcs",
    "стебля": "pcs",
    "стручков": "pcs",
    "порции": "pcs",
    "листиков": "pcs",
    "полоски": "pcs",
}

EXPECTED_RECIPE_COUNT = 43
EXPECTED_RECIPE_FILES = 19
EXPECTED_CONTENT_DOCUMENTS = 5

MEAT_CUTS = frozenset({"beef", "pork", "poultry"})

SUBSTITUTION_QUALITY_MIN = 0.50
BEST_BUCKET_LIMIT = 5

from apps.recipes.pantry_vocab import (  # noqa: E402
    CANONICAL_INGREDIENT_LABEL_RU,
    HAVE_GROUP_LABEL_RU,
    HAVE_GROUPS,
    HAVE_TEXT_ALIASES,
    HAVE_UI_GROUPS,
    PANTRY_ASSUMED,
    PANTRY_COMMON,
    PANTRY_EXOTIC,
    PANTRY_LEGACY_OR,
    PANTRY_SPICES,
    SHOPPING_GROUPS,
    SHOPPING_GROUP_LABEL_RU,
)

# Old name: shopping taxonomy, not the first-screen chips.
PANTRY_CHIP_GROUPS = SHOPPING_GROUPS

INTENT = frozenset({"fast", "pantry", "oven", "light", "easy", "batch"})

INTENT_LABEL_RU = {
    "fast": "Быстро",
    "pantry": "Из того, что есть",
    "oven": "В духовке",
    "light": "Полегче",
    "easy": "Проще",
    "batch": "На несколько дней",
}
```

---

## 4. `backend/apps/recipes/etl/__init__.py`

- Путь: `v2/backend/apps/recipes/etl/__init__.py`
- Классы и функции: нет классов/функций верхнего уровня
- Строк: 1

```python
# ETL helpers
```

---

## 5. `backend/apps/recipes/etl/_gen_ingredient_map.py`

- Путь: `v2/backend/apps/recipes/etl/_gen_ingredient_map.py`
- Классы и функции: e, main
- Строк: 182

```python
"""Generate v1_ingredient_map.json from exact V1 ingredient name strings."""

from __future__ import annotations

import json
from pathlib import Path


def e(canonical_id, title, contains=None, may_contain=None, unknown=None):
    return {
        "canonical_id": canonical_id,
        "title": title,
        "contains": contains or [],
        "may_contain": may_contain or [],
        "unknown": unknown or [],
    }


# Named store stock: celery is often undeclared (SAFETY). Do not hang milk/gluten —
# that made every stew look like it might contain milk.
BROTH_CELERY = ["celery"]

MAP = {
    "базилик свежий": e("fresh_basil", "базилик свежий"),
    "бальзамический уксус": e("balsamic_vinegar", "бальзамический уксус"),
    "баранья лопатка": e("lamb_shoulder", "баранья лопатка"),
    "бекон": e("bacon", "бекон"),
    "белое вино": e("white_wine", "белое вино", contains=["sulfite"]),
    "бульон": e("stock", "бульон", unknown=BROTH_CELERY),
    "бульон или вода": e("stock_or_water", "бульон или вода"),
    "бульон овощной": e("vegetable_stock", "бульон овощной", unknown=BROTH_CELERY),
    "бёдра куриные": e("chicken_thighs", "бёдра куриные"),
    "ванильное мороженое": e("vanilla_ice_cream", "ванильное мороженое", contains=["milk"], unknown=["egg"]),
    "ветчина": e("ham", "ветчина"),
    "вода": e("water", "вода"),
    "Вода": e("water", "вода"),
    "вода и яблочный уксус": e("water_and_apple_vinegar", "вода и яблочный уксус"),
    "вода или бульон": e("water_or_stock", "вода или бульон"),
    "гарам масала": e("garam_masala", "гарам масала"),
    "гвоздика": e("cloves", "гвоздика"),
    "глутамат натрия": e("msg", "глутамат натрия"),
    "говядина": e("beef", "говядина"),
    "говяжий огузок": e("beef_rump", "говяжий огузок"),
    "говяжьи рёбра": e("beef_ribs", "говяжьи рёбра"),
    "говяжья голяшка на кости": e("beef_shank_bone_in", "говяжья голяшка на кости"),
    "говяжья лопатка": e("beef_chuck", "говяжья лопатка"),
    "горошек": e("green_peas", "горошек"),
    "горчица": e("mustard", "горчица", contains=["mustard"]),
    "Горчица": e("mustard", "горчица", contains=["mustard"]),
    "Грецкие орехи": e("walnuts", "грецкие орехи", contains=["tree_nut"]),
    "гречка": e("buckwheat", "гречка"),
    "зелёный лук": e("green_onion", "зелёный лук"),
    "зира": e("cumin", "зира"),
    "имбирная паста": e("ginger_paste", "имбирная паста"),
    "имбирь": e("ginger", "имбирь"),
    "йогурт": e("yogurt", "йогурт", contains=["milk"]),
    "кабачки": e("zucchini", "кабачки"),
    "кардамон": e("cardamom", "кардамон"),
    "Картофель": e("potato", "картофель"),
    "кашмирский чили": e("kashmiri_chili", "кашмирский чили"),
    "кинза": e("cilantro", "кинза"),
    "кориандр": e("coriander", "кориандр"),
    "корица": e("cinnamon", "корица"),
    "красное вино или бальзамический уксус": e(
        "red_wine_or_balsamic", "красное вино или бальзамический уксус", contains=["sulfite"]
    ),
    "кукуруза": e("corn", "кукуруза"),
    "кукурузный крахмал": e("corn_starch", "кукурузный крахмал"),
    "Кукурузный крахмал": e("corn_starch", "кукурузный крахмал"),
    "кулинарная нить": e("butcher_twine", "кулинарная нить"),
    "кумин": e("cumin", "кумин"),
    "кунжут": e("sesame", "кунжут", contains=["sesame"]),
    "Куриная грудка": e("chicken_breast", "куриная грудка"),
    "куриные бедра": e("chicken_thighs", "куриные бедра"),
    "курица": e("whole_chicken", "курица"),
    "куркума": e("turmeric", "куркума"),
    "кусок свиной шеи": e("pork_neck", "кусок свиной шеи"),
    "Лавровый лист": e("bay_leaf", "лавровый лист"),
    "лавровый лист": e("bay_leaf", "лавровый лист"),
    "Лимон": e("lemon", "лимон"),
    "лимон": e("lemon", "лимон"),
    "лук": e("onion", "лук"),
    "Лук": e("onion", "лук"),
    "лук-шалот": e("shallot", "лук-шалот"),
    "Миндаль": e("almond", "миндаль", contains=["tree_nut"]),
    "минеральная вода сильногазированная": e("sparkling_mineral_water", "минеральная вода сильногазированная"),
    "морковь": e("carrot", "морковь"),
    "Морковь": e("carrot", "морковь"),
    "мука": e("wheat_flour", "мука", contains=["gluten"]),
    "мука и вода": e("flour_and_water_dough", "мука и вода", contains=["gluten"]),
    "мята": e("mint", "мята"),
    "мёд": e("honey", "мёд"),
    "Овощной бульон": e("vegetable_stock", "овощной бульон", unknown=BROTH_CELERY),
    "Огурец": e("cucumber", "огурец"),
    "оливковое масло": e("olive_oil", "оливковое масло"),
    "Оливковое масло": e("olive_oil", "оливковое масло"),
    "паприка": e("paprika", "паприка"),
    "Паприка": e("paprika", "паприка"),
    "пармезан": e("parmesan", "пармезан", contains=["milk"]),
    "Перец": e("black_pepper", "перец"),
    "перец": e("black_pepper", "перец"),
    "петрушка": e("parsley", "петрушка"),
    "пищевая сода": e("baking_soda", "пищевая сода"),
    "Помидоры": e("tomato", "помидоры"),
    "помидоры": e("tomato", "помидоры"),
    "Растительное масло": e("vegetable_oil", "растительное масло"),
    "растительное масло": e("vegetable_oil", "растительное масло"),
    "репчатый лук": e("onion", "репчатый лук"),
    "рибай": e("ribeye", "рибай"),
    "рис": e("rice", "рис"),
    "розмарин": e("rosemary", "розмарин"),
    "Салатный микс": e("salad_mix", "салатный микс"),
    "сахар": e("sugar", "сахар"),
    "сахарная пудра": e("powdered_sugar", "сахарная пудра"),
    "свиная шея (ошеек)": e("pork_neck", "свиная шея"),
    "сливочное и оливковое масло": e("butter_and_olive_oil", "сливочное и оливковое масло", contains=["milk"]),
    "сливочное масло": e("butter", "сливочное масло", contains=["milk"]),
    "соевый соус": e("soy_sauce", "соевый соус", contains=["soy", "gluten"]),
    "Соль": e("salt", "соль"),
    "соль": e("salt", "соль"),
    "соль крупная": e("coarse_salt", "соль крупная"),
    "соус или подлива": e("gravy", "соус или подлива"),
    "спагетти": e("spaghetti", "спагетти", contains=["gluten"]),
    "спаржа": e("asparagus", "спаржа"),
    "стейк": e("steak", "стейк"),
    "Судак": e("zander", "судак", contains=["fish"]),
    "сушёный розмарин": e("dried_rosemary", "сушёный розмарин"),
    "сушёный тимьян": e("dried_thyme", "сушёный тимьян"),
    "сыр": e("cheese", "сыр", contains=["milk"]),
    "Сыр твёрдый": e("hard_cheese", "сыр твёрдый", contains=["milk"]),
    "тимьян": e("thyme", "тимьян"),
    "тимьян или розмарин": e("thyme_or_rosemary", "тимьян или розмарин"),
    "томатная паста": e("tomato_paste", "томатная паста"),
    "Томатное пюре": e("tomato_puree", "томатное пюре"),
    "томатное пюре": e("tomato_puree", "томатное пюре"),
    "томаты": e("tomato", "томаты"),
    "Укроп": e("dill", "укроп"),
    "укроп": e("dill", "укроп"),
    "Уксус": e("vinegar", "уксус"),
    "уксус 9%": e("vinegar_9", "уксус 9%"),
    "Фасоль консервированная": e("canned_beans", "фасоль консервированная"),
    "филе лосося": e("salmon_fillet", "филе лосося", contains=["fish"]),
    "филе форели": e("trout_fillet", "филе форели", contains=["fish"]),
    "хлеб": e("bread", "хлеб", contains=["gluten"]),
    "хлопья перца": e("chili_flakes", "хлопья перца"),
    "хлопья чили": e("chili_flakes", "хлопья чили"),
    "черный перец": e("black_pepper", "чёрный перец"),
    "чеснок": e("garlic", "чеснок"),
    "Чеснок": e("garlic", "чеснок"),
    "чесночная паста": e("garlic_paste", "чесночная паста"),
    "чили": e("chili", "чили"),
    "чёрный перец": e("black_pepper", "чёрный перец"),
    "Чёрный перец": e("black_pepper", "чёрный перец"),
    "чёрный перец свежемолотый": e("fresh_black_pepper", "чёрный перец свежемолотый"),
    "шампиньоны": e("champignons", "шампиньоны"),
    "шафран": e("saffron", "шафран"),
    "шоколад": e("dark_chocolate", "шоколад", may_contain=["milk"]),
    "яблоки": e("apple", "яблоки"),
    "яичный белок": e("egg_white", "яичный белок", contains=["egg"]),
    "яйца": e("eggs", "яйца", contains=["egg"]),
    "яйцо": e("egg", "яйцо", contains=["egg"]),
}


def main() -> None:
    names_path = Path(__file__).resolve().parents[3] / "_scan_v1_out.txt"
    names: list[str] = []
    if names_path.is_file():
        text = names_path.read_text(encoding="utf-8")
        section = text.split("---NAMES---", 1)[1]
        names = [line for line in section.strip().splitlines() if line]
    missing = [n for n in names if n not in MAP]
    extra = [k for k in MAP if names and k not in names]
    if missing:
        raise SystemExit("Missing names:\n" + "\n".join(missing))
    out = Path(__file__).resolve().parents[1] / "fixtures" / "v1_ingredient_map.json"
    out.write_text(json.dumps(MAP, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} keys={len(MAP)} scanned={len(names)} extra={extra}")


if __name__ == "__main__":
    main()
```

---

## 6. `backend/apps/recipes/etl/draft.py`

- Путь: `v2/backend/apps/recipes/etl/draft.py`
- Классы и функции: DraftError, load_json, validate_draft, parse_draft, known_from_v1_map, load_review, review_allows_import
- Строк: 782

```python
"""Validate and parse V2 recipe draft JSON (overlay / waves). No LLM."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from apps.recipes.constants import (
    ADAPTATION_TYPE,
    ALLERGEN,
    COOK_METHOD,
    CUT,
    DISH_TYPE,
    ENERGY_PROFILE,
    EQUIPMENT,
    HIGH_RISK,
    MAX_VARIANTS,
    PROTEIN_BASE,
    SCALE_MODE,
    UNIT,
    USE_CASE,
    VARIANT_AXIS,
    YIELD_KIND,
)
from apps.recipes.etl.taxonomy import TEMP_REQUIRED_SLUGS

FORBIDDEN_METHOD_ALIASES = frozenset({"duhovka", "skovoroda", "kastryulya", "tushenie"})
FORBIDDEN_URL_NEEDLES = ("sol-chef.ru",)
MANUAL_CANONICALS = frozenset(
    {"baking_soda", "yeast", "dry_yeast", "gelatin", "baking_powder"}
)
WEIGHT_VOLUME = frozenset({"g", "kg", "ml", "l"})
ALLERGEN_DELTA_KEYS = (
    "contains_add",
    "contains_remove",
    "may_contain_add",
    "may_contain_remove",
    "unknown_add",
    "unknown_remove",
)
EMPTY_ALLERGEN_DELTA = {key: [] for key in ALLERGEN_DELTA_KEYS}
FORBIDDEN_RECIPE_NUTRITION_KEYS = frozenset(
    {
        "kcal",
        "nutrition",
        "protein_g",
        "fat_g",
        "carbs_g",
        "per_serving",
        "per_100g_cooked",
        "per_100g_input",
    }
)

MIN_NOTES_OVERLAY = 3
MAX_NOTES = 10
LINE_ALLERGEN_KEYS = (
    "allergens_contains",
    "allergens_may_contain",
    "allergens_unknown",
)


class DraftError(Exception):
    pass


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise DraftError(f"Нет файла {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DraftError(f"{path.name}: не JSON ({exc})") from exc
    if not isinstance(payload, dict):
        raise DraftError(f"{path.name}: нужен объект рецепта, не массив")
    return payload


def validate_draft(
    raw: dict,
    *,
    overlay: bool = True,
    known_ingredients: dict[str, dict] | None = None,
) -> list[str]:
    errors: list[str] = []
    slug = (raw.get("id") or raw.get("slug") or "").strip()
    if not slug:
        errors.append("Нет id/slug")
        slug = "?"

    def err(msg: str) -> None:
        errors.append(f"{slug}: {msg}")

    title = (raw.get("title") or "").strip()
    if not title:
        err("нет title")
    if raw.get("editorial_tested") is True:
        err("агент не ставит editorial_tested")
    if raw.get("tags") or raw.get("category"):
        err("tags/category — поля V1, не писать")
    for key in FORBIDDEN_RECIPE_NUTRITION_KEYS:
        if key in raw:
            err(f"ключ {key} на рецепте запрещён")

    _enum("protein_base", raw.get("protein_base"), PROTEIN_BASE, err)
    extra_bases = raw.get("protein_bases_extra") or []
    if extra_bases:
        if not isinstance(extra_bases, list):
            err("protein_bases_extra не список")
        else:
            seen_extra: set[str] = set()
            for code in extra_bases:
                _enum("protein_bases_extra", code, PROTEIN_BASE, err)
                if code == raw.get("protein_base"):
                    err("protein_bases_extra дублирует protein_base")
                if code in seen_extra:
                    err(f"дубль protein_bases_extra {code}")
                seen_extra.add(code)
    _enum("cook_method", raw.get("cook_method"), COOK_METHOD, err)
    if raw.get("cook_method") in FORBIDDEN_METHOD_ALIASES:
        err("cook_method V1-алиас запрещён")
    _enum("dish_type", raw.get("dish_type"), DISH_TYPE, err)
    if raw.get("dish_type") in {"pan_fry", "stew", "oven", "grill"}:
        err("dish_type не кодирует способ готовки")
    equipment = raw.get("equipment")
    if equipment is not None and equipment != "":
        _enum("equipment", equipment, EQUIPMENT, err)
    energy = raw.get("energy_profile") or "standard"
    _enum("energy_profile", energy, ENERGY_PROFILE, err)
    if raw.get("scale_mode"):
        _enum("scale_mode", raw.get("scale_mode"), SCALE_MODE, err)
    if raw.get("scale_mode") == "fixed":
        err("scale_mode=fixed нет; это scalable=false")
    _check_yield(raw, err)

    if overlay:
        _check_overlay_profile(raw, err)
        _check_adaptations(raw.get("adaptations"), err)

    if "prep" in raw:
        prep = raw.get("prep")
        if not isinstance(prep, list):
            err("prep должен быть списком {text}")
        elif not prep:
            err("пустой prep — уберите ключ")
        else:
            for index, item in enumerate(prep):
                if not isinstance(item, dict) or not str(item.get("text") or "").strip():
                    err(f"prep[{index}]: нужен text")

    for cut in raw.get("allowed_cuts") or []:
        if cut not in CUT:
            err(f"неизвестный cut {cut!r}")

    url = (raw.get("source_url") or "").strip()
    for needle in FORBIDDEN_URL_NEEDLES:
        if needle in url.lower():
            err("циклический source_url (sol-chef.ru) — Critical")

    flags = raw.get("high_risk_flags") or []
    for flag in flags:
        if flag not in HIGH_RISK:
            err(f"неизвестный high-risk {flag!r}")
    if flags and not (raw.get("caution_text") or "").strip():
        err("high-risk без caution_text")

    notes = raw.get("notes")
    if not isinstance(notes, list):
        err("notes должен быть списком {title,text}")
        notes = []
    titled = 0
    for item in notes:
        if not isinstance(item, dict) or not str(item.get("text") or "").strip():
            err("пустой пункт notes")
            continue
        if item.get("title"):
            titled += 1
    if overlay:
        if len(notes) < MIN_NOTES_OVERLAY:
            err(f"оверлей: notes меньше {MIN_NOTES_OVERLAY}")
        if len(notes) > MAX_NOTES:
            err(f"notes больше {MAX_NOTES}")

    lines = raw.get("ingredients")
    if not isinstance(lines, list) or not lines:
        err("нет ingredients")
        lines = []
    positions: set[int] = set()
    anchors = 0
    weight_lines = 0
    canons: dict[str, dict] = {}
    known = dict(known_ingredients or {})
    for extra in raw.get("new_ingredients") or []:
        if not isinstance(extra, dict) or not extra.get("canonical_id"):
            err("new_ingredients: нужен canonical_id")
            continue
        cid = extra["canonical_id"]
        if cid in known:
            err(f"new_ingredients {cid}: канон уже в реестре — уберите заявку")
        canons[cid] = extra
        for key in ("allergens_contains", "allergens_may_contain", "allergens_unknown"):
            for code in extra.get(key) or extra.get(key.replace("allergens_", "")) or []:
                if code not in ALLERGEN:
                    err(f"new_ingredients {cid}: аллерген {code!r}")

    for index, line in enumerate(lines):
        if not isinstance(line, dict):
            err(f"ингредиент {index} не объект")
            continue
        cid = (line.get("canonical_id") or "").strip()
        if not cid:
            err(f"ингредиент {index}: нет canonical_id")
        unit = line.get("unit")
        if unit not in UNIT:
            err(f"{cid or index}: unit {unit!r} не из VOCAB")
        if unit in {"cup", "стакан", "стакана"}:
            err(f"{cid}: стакан/cup запрещён")
        pos = line.get("position", index)
        try:
            pos = int(pos)
        except (TypeError, ValueError):
            err(f"{cid}: position не число")
            pos = index
        if pos in positions:
            err(f"дубль position ингредиента {pos}")
        positions.add(pos)
        mode = line.get("scale_mode") or "linear"
        if mode not in SCALE_MODE:
            err(f"{cid}: scale_mode {mode!r}")
        if cid in MANUAL_CANONICALS and mode == "gentle":
            err(f"{cid}: сода/дрожжи/желатин — не gentle; linear или manual")
        scalable = bool(line.get("scalable", True))
        amount = line.get("amount")
        if unit in {"to_taste", "pinch"}:
            if amount is not None:
                err(f"{cid}: to_taste/pinch — amount null")
            if scalable:
                err(f"{cid}: to_taste/pinch — scalable=false")
        if line.get("is_anchor"):
            anchors += 1
            if unit not in WEIGHT_VOLUME or amount is None:
                err(f"{cid}: якорь только с количеством г/мл/кг/л")
        if scalable and unit in WEIGHT_VOLUME and amount is not None:
            weight_lines += 1
        if "timer_min" in line:
            err("timer_min у ингредиента")
        for key in LINE_ALLERGEN_KEYS:
            if key in line:
                err(f"{cid}: аллергены только в реестре Ingredient, не в строке рецепта")
        _check_line_nutrition(line, cid, err)

    if anchors > 1:
        err("больше одного is_anchor")
    if overlay and anchors == 0 and raw.get("servings") is None and weight_lines:
        err("нет якоря и нет servings — граммовка на сайте выключена")

    steps = raw.get("steps")
    if not isinstance(steps, list) or not steps:
        err("нет steps")
        steps = []
    step_pos: set[int] = set()
    targets: set[int] = set()
    pan_note = False
    for index, step in enumerate(steps):
        if isinstance(step, str):
            err(f"шаг {index}: строка запрещена, нужен объект")
            continue
        if not isinstance(step, dict):
            err(f"шаг {index}: не объект")
            continue
        if not str(step.get("text") or "").strip():
            err(f"шаг {index}: пустой text")
        if step.get("timer_min") is not None:
            err(f"шаг {index}: timer_min — пишите timer_seconds")
        pos = step.get("position", index)
        try:
            pos = int(pos)
        except (TypeError, ValueError):
            err(f"шаг {index}: position не число")
            pos = index
        if pos in step_pos:
            err(f"дубль position шага {pos}")
        step_pos.add(pos)
        pull = step.get("pull_internal_temperature_c")
        target = step.get("target_internal_temperature_c")
        hold = step.get("hold_seconds")
        if pull is not None and target is None:
            err(f"шаг {pos}: pull без target")
        if target is not None:
            try:
                targets.add(int(target))
            except (TypeError, ValueError):
                err(f"шаг {pos}: target не число")
        text = (step.get("text") or "").lower()
        note = (step.get("equipment_note") or "").lower()
        if "порци" in text or "не перегруз" in text or "не перегруз" in note or "порци" in note:
            pan_note = True
        if step.get("equipment_note"):
            pan_note = True
        if hold is not None and int(hold) < 0:
            err(f"шаг {pos}: hold отрицательный")

    cook = raw.get("cook_method")
    protein = raw.get("protein_base")
    cuts = set(raw.get("allowed_cuts") or [])
    if cook == "pan_fry" and protein in {"beef", "pork", "poultry", "lamb"} and not pan_note:
        err("pan_fry мяса: в шаге жарки нужна оговорка не перегружать сковороду")
    ready_meat_no_cook = cook == "no_cook" and protein in {
        "poultry",
        "beef",
        "pork",
        "lamb",
        "offal",
    }
    if ready_meat_no_cook:
        # Копчёности, тушёнка, ветчина: не требовать target сырого куска.
        pass
    elif protein == "poultry":
        if "whole_bird" in cuts:
            if not ({72, 82} <= targets):
                err("целая птица: нужны target 72 и 82")
        elif "drumstick" in cuts:
            if not targets or max(targets) < 82:
                err("голень птицы на кости: target не ниже 82")
        elif "thigh" in cuts:
            if not targets or max(targets) < 74:
                err("бедро птицы: target не ниже 74 (без кости); на кости — 82")
        elif "breast" in cuts:
            if not targets or max(targets) < 72:
                err("грудка птицы: target не ниже 72")
        elif not targets:
            err("птица: нет target_internal_temperature_c")
    elif protein == "fish_canned":
        # Промышленные консервы: не требовать target 63.
        pass
    elif protein in {"fish_white_sea", "fish_red_sea", "fish_river"}:
        if "raw_fish" in flags:
            pass
        elif cook == "no_cook":
            # Сборка готовых консервов / холодный боул: не требовать повторный target 63.
            pass
        elif not targets or min(targets) < 63:
            err("готовая рыба: target не ниже 63")
    elif protein == "pork" and "mince" not in cuts:
        if not targets:
            err("свинина: нет target")
        else:
            t = min(targets)
            holds = [
                int(s.get("hold_seconds") or 0)
                for s in steps
                if isinstance(s, dict) and s.get("hold_seconds") is not None
            ]
            ok = t >= 71 or (t >= 63 and (max(holds) if holds else 0) >= 180)
            if not ok:
                err("свинина: 63 °C + hold ≥ 180 с или 71 °C")
    elif slug in TEMP_REQUIRED_SLUGS and not targets:
        err("нет target_internal_temperature_c (SAFETY)")

    variants = raw.get("variants") or raw.get("variations") or []
    if raw.get("variations") and not raw.get("variants"):
        for item in raw.get("variations") or []:
            if isinstance(item, dict) and item.get("text") and not item.get("has_delta"):
                err("variations[].text без дельты — для оверлея запрещено")
    codes: set[str] = set()
    for item in variants:
        if not isinstance(item, dict):
            err("вариант не объект")
            continue
        axis = item.get("axis") or "addon"
        if axis not in VARIANT_AXIS:
            err(f"axis {axis!r} не addon/equipment/energy")
        code = (item.get("code") or "").strip()
        if not code:
            err("вариант без code")
        if code in codes:
            err(f"дубль variant code {code}")
        codes.add(code)
        if axis == "energy" and code not in {"light", "rich"}:
            err(f"energy code {code!r} — только light/rich")
        has_delta = bool(item.get("has_delta"))
        ing = item.get("ingredient_delta")
        step_delta = item.get("step_delta")
        if item.get("text") and not has_delta:
            err(f"{code}: текстовая вариация без has_delta")
        if has_delta:
            if not ing and not step_delta:
                err(f"{code}: has_delta без ingredient_delta/step_delta")
            if ing is not None:
                _check_allergen_delta(item.get("allergen_delta"), err, code)
                _check_delta_nutrition(ing, err, code)
        if item.get("cook_method_override"):
            _enum("cook_method_override", item.get("cook_method_override"), COOK_METHOD, err)
        if item.get("protein_base_override"):
            _enum("protein_base_override", item.get("protein_base_override"), PROTEIN_BASE, err)
            if item.get("protein_base_override") == raw.get("protein_base"):
                err(f"{code}: protein_base_override совпадает с базой")
            if axis != "addon":
                err(f"{code}: protein_base_override только у addon")
            if not has_delta:
                err(f"{code}: protein_base_override без has_delta")
        if item.get("equipment"):
            _enum("variant.equipment", item.get("equipment"), EQUIPMENT, err)

    if overlay and len(variants) > MAX_VARIANTS:
        err(f"вариантов больше {MAX_VARIANTS}")

    if overlay and known_ingredients is not None:
        registry = set(known_ingredients) | set(canons)
        for cid in _draft_canonicals(raw):
            if cid and cid not in registry:
                err(f"нет канона {cid} (реестр или new_ingredients)")

    return errors


def _enum(name: str, value, allowed: frozenset[str], err) -> None:
    if value not in allowed:
        err(f"{name}={value!r} не из VOCAB")


def _check_overlay_profile(raw: dict, err) -> None:
    profile = raw.get("time_profile")
    total = None
    active = None
    if isinstance(profile, dict):
        total = profile.get("total_minutes")
        active = profile.get("active_minutes")
    else:
        total = raw.get("time_minutes")
        active = raw.get("active_minutes")
    if total is None or active is None:
        err("оверлей: нужен time_profile {total_minutes, active_minutes}")
    else:
        try:
            total_i = int(total)
            active_i = int(active)
        except (TypeError, ValueError):
            err("time_profile: минуты — целые")
        else:
            if total_i < 1 or active_i < 0:
                err("time_profile: total ≥ 1, active ≥ 0")
            elif active_i > total_i:
                err("active_minutes больше total_minutes")
    effort = raw.get("effort_level", raw.get("effort"))
    washing = raw.get("washing_level", raw.get("washing"))
    for name, value in (("effort_level", effort), ("washing_level", washing)):
        if value is None:
            err(f"оверлей: нужен {name} 1–5")
            continue
        try:
            level = int(value)
        except (TypeError, ValueError):
            err(f"{name} должен быть 1–5")
            continue
        if not 1 <= level <= 5:
            err(f"{name} должен быть 1–5")
    cases = raw.get("use_cases")
    if not isinstance(cases, list):
        err("use_cases должен быть списком (можно [])")
        return
    seen: set[str] = set()
    for code in cases:
        if code not in USE_CASE:
            err(f"use_case {code!r} не из VOCAB")
        elif code in seen:
            err(f"дубль use_case {code}")
        seen.add(code)


def _check_adaptations(adaptations, err) -> None:
    if adaptations is None:
        err("оверлей: нужен adaptations (можно [])")
        return
    if not isinstance(adaptations, list):
        err("adaptations должен быть списком")
        return
    for index, item in enumerate(adaptations):
        if not isinstance(item, dict):
            err(f"adaptation[{index}] не объект")
            continue
        kind = item.get("type")
        if kind not in ADAPTATION_TYPE:
            err(f"adaptation[{index}]: type {kind!r}")
            continue
        quality = item.get("quality")
        if quality is not None:
            try:
                q = float(quality)
            except (TypeError, ValueError):
                err(f"adaptation[{index}]: quality не число")
            else:
                if not 0 <= q <= 1:
                    err(f"adaptation[{index}]: quality 0–1")
        if kind == "substitution":
            if not item.get("from") or not item.get("to"):
                err(f"adaptation[{index}]: substitution нужен from и to")
        elif kind == "omission":
            if not item.get("ingredient"):
                err(f"adaptation[{index}]: omission нужен ingredient")
        else:
            src = item.get("from")
            dest = item.get("to")
            if not src or not dest:
                err(f"adaptation[{index}]: {kind} нужен from и to")
            elif kind == "equipment":
                if src not in EQUIPMENT:
                    err(f"adaptation[{index}]: from {src!r} не equipment")
                if dest not in EQUIPMENT:
                    err(f"adaptation[{index}]: to {dest!r} не equipment")
            elif kind == "method":
                if src not in COOK_METHOD:
                    err(f"adaptation[{index}]: from {src!r} не cook_method")
                if dest not in COOK_METHOD:
                    err(f"adaptation[{index}]: to {dest!r} не cook_method")


def _draft_canonicals(raw: dict) -> set[str]:
    found: set[str] = set()
    for line in raw.get("ingredients") or []:
        if isinstance(line, dict) and line.get("canonical_id"):
            found.add(line["canonical_id"])
    for item in raw.get("variants") or raw.get("variations") or []:
        if not isinstance(item, dict):
            continue
        delta = item.get("ingredient_delta") or {}
        if not isinstance(delta, dict):
            continue
        for spec in [*(delta.get("add") or []), *(delta.get("replace") or [])]:
            if isinstance(spec, dict) and spec.get("canonical_id"):
                found.add(spec["canonical_id"])
    return found


def _check_yield(raw: dict, err) -> None:
    kind = raw.get("yield_kind")
    if kind is not None and kind != "":
        _enum("yield_kind", kind, YIELD_KIND, err)
    weight = raw.get("yield_weight_g")
    if weight is None or weight == "":
        if kind:
            err("yield_kind без yield_weight_g")
        return
    try:
        value = Decimal(str(weight))
    except (InvalidOperation, TypeError, ValueError):
        err("yield_weight_g не число")
        return
    if value <= 0:
        err("yield_weight_g должен быть > 0")


def _check_line_nutrition(line: dict, cid: str, err) -> None:
    if "nutrition_exclude" in line and not isinstance(line.get("nutrition_exclude"), bool):
        err(f"{cid}: nutrition_exclude должен быть bool")
    if line.get("nutrition_exclude") and line.get("nutrition_factor") is not None:
        err(f"{cid}: nutrition_factor не вместе с nutrition_exclude")
    if "nutrition_factor" in line and line.get("nutrition_factor") is not None:
        try:
            factor = Decimal(str(line.get("nutrition_factor")))
        except (InvalidOperation, TypeError, ValueError):
            err(f"{cid}: nutrition_factor не число")
            return
        if not (Decimal("0.01") <= factor <= Decimal("1")):
            err(f"{cid}: nutrition_factor должен быть 0.01–1")


def _check_delta_nutrition(delta, err, code: str) -> None:
    if not isinstance(delta, dict):
        return
    for spec in [*(delta.get("add") or []), *(delta.get("replace") or [])]:
        if not isinstance(spec, dict):
            continue
        cid = (spec.get("canonical_id") or "").strip() or f"{code}:delta"
        _check_line_nutrition(spec, cid, err)


def _check_allergen_delta(delta, err, code: str) -> None:
    if not isinstance(delta, dict):
        err(f"{code}: ingredient_delta требует allergen_delta")
        return
    for key in ALLERGEN_DELTA_KEYS:
        for item in delta.get(key) or []:
            if item not in ALLERGEN:
                err(f"{code}: allergen_delta {key} код {item!r}")


def _dec(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DraftError(f"Некорректное число {value!r}") from exc


def parse_draft(raw: dict, *, known_ingredients: dict[str, dict] | None) -> dict:
    errors = validate_draft(raw, overlay=True, known_ingredients=known_ingredients)
    if errors:
        extra = f" (+{len(errors) - 12})" if len(errors) > 12 else ""
        raise DraftError("; ".join(errors[:12]) + extra)
    slug = (raw.get("id") or raw.get("slug") or "").strip()
    known = dict(known_ingredients or {})
    new_canons: list[dict] = []
    for extra in raw.get("new_ingredients") or []:
        cid = extra["canonical_id"]
        row = {
            "canonical_id": cid,
            "title": extra.get("title") or extra.get("display_name") or cid,
            "aliases": extra.get("aliases") or [],
            "contains": extra.get("allergens_contains") or extra.get("contains") or [],
            "may_contain": extra.get("allergens_may_contain") or extra.get("may_contain") or [],
            "unknown": extra.get("allergens_unknown") or extra.get("unknown") or [],
        }
        known[cid] = row
        new_canons.append(row)

    lines = []
    titles = []
    for index, line in enumerate(raw["ingredients"]):
        cid = line["canonical_id"]
        meta = known.get(cid)
        if meta is None:
            raise DraftError(f"{slug}: нет канона {cid} (сид или new_ingredients)")
        unit = line["unit"]
        amount = _dec(line.get("amount"))
        amount_max = _dec(line.get("amount_max"))
        scalable = bool(line.get("scalable", True))
        if unit in {"to_taste", "pinch"}:
            amount = None
            amount_max = None
            scalable = False
        display = line.get("display_name") or meta.get("title") or cid
        titles.append(display)
        lines.append(
            {
                "canonical_id": cid,
                "ingredient_title": meta.get("title") or display,
                "aliases": meta.get("aliases") or [],
                "contains": meta.get("contains") or [],
                "may_contain": meta.get("may_contain") or [],
                "unknown": meta.get("unknown") or [],
                "position": int(line.get("position", index)),
                "amount": amount,
                "amount_max": amount_max,
                "unit": unit,
                "detail": line.get("detail"),
                "scale_mode": line.get("scale_mode") or "linear",
                "scalable": scalable,
                "is_anchor": bool(line.get("is_anchor")),
                "optional": bool(line.get("optional", False)),
                "nutrition_exclude": bool(line.get("nutrition_exclude", False)),
                "nutrition_factor": _dec(line.get("nutrition_factor")),
                "choice_group": line.get("choice_group"),
                "display_name": display,
            }
        )

    steps = []
    for index, step in enumerate(raw["steps"]):
        pull = step.get("pull_internal_temperature_c")
        target = step.get("target_internal_temperature_c")
        hold = step.get("hold_seconds")
        steps.append(
            {
                "position": int(step.get("position", index)),
                "text": step["text"],
                "timer_seconds": step.get("timer_seconds"),
                "timer_label": step.get("timer_label"),
                "timer_note": step.get("timer_note"),
                "pull_internal_temperature_c": int(pull) if pull is not None else None,
                "target_internal_temperature_c": int(target) if target is not None else None,
                "hold_seconds": int(hold) if hold is not None else None,
                "equipment_note": step.get("equipment_note"),
            }
        )

    variants = []
    for item in raw.get("variants") or []:
        allergen = item.get("allergen_delta")
        if item.get("has_delta") and item.get("ingredient_delta") is not None and allergen is None:
            allergen = dict(EMPTY_ALLERGEN_DELTA)
        variants.append(
            {
                "axis": item.get("axis") or "addon",
                "code": item["code"],
                "title": item["title"],
                "has_delta": bool(item.get("has_delta")),
                "legacy_text": item.get("legacy_text"),
                "ingredient_delta": item.get("ingredient_delta"),
                "step_delta": item.get("step_delta"),
                "allergen_delta": allergen,
                "high_risk_delta": item.get("high_risk_delta") or {"add": [], "remove": []},
                "cook_method_override": item.get("cook_method_override"),
                "protein_base_override": item.get("protein_base_override"),
                "equipment": item.get("equipment"),
                "caution_text_override": item.get("caution_text_override"),
            }
        )

    url = (raw.get("source_url") or "").strip() or None
    profile = raw.get("time_profile") if isinstance(raw.get("time_profile"), dict) else {}
    extra_bases = raw.get("protein_bases_extra") or []
    if not isinstance(extra_bases, list):
        extra_bases = []
    return {
        "slug": slug,
        "title": raw["title"],
        "protein_base": raw["protein_base"],
        "protein_bases_extra": extra_bases if isinstance(extra_bases, list) else [],
        "cook_method": raw["cook_method"],
        "dish_type": raw["dish_type"],
        "scale_mode": raw.get("scale_mode") or "linear",
        "scalable": raw.get("scalable", True),
        "servings": raw.get("servings"),
        "yield_weight_g": _dec(raw.get("yield_weight_g")),
        "yield_kind": (raw.get("yield_kind") or None)
        or ("estimated" if raw.get("yield_weight_g") not in (None, "") else None),
        "summary": raw.get("summary"),
        "source_name": raw.get("source_name"),
        "source_url": url,
        "source_type": raw.get("source_type"),
        "high_risk_flags": raw.get("high_risk_flags") or [],
        "caution_text": raw.get("caution_text"),
        "energy_profile": raw.get("energy_profile") or "standard",
        "equipment": raw.get("equipment") or None,
        "allowed_cuts": raw.get("allowed_cuts") or [],
        "notes": raw.get("notes") or [],
        "prep": raw.get("prep") or [],
        "time_total_minutes": profile.get("total_minutes", raw.get("time_minutes")),
        "time_active_minutes": profile.get("active_minutes", raw.get("active_minutes")),
        "effort_level": raw.get("effort_level", raw.get("effort")),
        "washing_level": raw.get("washing_level", raw.get("washing")),
        "use_cases": raw.get("use_cases") or [],
        "adaptations": raw.get("adaptations") or [],
        "new_canons": new_canons,
        "ingredient_titles": " ".join(titles),
        "lines": lines,
        "steps": steps,
        "variants": variants,
        "origin": "draft",
        "status": "published",
        "raw": raw,
    }


def known_from_v1_map(ingredient_map: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in ingredient_map.values():
        cid = row["canonical_id"]
        current = out.get(cid)
        aliases = list(row.get("aliases") or [])
        if current:
            aliases = list(dict.fromkeys([*(current.get("aliases") or []), *aliases]))
        out[cid] = {
            "canonical_id": cid,
            "title": row.get("title") or cid,
            "aliases": aliases,
            "contains": row.get("contains") or [],
            "may_contain": row.get("may_contain") or [],
            "unknown": row.get("unknown") or [],
        }
    return out


def load_review(path: Path) -> dict:
    if not path.is_file():
        raise DraftError(f"Нет вердикта {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DraftError(f"{path.name}: вердикт не объект")
    return payload


def review_allows_import(review: dict) -> bool:
    return (
        review.get("verdict") == "accept"
        and review.get("cookable") is True
        and review.get("real") is not False
    )
```

---

## 7. `backend/apps/recipes/etl/ingredients.py`

- Путь: `v2/backend/apps/recipes/etl/ingredients.py`
- Классы и функции: parse_amount, map_unit_and_amount, infer_scale_mode, is_anchor_candidate, is_optional_line
- Строк: 95

```python
"""Map V1 ingredient rows to VOCAB units and scale_mode."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from apps.recipes.constants import V1_UNIT_TO_VOCAB
from apps.recipes.etl.load import V1ImportError

# 1 Russian cup = 250 ml. VOCAB forbids storing cup; convert amount.
CUP_TO_ML = Decimal("250")

GENTLE_NAME_MARKERS = (
    "соль",
    "перец",
    "паприка",
    "зира",
    "кумин",
    "куркума",
    "кориандр",
    "корица",
    "гвоздика",
    "чили",
    "гарам",
    "шафран",
    "тимьян",
    "розмарин",
    "хлопья перца",
    "хлопья чили",
)

MANUAL_NAME_MARKERS = (
    "сода",
    "разрыхлител",
    "дрожж",
    "желатин",
)

EGG_NAME_MARKERS = ("яйц", "белок")

OIL_NAMES = (
    "растительное масло",
    "оливковое масло",
)

SPICE_OIL_UNITS = {"tsp", "tbsp"}


def parse_amount(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise V1ImportError(f"Некорректное количество {value!r}") from exc


def map_unit_and_amount(v1_unit: str | None, amount: Decimal | None) -> tuple[str, Decimal | None]:
    if not v1_unit:
        return "to_taste", None
    unit = v1_unit.strip()
    if unit == "стакана":
        if amount is None:
            raise V1ImportError("Единица «стакана» без количества")
        return "ml", amount * CUP_TO_ML
    mapped = V1_UNIT_TO_VOCAB.get(unit)
    if mapped is None:
        raise V1ImportError(f"Неизвестная единица V1: {unit!r}")
    return mapped, amount


def infer_scale_mode(name: str, unit: str, explicit: str | None) -> str:
    if explicit in {"linear", "gentle", "whole", "manual"}:
        return explicit
    lower = name.lower()
    # Do NOT use V1 autodetet «soda → gentle».
    if any(marker in lower for marker in MANUAL_NAME_MARKERS):
        return "manual"
    if unit == "pcs" and any(marker in lower for marker in EGG_NAME_MARKERS):
        return "whole"
    if any(marker in lower for marker in GENTLE_NAME_MARKERS):
        return "gentle"
    if lower in OIL_NAMES and unit in SPICE_OIL_UNITS:
        return "gentle"
    return "linear"


def is_anchor_candidate(scalable: bool, amount: Decimal | None, unit: str) -> bool:
    return scalable and amount is not None and unit in {"g", "ml", "kg", "l"}


def is_optional_line(detail: str | None) -> bool:
    """Garnish / serving / «по желанию» — not required for the dish."""
    text = (detail or "").lower()
    return "для подачи" in text or "по желанию" in text
```

---

## 8. `backend/apps/recipes/etl/load.py`

- Путь: `v2/backend/apps/recipes/etl/load.py`
- Классы и функции: V1ImportError, resolve_v1_root, read_index, load_recipe_objects, folder_from_rel
- Строк: 62

```python
"""Load V1 recipe JSON (no DB). Used by import_v1 and tests."""

from __future__ import annotations

import json
from pathlib import Path

from apps.recipes.constants import EXPECTED_RECIPE_COUNT, EXPECTED_RECIPE_FILES


class V1ImportError(Exception):
    pass


def resolve_v1_root(root: Path) -> Path:
    """Accept the repo root or `archive/v1`. Prefer a tree that still has the catalog JSON."""
    for candidate in (root, root / "archive" / "v1"):
        if (candidate / "data" / "recipes" / "index.json").is_file():
            return candidate
    archived = root / "archive" / "v1"
    raise V1ImportError(
        f"Нет каталога V1 (data/recipes/index.json) в {root} или {archived}"
    )


def read_index(data_root: Path) -> list[str]:
    index_path = data_root / "data" / "recipes" / "index.json"
    if not index_path.is_file():
        raise V1ImportError(f"Нет файла {index_path}")
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    files = payload.get("files") or []
    if len(files) != EXPECTED_RECIPE_FILES:
        raise V1ImportError(
            f"Ожидалось {EXPECTED_RECIPE_FILES} файлов в index.json, получено {len(files)}"
        )
    return files


def load_recipe_objects(data_root: Path) -> list[tuple[str, dict]]:
    """Return list of (relative_file, recipe_dict). Fails if count ≠ 43."""
    files = read_index(data_root)
    found: list[tuple[str, dict]] = []
    for rel in files:
        path = data_root / rel
        if not path.is_file():
            raise V1ImportError(f"Нет файла рецептов {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise V1ImportError(f"{rel} должен быть массивом рецептов")
        for recipe in data:
            found.append((rel, recipe))
    if len(found) != EXPECTED_RECIPE_COUNT:
        raise V1ImportError(
            f"Ожидалось {EXPECTED_RECIPE_COUNT} рецептов, получено {len(found)}"
        )
    return found


def folder_from_rel(rel: str) -> str:
    # data/recipes/duhovka/ptitsa.json → duhovka
    parts = Path(rel).parts
    return parts[2]
```

---

## 9. `backend/apps/recipes/etl/nutrition.py`

- Путь: `v2/backend/apps/recipes/etl/nutrition.py`
- Классы и функции: seed_path, load_seed, load_ingredient_nutrition
- Строк: 82

```python
"""Load Ingredient nutrition from the git seed. No HTTP, no FDC at runtime."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from apps.recipes.constants import NUTRITION_BASIS, NUTRITION_SOURCE
from apps.recipes.models import Ingredient

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "ingredient_nutrition.json"
MACRO_KEYS = ("kcal", "protein_g", "fat_g", "carbs_g")
G_PER_FIELDS = (
    "g_per_tsp",
    "g_per_tbsp",
    "g_per_pcs",
    "g_per_clove",
    "g_per_bunch",
    "g_per_slice",
)


def seed_path() -> Path:
    return FIXTURE


def load_seed(path: Path | None = None) -> dict:
    target = path or FIXTURE
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{target.name}: нужен объект canonical_id → нутриенты")
    return payload


def _dec(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Некорректное число {value!r}") from exc


def _row_defaults(cid: str, row: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError(f"{cid}: значение сида не объект")
    missing = [key for key in MACRO_KEYS if row.get(key) is None]
    if missing:
        raise ValueError(f"{cid}: в сиде нет {', '.join(missing)}")
    source = row.get("source")
    if source not in NUTRITION_SOURCE:
        raise ValueError(f"{cid}: nutrition_source {source!r}")
    defaults = {
        "kcal_per_100g": _dec(row["kcal"]),
        "protein_g_per_100g": _dec(row["protein_g"]),
        "fat_g_per_100g": _dec(row["fat_g"]),
        "carbs_g_per_100g": _dec(row["carbs_g"]),
        "nutrition_basis": "raw_100g",
        "nutrition_source": source,
        "nutrition_source_id": row.get("source_id") or None,
    }
    if defaults["nutrition_basis"] not in NUTRITION_BASIS:
        raise ValueError(f"{cid}: nutrition_basis")
    if row.get("density_g_per_ml") is not None:
        defaults["density_g_per_ml"] = _dec(row["density_g_per_ml"])
    for field in G_PER_FIELDS:
        if row.get(field) is not None:
            defaults[field] = _dec(row[field])
    return defaults


def load_ingredient_nutrition(path: Path | None = None) -> int:
    """Update existing Ingredient rows. Does not touch title/allergens."""
    payload = load_seed(path)
    updated = 0
    for cid, row in payload.items():
        if not cid or cid.startswith("_"):
            continue
        fields = _row_defaults(cid, row)
        count = Ingredient.objects.filter(canonical_id=cid).update(**fields)
        if count:
            updated += count
    return updated
```

---

## 10. `backend/apps/recipes/etl/serialize.py`

- Путь: `v2/backend/apps/recipes/etl/serialize.py`
- Классы и функции: recipe_to_draft
- Строк: 129

```python
"""Serialize a live Recipe row back to author draft JSON."""

from __future__ import annotations

from decimal import Decimal

from apps.recipes.models import Recipe


def _num(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    return value


def recipe_to_draft(recipe: Recipe) -> dict:
    payload: dict = {
        "id": recipe.slug,
        "title": recipe.title,
        "summary": recipe.summary,
        "protein_base": recipe.protein_base,
        "cook_method": recipe.cook_method,
        "dish_type": recipe.dish_type,
        "equipment": recipe.equipment,
        "energy_profile": recipe.energy_profile or "standard",
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "protein_bases_extra": list(recipe.protein_bases_extra or []),
        "scale_mode": recipe.scale_mode or "linear",
        "scalable": recipe.scalable,
        "source_type": recipe.source_type,
        "source_name": recipe.source_name,
        "source_url": recipe.source_url,
        "high_risk_flags": list(recipe.high_risk_flags or []),
        "caution_text": recipe.caution_text,
        "time_profile": {
            "total_minutes": recipe.time_total_minutes,
            "active_minutes": recipe.time_active_minutes,
        },
        "effort_level": recipe.effort_level,
        "washing_level": recipe.washing_level,
        "use_cases": list(recipe.use_cases or []),
        "adaptations": recipe.adaptations or [],
        "prep": recipe.prep or [],
        "notes": recipe.notes or [],
        "ingredients": [],
        "steps": [],
        "variants": [],
    }
    if recipe.servings is not None:
        payload["servings"] = recipe.servings
    if recipe.yield_weight_g is not None:
        payload["yield_weight_g"] = _num(recipe.yield_weight_g)
        if recipe.yield_kind:
            payload["yield_kind"] = recipe.yield_kind

    for line in recipe.ingredients.select_related("ingredient").all():
        row = {
            "position": line.position,
            "canonical_id": line.ingredient.canonical_id,
            "display_name": line.display_name or line.ingredient.title,
            "amount": _num(line.amount),
            "unit": line.unit,
            "scale_mode": line.scale_mode,
            "scalable": line.scalable,
            "is_anchor": line.is_anchor,
            "optional": line.optional,
        }
        if line.amount_max is not None:
            row["amount_max"] = _num(line.amount_max)
        if line.detail:
            row["detail"] = line.detail
        if line.choice_group:
            row["choice_group"] = line.choice_group
        if line.nutrition_exclude:
            row["nutrition_exclude"] = True
        if line.nutrition_factor is not None:
            row["nutrition_factor"] = _num(line.nutrition_factor)
        payload["ingredients"].append(row)

    for step in recipe.steps.all():
        row = {"position": step.position, "text": step.text}
        if step.timer_seconds is not None:
            row["timer_seconds"] = step.timer_seconds
        if step.timer_label:
            row["timer_label"] = step.timer_label
        if step.timer_note:
            row["timer_note"] = step.timer_note
        if step.pull_internal_temperature_c is not None:
            row["pull_internal_temperature_c"] = step.pull_internal_temperature_c
        if step.target_internal_temperature_c is not None:
            row["target_internal_temperature_c"] = step.target_internal_temperature_c
        if step.hold_seconds is not None:
            row["hold_seconds"] = step.hold_seconds
        if step.equipment_note:
            row["equipment_note"] = step.equipment_note
        payload["steps"].append(row)

    for variant in recipe.variants.all():
        row = {
            "axis": variant.axis,
            "code": variant.code,
            "title": variant.title,
            "has_delta": variant.has_delta,
        }
        if variant.legacy_text:
            row["legacy_text"] = variant.legacy_text
        if variant.ingredient_delta is not None:
            row["ingredient_delta"] = variant.ingredient_delta
        if variant.step_delta is not None:
            row["step_delta"] = variant.step_delta
        if variant.allergen_delta is not None:
            row["allergen_delta"] = variant.allergen_delta
        if variant.high_risk_delta:
            row["high_risk_delta"] = variant.high_risk_delta
        if variant.cook_method_override:
            row["cook_method_override"] = variant.cook_method_override
        if variant.protein_base_override:
            row["protein_base_override"] = variant.protein_base_override
        if variant.equipment:
            row["equipment"] = variant.equipment
        if variant.caution_text_override:
            row["caution_text_override"] = variant.caution_text_override
        payload["variants"].append(row)

    return payload
```

---

## 11. `backend/apps/recipes/etl/taxonomy.py`

- Путь: `v2/backend/apps/recipes/etl/taxonomy.py`
- Классы и функции: нет классов/функций верхнего уровня
- Строк: 105

```python
"""protein_base + dish_type per V1 slug — RECIPE-INVENTORY FACT table, not guessed."""

# slug -> (protein_base, dish_type)
RECIPE_TAXONOMY: dict[str, tuple[str, str]] = {
    "shokoladnyy-fondan": ("vegetarian", "dessert"),
    "stejk-reverse-sear": ("beef", "main"),
    "govyazhya-lopatka-zapishennaya-v-rukave": ("beef", "main"),
    "govyazhi-golyashki-tomlenye-v-duhovke": ("beef", "main"),
    "govyazhij-oguzok-rostbif-v-duhovke": ("beef", "main"),
    "classic-roast-chicken": ("poultry", "main"),
    "kuritsa-maslo-limon-zapechennaya": ("poultry", "main"),
    "kuritsa-s-yablokami-zapechennaya": ("poultry", "main"),
    "kuritsa-tselikom-limonnoe-maslo-bazovyy": ("poultry", "main"),
    "losos-v-duhovke-s-limonom-i-ukropom": ("fish_red_sea", "main"),
    "sudak-v-duhovke-s-limonom": ("fish_river", "main"),
    "svinoj-shashlyk-v-duhovke-na-shpazhkah": ("pork", "main"),
    "svinnaya-sheya-zapechennaya-s-paprikoj": ("pork", "main"),
    "stejk-na-grile": ("beef", "main"),
    "govyazhi-rebra-mangal-folga-soja-med": ("beef", "main"),
    "govyazhi-rebra-mangal-bez-folgi-perets": ("beef", "main"),
    "rassypchataya-grechka-suhoj-obzharki-s-lukom-i-gribami": ("vegetarian", "pasta_grains"),
    "rizotto-bazovyy-parmezan": ("vegetarian", "pasta_grains"),
    "grechka-na-garnir-s-lukom": ("vegetarian", "side"),
    "spagetti-aglio-e-olio": ("vegetarian", "pasta_grains"),
    "spagetti-kacho-e-pepe": ("vegetarian", "pasta_grains"),
    "korichnevoe-maslo": ("eggs_dairy", "sauce"),
    "aromatizirovannoe-maslo-chili-myod": ("eggs_dairy", "sauce"),
    "ber-mane": ("eggs_dairy", "sauce"),
    "ovoshchnoy-sup-s-fasolyu": ("vegetarian", "soup"),
    "stejk-na-skovorode-pan-searing": ("beef", "main"),
    "barhatnaya-govyadina-po-kitajski": ("beef", "main"),
    "basting-slivochnym-maslom": ("beef", "sauce"),
    "ribaj-na-skovorode-s-timyanom": ("beef", "main"),
    "zharenyy-ris-po-aziatski-vok": ("vegetarian", "pasta_grains"),
    "kurinaya-grudka-na-skovorode-s-paprikoy": ("poultry", "main"),
    "salat-s-syrom-i-gretskimi-orehami": ("vegetarian", "salad"),
    "luchnyy-sous-s-gorchitsey-na-skovorode": ("vegetarian", "sauce"),
    "shakshuka-s-tomatami-i-bazilikom": ("eggs_dairy", "breakfast"),
    "frittata-s-kabachkami-i-bekonom": ("eggs_dairy", "breakfast"),
    "tost-s-yajtsom-pashot-bekonom-i-salsoj": ("eggs_dairy", "breakfast"),
    "vzbitoe-slivochnoe-maslo": ("eggs_dairy", "sauce"),
    "baranya-lopatka-tushenaya-s-lukom-shalot": ("lamb", "main"),
    "govyadina-tushenaya-na-volokna-zamorozka": ("beef", "main"),
    "kurinoe-birjani-po-hajderabadski": ("poultry", "main"),
    "bystroe-kurinoe-karri": ("poultry", "main"),
    "tushenye-kurinye-bedra-s-tomatom": ("poultry", "main"),
    "tushenaya-kuritsa-s-grechkoj-na-dni": ("poultry", "main"),
}

POULTRY_TEMP_SLUGS = frozenset(
    {
        "classic-roast-chicken",
        "kuritsa-maslo-limon-zapechennaya",
        "kuritsa-s-yablokami-zapechennaya",
        "kuritsa-tselikom-limonnoe-maslo-bazovyy",
        "kurinaya-grudka-na-skovorode-s-paprikoy",
        "kurinoe-birjani-po-hajderabadski",
        "bystroe-kurinoe-karri",
        "tushenye-kurinye-bedra-s-tomatom",
        "tushenaya-kuritsa-s-grechkoj-na-dni",
    }
)

TEMP_REQUIRED_SLUGS = POULTRY_TEMP_SLUGS | {
    "losos-v-duhovke-s-limonom-i-ukropom",
    "sudak-v-duhovke-s-limonom",
    "svinoj-shashlyk-v-duhovke-na-shpazhkah",
    "svinnaya-sheya-zapechennaya-s-paprikoj",
}

CAUTION_TEXT = {
    "classic-roast-chicken": (
        "Целая птица: проверьте термометром грудку (не ниже 72 °C) и бедро "
        "(не ниже 82 °C). Не ориентируйтесь только на цвет сока. "
        "Не для детских подборок без дополнительной проверки."
    ),
    "kuritsa-maslo-limon-zapechennaya": (
        "Целая птица: грудка не ниже 72 °C, бедро не ниже 82 °C. "
        "Проверяйте термометром, не по цвету сока."
    ),
    "kuritsa-s-yablokami-zapechennaya": (
        "Целая птица: грудка не ниже 72 °C, бедро не ниже 82 °C. "
        "Проверяйте термометром, не по цвету сока."
    ),
    "kuritsa-tselikom-limonnoe-maslo-bazovyy": (
        "Целая птица: грудка не ниже 72 °C, бедро не ниже 82 °C. "
        "Проверяйте термометром, не по цвету сока."
    ),
    "kurinaya-grudka-na-skovorode-s-paprikoy": (
        "Куриная грудка: внутренняя температура не ниже 72 °C. "
        "Не определяйте готовность только по цвету сока."
    ),
    "kurinoe-birjani-po-hajderabadski": (
        "Тёмное мясо птицы (бёдра): внутренняя температура не ниже 82 °C."
    ),
    "bystroe-kurinoe-karri": (
        "Куриные куски (бёдра): внутренняя температура не ниже 82 °C."
    ),
    "tushenye-kurinye-bedra-s-tomatom": (
        "Куриные бёдра: внутренняя температура у кости не ниже 82 °C."
    ),
    "tushenaya-kuritsa-s-grechkoj-na-dni": (
        "Куриные бёдра: внутренняя температура не ниже 82 °C."
    ),
}
```

---

## 12. `backend/apps/recipes/etl/upsert.py`

- Путь: `v2/backend/apps/recipes/etl/upsert.py`
- Классы и функции: upsert_recipe
- Строк: 148

```python
"""Write a parsed recipe dict into Postgres (V1 ETL and draft overlay)."""

from __future__ import annotations

from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRevision,
    RecipeStep,
    RecipeVariant,
)


def upsert_recipe(item: dict) -> Recipe:
    recipe, _created = Recipe.objects.update_or_create(
        slug=item["slug"],
        defaults={
            "title": item["title"],
            "protein_base": item["protein_base"],
            "protein_bases_extra": item.get("protein_bases_extra") or [],
            "cook_method": item["cook_method"],
            "dish_type": item["dish_type"],
            "scale_mode": item.get("scale_mode") or "linear",
            "scalable": item.get("scalable", True),
            "servings": item.get("servings"),
            "yield_weight_g": item.get("yield_weight_g"),
            "yield_kind": item.get("yield_kind"),
            "summary": item.get("summary"),
            "source_name": item.get("source_name"),
            "source_url": item.get("source_url"),
            "source_type": item.get("source_type"),
            "editorial_tested": False,
            "high_risk_flags": item.get("high_risk_flags") or [],
            "caution_text": item.get("caution_text"),
            "energy_profile": item.get("energy_profile") or "standard",
            "status": item.get("status") or "published",
            "ingredient_titles": item.get("ingredient_titles") or "",
            "equipment": item.get("equipment"),
            "allowed_cuts": item.get("allowed_cuts") or [],
            "notes": item.get("notes") or [],
            "prep": item.get("prep") or [],
            "time_total_minutes": item.get("time_total_minutes"),
            "time_active_minutes": item.get("time_active_minutes"),
            "effort_level": item.get("effort_level"),
            "washing_level": item.get("washing_level"),
            "use_cases": item.get("use_cases") or [],
            "adaptations": item.get("adaptations") or [],
        },
    )
    recipe.full_clean(exclude=["search_vector"])
    recipe.save()

    # Title/allergens only — nutrition columns are filled by load_ingredient_nutrition.
    for canon in item.get("new_canons") or []:
        Ingredient.objects.update_or_create(
            canonical_id=canon["canonical_id"],
            defaults={
                "title": canon.get("title") or canon["canonical_id"],
                "aliases": canon.get("aliases") or [],
                "allergens_contains": canon.get("contains") or [],
                "allergens_may_contain": canon.get("may_contain") or [],
                "allergens_unknown": canon.get("unknown") or [],
            },
        )

    RecipeIngredient.objects.filter(recipe=recipe).delete()
    RecipeStep.objects.filter(recipe=recipe).delete()
    RecipeVariant.objects.filter(recipe=recipe).delete()

    for line in item["lines"]:
        ingredient, _ = Ingredient.objects.update_or_create(
            canonical_id=line["canonical_id"],
            defaults={
                "title": line["ingredient_title"],
                "aliases": line.get("aliases") or [],
                "allergens_contains": line.get("contains") or [],
                "allergens_may_contain": line.get("may_contain") or [],
                "allergens_unknown": line.get("unknown") or [],
            },
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            position=line["position"],
            amount=line.get("amount"),
            amount_max=line.get("amount_max"),
            unit=line["unit"],
            detail=line.get("detail"),
            scale_mode=line.get("scale_mode") or "linear",
            scalable=bool(line.get("scalable", True)),
            is_anchor=bool(line.get("is_anchor")),
            optional=bool(line.get("optional", False)),
            nutrition_exclude=bool(line.get("nutrition_exclude")),
            nutrition_factor=line.get("nutrition_factor"),
            choice_group=line.get("choice_group"),
            display_name=line.get("display_name"),
        )
    for step in item["steps"]:
        RecipeStep.objects.create(
            recipe=recipe,
            position=step["position"],
            text=step["text"],
            timer_seconds=step.get("timer_seconds"),
            timer_label=step.get("timer_label"),
            timer_note=step.get("timer_note"),
            pull_internal_temperature_c=step.get("pull_internal_temperature_c"),
            target_internal_temperature_c=step.get("target_internal_temperature_c"),
            hold_seconds=step.get("hold_seconds"),
            equipment_note=step.get("equipment_note"),
        )
    for variant in item.get("variants") or []:
        RecipeVariant.objects.create(
            recipe=recipe,
            axis=variant["axis"],
            code=variant["code"],
            title=variant["title"],
            has_delta=bool(variant.get("has_delta")),
            legacy_text=variant.get("legacy_text"),
            ingredient_delta=variant.get("ingredient_delta"),
            step_delta=variant.get("step_delta"),
            allergen_delta=variant.get("allergen_delta"),
            high_risk_delta=variant.get("high_risk_delta") or {},
            cook_method_override=variant.get("cook_method_override"),
            protein_base_override=variant.get("protein_base_override"),
            equipment=variant.get("equipment"),
            caution_text_override=variant.get("caution_text_override"),
        )

    payload = {
        "slug": item["slug"],
        "title": item["title"],
        "origin": item.get("origin") or "v1",
        "protein_base": item["protein_base"],
        "cook_method": item["cook_method"],
        "dish_type": item["dish_type"],
        "raw": item.get("raw"),
    }
    RecipeRevision.objects.update_or_create(
        recipe=recipe,
        status="published",
        defaults={"payload_json": payload},
    )
    from apps.recipes.services.snapshots import refresh_axis_snapshots

    recipe.refresh_from_db()
    refresh_axis_snapshots(recipe)
    return recipe
```

---

## 13. `backend/apps/recipes/exceptions.py`

- Путь: `v2/backend/apps/recipes/exceptions.py`
- Классы и функции: api_exception_handler
- Строк: 13

```python
from rest_framework.views import exception_handler

from apps.prep.exceptions import PrepError
from apps.recipes.services.assemble import VariantError
from apps.recipes.services.scale import ScaleConflict


def api_exception_handler(exc, context):
    if isinstance(exc, (ScaleConflict, VariantError, PrepError)):
        from rest_framework.response import Response

        return Response({"detail": str(exc)}, status=400)
    return exception_handler(exc, context)
```

---

## 14. `backend/apps/recipes/management/commands/audit_core_ids.py`

- Путь: `v2/backend/apps/recipes/management/commands/audit_core_ids.py`
- Классы и функции: Command
- Строк: 35

```python
"""List published recipes with required assembled lines missing canonical_id."""

from django.core.management.base import BaseCommand

from apps.recipes.models import Recipe
from apps.recipes.services.assemble import VariantError, assemble_recipe


class Command(BaseCommand):
    help = "Сироты canonical_id в обязательных строках опубликованных рецептов."

    def handle(self, *args, **options):
        found = 0
        qs = Recipe.objects.filter(status="published").prefetch_related(
            "ingredients__ingredient", "variants", "steps"
        )
        for recipe in qs:
            try:
                assembled = assemble_recipe(recipe, enrich=False)
            except VariantError as exc:
                self.stderr.write(f"{recipe.slug}: {exc}")
                continue
            orphans = [
                (line.get("name") or "?").strip() or "?"
                for line in assembled.ingredients
                if not (line.get("canonical_id") or "").strip() and not line.get("optional")
            ]
            if not orphans:
                continue
            found += 1
            self.stdout.write(f"{recipe.slug}: {', '.join(orphans)}")
        if found == 0:
            self.stdout.write("сирот canonical_id нет")
            return
        self.stdout.write(f"итого {found}")
```

---

## 15. `backend/apps/recipes/management/commands/export_draft.py`

- Путь: `v2/backend/apps/recipes/management/commands/export_draft.py`
- Классы и функции: Command
- Строк: 42

```python
"""Write a live Recipe from Postgres as author draft JSON."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.recipes.etl.serialize import recipe_to_draft
from apps.recipes.models import Recipe


class Command(BaseCommand):
    help = "Выгрузить рецепт из БД в JSON черновика (для правки и import_draft --path)."

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True, help="slug рецепта")
        parser.add_argument(
            "--path",
            type=str,
            help="Куда писать. По умолчанию stdout.",
        )

    def handle(self, *args, **options):
        slug = options["slug"].strip()
        try:
            recipe = Recipe.objects.prefetch_related(
                "ingredients__ingredient", "steps", "variants"
            ).get(slug=slug)
        except Recipe.DoesNotExist as exc:
            raise CommandError(f"Нет рецепта {slug}") from exc
        payload = recipe_to_draft(recipe)
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        dest = options.get("path")
        if dest:
            path = Path(dest)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            self.stdout.write(f"записан {path}")
            return
        self.stdout.write(text)
```

---

## 16. `backend/apps/recipes/management/commands/import_draft.py`

- Путь: `v2/backend/apps/recipes/management/commands/import_draft.py`
- Классы и функции: Command, drafts_root, v1_map_path
- Строк: 123

```python
"""Import V2 recipe drafts into Postgres (overlay after import_v1)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.recipes.etl.draft import (
    DraftError,
    known_from_v1_map,
    load_json,
    parse_draft,
    validate_draft,
)
from apps.recipes.etl.nutrition import load_ingredient_nutrition
from apps.recipes.etl.upsert import upsert_recipe


def drafts_root() -> Path:
    candidates: list[Path] = []
    docs_root = os.environ.get("DOCS_ROOT")
    if docs_root:
        candidates.append(Path(docs_root) / "drafts")
    candidates.append(Path(settings.V1_DATA_ROOT) / "v2" / "docs" / "drafts")
    candidates.append(Path(__file__).resolve().parents[5] / "docs" / "drafts")
    for candidate in candidates:
        if (candidate / "recipes").is_dir():
            return candidate
    return candidates[0]


def v1_map_path() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "v1_ingredient_map.json"


class Command(BaseCommand):
    help = (
        "Validate and upsert V2 draft recipes. "
        "--path один файл; --accepted все *.json в drafts/recipes/; "
        "пустая папка — успех, не ошибка. Вердикт Terra для импорта не нужен."
    )

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Один файл черновика")
        parser.add_argument(
            "--accepted",
            action="store_true",
            help="Все JSON в drafts/recipes/ (без reviews)",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Только валидатор, без записи",
        )

    def handle(self, *args, **options):
        root = drafts_root()
        recipes_dir = root / "recipes"
        try:
            known = known_from_v1_map(json.loads(v1_map_path().read_text(encoding="utf-8")))
        except OSError as exc:
            raise CommandError(f"Нет сида ингредиентов: {exc}") from exc

        paths: list[Path] = []
        if options.get("path"):
            paths = [Path(options["path"])]
        elif options.get("accepted") or options.get("check"):
            if recipes_dir.is_dir():
                paths = sorted(recipes_dir.glob("*.json"))
        else:
            raise CommandError("Укажите --path FILE или --accepted или --check")

        if not paths:
            self.stdout.write("Черновиков нет.")
            return

        imported = 0
        skipped = 0
        fail_fast = bool(options.get("path"))
        for path in paths:
            if path.name.startswith("_"):
                continue
            try:
                raw = load_json(path)
            except DraftError as exc:
                if fail_fast:
                    raise CommandError(str(exc)) from exc
                skipped += 1
                self.stdout.write(f"пропуск {path.name}: {exc}")
                continue
            errors = validate_draft(raw, overlay=True, known_ingredients=known)
            slug = (raw.get("id") or raw.get("slug") or path.stem).strip()
            if errors:
                for item in errors:
                    self.stderr.write(item)
                msg = f"{path.name}: валидатор {len(errors)} ошибок"
                if fail_fast:
                    raise CommandError(msg)
                skipped += 1
                self.stdout.write(f"пропуск {slug}: {msg}")
                continue
            if options.get("check") and not options.get("accepted"):
                self.stdout.write(f"OK {slug}")
                continue
            try:
                item = parse_draft(raw, known_ingredients=known)
            except DraftError as exc:
                if fail_fast:
                    raise CommandError(str(exc)) from exc
                skipped += 1
                self.stdout.write(f"пропуск {slug}: {exc}")
                continue
            with transaction.atomic():
                upsert_recipe(item)
                load_ingredient_nutrition()
            imported += 1
            self.stdout.write(f"записан {slug}")
        self.stdout.write(f"готово imported={imported} skipped={skipped}")
```

---

## 17. `backend/apps/recipes/management/commands/import_v1.py`

- Путь: `v2/backend/apps/recipes/management/commands/import_v1.py`
- Классы и функции: Command, run_import
- Строк: 359

```python
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.content.models import ContentDocument
from apps.recipes.constants import (
    EXPECTED_CONTENT_DOCUMENTS,
    V1_FOLDER_TO_COOK_METHOD,
    V1_FOLDER_TO_EQUIPMENT,
    slugify_ru,
)
from apps.recipes.etl.ingredients import (
    infer_scale_mode,
    is_anchor_candidate,
    is_optional_line,
    map_unit_and_amount,
    parse_amount,
)
from apps.recipes.etl.load import (
    V1ImportError,
    folder_from_rel,
    load_recipe_objects,
    resolve_v1_root,
)
from apps.recipes.etl.nutrition import load_ingredient_nutrition
from apps.recipes.etl.taxonomy import (
    CAUTION_TEXT,
    POULTRY_TEMP_SLUGS,
    RECIPE_TAXONOMY,
    TEMP_REQUIRED_SLUGS,
)
from apps.recipes.etl.upsert import upsert_recipe
from apps.recipes.models import Recipe
from apps.recipes.services.notes import split_notes_blob
from apps.recipes.services.substitutions import upsert_substitution_rules

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

CONTENT_SOURCES = [
    ("guide", "grains", "Крупы", "data/grains.json"),
    ("guide", "tips", "Советы", "data/tips.json"),
    ("meat", "beef", "Говядина", "data/meat-beef.json"),
    ("meat", "pork", "Свинина", "data/meat-pork.json"),
    ("meat", "poultry", "Птица", "data/meat-poultry.json"),
]


class Command(BaseCommand):
    help = "Import V1 catalog JSON into Postgres (upsert, one transaction)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print a report and write nothing.",
        )

    def handle(self, *args, **options):
        data_root = resolve_v1_root(Path(settings.V1_DATA_ROOT))
        dry_run = options["dry_run"]
        try:
            report = run_import(data_root, dry_run=dry_run)
        except V1ImportError as exc:
            raise CommandError(str(exc)) from exc
        for line in report:
            self.stdout.write(line)


def run_import(data_root: Path, *, dry_run: bool) -> list[str]:
    recipes = load_recipe_objects(data_root)
    ingredient_map = _load_json(FIXTURES / "v1_ingredient_map.json")
    temp_seed = _load_json(FIXTURES / "v1_step_temperatures.json")
    _validate_seed_coverage(recipes, ingredient_map, temp_seed)

    parsed = [_parse_recipe(rel, raw, ingredient_map, temp_seed) for rel, raw in recipes]
    unique_names = {name for _rel, raw in recipes for name in _ingredient_names(raw)}
    report = [
        f"V1_DATA_ROOT={data_root}",
        f"files={len({rel for rel, _ in recipes})}",
        f"recipes={len(parsed)}",
        f"unique_ingredient_names={len(unique_names)}",
        f"content_documents={EXPECTED_CONTENT_DOCUMENTS}",
        f"dry_run={dry_run}",
    ]
    if dry_run:
        report.append("Запись в БД пропущена.")
        return report

    skipped_overlay = 0
    with transaction.atomic():
        _upsert_content(data_root)
        for item in parsed:
            if _is_v2_overlay(item["slug"]):
                skipped_overlay += 1
                continue
            _upsert_recipe(item)
        docs = ContentDocument.objects.count()
        if docs != EXPECTED_CONTENT_DOCUMENTS:
            raise V1ImportError(
                f"ContentDocument.count={docs}, expected {EXPECTED_CONTENT_DOCUMENTS}"
            )
        load_ingredient_nutrition()
        subs = upsert_substitution_rules()
    report.append(
        f"записано recipes={Recipe.objects.count()} "
        f"skipped_overlay={skipped_overlay} "
        f"content={ContentDocument.objects.count()} substitutions={subs}"
    )
    return report


def _load_json(path: Path):
    if not path.is_file():
        raise V1ImportError(f"Нет сида {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _ingredient_names(raw: dict) -> list[str]:
    names = []
    for item in raw.get("ingredients") or []:
        if isinstance(item, dict) and item.get("name"):
            names.append(item["name"])
    return names


def _validate_seed_coverage(recipes, ingredient_map, temp_seed) -> None:
    missing_ing = []
    for _rel, raw in recipes:
        for name in _ingredient_names(raw):
            if name not in ingredient_map:
                missing_ing.append(name)
    if missing_ing:
        uniq = sorted(set(missing_ing))
        raise V1ImportError(
            "Нет ключа в v1_ingredient_map.json: " + ", ".join(uniq[:20])
            + (f" (+{len(uniq) - 20})" if len(uniq) > 20 else "")
        )
    missing_temp = sorted(TEMP_REQUIRED_SLUGS - set(temp_seed))
    if missing_temp:
        raise V1ImportError(
            "Нет сида температур для: " + ", ".join(missing_temp)
        )


def _parse_recipe(rel: str, raw: dict, ingredient_map: dict, temp_seed: dict) -> dict:
    slug = raw["id"]
    if slug not in RECIPE_TAXONOMY:
        raise V1ImportError(f"Нет taxonomy для {slug}")
    protein_base, dish_type = RECIPE_TAXONOMY[slug]
    folder = folder_from_rel(rel)
    cook_method = V1_FOLDER_TO_COOK_METHOD.get(folder)
    if not cook_method:
        raise V1ImportError(f"Неизвестная папка V1 {folder} ({rel})")
    equipment = V1_FOLDER_TO_EQUIPMENT.get(folder)

    lines = []
    anchor_index = None
    titles = []
    for position, item in enumerate(raw.get("ingredients") or []):
        if not isinstance(item, dict):
            raise V1ImportError(f"{slug}: ингредиент не объект")
        name = item.get("name") or ""
        mapped = ingredient_map[name]
        amount = parse_amount(item.get("amount"))
        amount_max = parse_amount(item.get("amount_max"))
        v1_unit = item.get("unit")
        unit, amount = map_unit_and_amount(v1_unit, amount)
        if v1_unit == "стакана" and amount_max is not None:
            amount_max = amount_max * Decimal("250")
        scalable = item.get("scalable", True)
        if unit in {"to_taste", "pinch"}:
            amount = None
            amount_max = None
            scalable = False
        if amount is None and unit not in {"to_taste", "pinch"}:
            detail = (item.get("detail") or "").lower()
            if "щепот" in detail:
                unit = "pinch"
            else:
                unit = "to_taste"
            scalable = False
        scale_mode = infer_scale_mode(name, unit, item.get("scale_mode"))
        if is_anchor_candidate(scalable, amount, unit) and anchor_index is None:
            anchor_index = position
        titles.append(mapped.get("title") or name)
        lines.append(
            {
                "canonical_id": mapped["canonical_id"],
                "ingredient_title": mapped["title"],
                "contains": mapped.get("contains") or [],
                "may_contain": mapped.get("may_contain") or [],
                "unknown": mapped.get("unknown") or [],
                "position": position,
                "amount": amount,
                "amount_max": amount_max if unit not in {"to_taste", "pinch"} else None,
                "unit": unit,
                "detail": item.get("detail"),
                "scale_mode": scale_mode,
                "scalable": bool(scalable),
                "is_anchor": False,
                "optional": is_optional_line(item.get("detail")),
                "display_name": name,
            }
        )
    if anchor_index is not None:
        lines[anchor_index]["is_anchor"] = True

    steps = _parse_steps(slug, raw.get("steps") or [], temp_seed)
    if slug in TEMP_REQUIRED_SLUGS:
        targets = {
            step["target_internal_temperature_c"]
            for step in steps
            if step["target_internal_temperature_c"] is not None
        }
        if not targets:
            raise V1ImportError(f"{slug}: нет target в сиде температур")
        if slug in {
            "classic-roast-chicken",
            "kuritsa-maslo-limon-zapechennaya",
            "kuritsa-s-yablokami-zapechennaya",
            "kuritsa-tselikom-limonnoe-maslo-bazovyy",
        } and not ({72, 82} <= targets):
            raise V1ImportError(f"{slug}: целая птица требует target 72 и 82")

    flags = []
    caution = None
    if slug in POULTRY_TEMP_SLUGS:
        flags = ["poultry_temp"]
        caution = CAUTION_TEXT.get(slug)
        if not caution:
            raise V1ImportError(f"{slug}: poultry_temp без caution_text")

    source_url = (raw.get("source_url") or "").strip() or None
    return {
        "slug": slug,
        "title": raw["title"],
        "protein_base": protein_base,
        "cook_method": cook_method,
        "dish_type": dish_type,
        "summary": raw.get("summary"),
        "source_name": raw.get("source_name") or None,
        "source_url": source_url,
        "source_type": raw.get("source_type") or None,
        "ingredient_titles": " ".join(titles),
        "equipment": equipment,
        "allowed_cuts": [],
        "notes": split_notes_blob(raw.get("notes")),
        "prep": raw.get("prep") or [],
        "variants": _parse_legacy_variants(raw.get("variations") or []),
        "high_risk_flags": flags,
        "caution_text": caution,
        "lines": lines,
        "steps": steps,
        "origin": "v1",
        "raw": raw,
    }


def _parse_steps(slug: str, raw_steps: list, temp_seed: dict) -> list[dict]:
    rules = temp_seed.get(slug) or []
    used = [False] * len(rules)
    out = []
    for position, step in enumerate(raw_steps):
        if isinstance(step, str):
            text = step
            timer_min = None
            timer_label = None
            timer_note = None
        elif isinstance(step, dict):
            text = step.get("text") or ""
            timer_min = step.get("timer_min")
            timer_label = step.get("timer_label")
            timer_note = step.get("timer_note")
        else:
            raise V1ImportError(f"{slug}: шаг {position} неизвестного типа")
        pull = target = hold = None
        for i, rule in enumerate(rules):
            if used[i]:
                continue
            needle = rule["match"]
            if needle.lower() in text.lower():
                used[i] = True
                pull = rule.get("pull_internal_temperature_c")
                target = rule.get("target_internal_temperature_c")
                hold = rule.get("hold_seconds")
                break
        out.append(
            {
                "position": position,
                "text": text,
                "timer_seconds": int(timer_min * 60) if timer_min is not None else None,
                "timer_label": timer_label,
                "timer_note": timer_note,
                "pull_internal_temperature_c": pull,
                "target_internal_temperature_c": target,
                "hold_seconds": hold,
            }
        )
    unused = [rules[i]["match"] for i, flag in enumerate(used) if not flag]
    if unused:
        raise V1ImportError(f"{slug}: сид температур не совпал со шагами: {unused}")
    return out


def _parse_legacy_variants(raw_variations: list) -> list[dict]:
    used: set[str] = set()
    out = []
    for item in raw_variations:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip() or "Вариация"
        out.append(
            {
                "axis": "addon",
                "code": slugify_ru(title, used=used),
                "title": title,
                "has_delta": False,
                "legacy_text": item.get("text") or "",
                "ingredient_delta": None,
                "step_delta": None,
                "allergen_delta": None,
                "high_risk_delta": {},
                "cook_method_override": None,
                "protein_base_override": None,
                "equipment": None,
                "caution_text_override": None,
            }
        )
    return out


def _upsert_content(data_root: Path) -> None:
    for type_name, slug, title, rel in CONTENT_SOURCES:
        path = data_root / rel
        if not path.is_file():
            raise V1ImportError(f"Нет справочника {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        ContentDocument.objects.update_or_create(
            type=type_name,
            slug=slug,
            defaults={"title": title, "payload_json": payload},
        )


def _is_v2_overlay(slug: str) -> bool:
    """Overlay/wave rows have time_profile; do not roll them back to V1 JSON."""
    return Recipe.objects.filter(slug=slug, time_total_minutes__isnull=False).exists()


def _upsert_recipe(item: dict) -> None:
    upsert_recipe(item)
```

---

## 18. `backend/apps/recipes/management/commands/rebuild_axis_snapshots.py`

- Путь: `v2/backend/apps/recipes/management/commands/rebuild_axis_snapshots.py`
- Классы и функции: Command
- Строк: 20

```python
"""Rebuild calculator axis snapshots for published recipes."""

from django.core.management.base import BaseCommand

from apps.recipes.models import Recipe
from apps.recipes.services.snapshots import refresh_axis_snapshots


class Command(BaseCommand):
    help = "Собрать axis_snapshots для солвера калькулятора."

    def handle(self, *args, **options):
        qs = Recipe.objects.filter(status="published").prefetch_related(
            "ingredients__ingredient", "variants", "steps"
        )
        written = 0
        for recipe in qs:
            refresh_axis_snapshots(recipe)
            written += 1
        self.stdout.write(f"снимки: {written}")
```

---

## 19. `backend/apps/recipes/models.py`

- Путь: `v2/backend/apps/recipes/models.py`
- Классы и функции: NormalizeRu, ToTsVector, Recipe, RecipeVariant, RecipeRevision, Ingredient, RecipeIngredient, SubstitutionRule, RecipeStep
- Строк: 383

```python
"""Recipe catalog models — live card on Recipe, not joined to revisions (DATA-MODEL)."""

from __future__ import annotations

from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, GeneratedField, Value
from django.db.models.functions import Coalesce, Concat

from apps.recipes.constants import (
    COOK_METHOD,
    CUT,
    DISH_TYPE,
    ENERGY_PROFILE,
    EQUIPMENT,
    HIGH_RISK,
    NUTRITION_BASIS,
    NUTRITION_SOURCE,
    PROTEIN_BASE,
    RECIPE_STATUS,
    SCALE_MODE,
    UNIT,
    USE_CASE,
    VARIANT_AXIS,
    YIELD_KIND,
)


def _choice(codes: frozenset[str]) -> list[tuple[str, str]]:
    return [(code, code) for code in sorted(codes)]


class NormalizeRu(models.Func):
    """Postgres normalize_ru(text) — ё→е, lower. Not unaccent."""

    function = "normalize_ru"
    output_field = models.TextField()
    arity = 1


class ToTsVector(models.Func):
    function = "to_tsvector"
    output_field = SearchVectorField()

    def __init__(self, config: str, expression):
        super().__init__(Value(config), expression)


class Recipe(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.TextField()
    protein_base = models.CharField(max_length=32, choices=_choice(PROTEIN_BASE))
    cook_method = models.CharField(max_length=32, choices=_choice(COOK_METHOD))
    dish_type = models.CharField(max_length=32, choices=_choice(DISH_TYPE))
    scale_mode = models.CharField(
        max_length=16, choices=_choice(SCALE_MODE), default="linear"
    )
    scalable = models.BooleanField(default=True)
    servings = models.PositiveIntegerField(null=True, blank=True)
    yield_weight_g = models.DecimalField(
        max_digits=8, decimal_places=1, null=True, blank=True
    )
    yield_kind = models.CharField(
        max_length=16, choices=_choice(YIELD_KIND), null=True, blank=True
    )
    summary = models.TextField(null=True, blank=True)
    source_name = models.TextField(null=True, blank=True)
    source_url = models.URLField(max_length=500, null=True, blank=True)
    source_type = models.TextField(null=True, blank=True)
    editorial_tested = models.BooleanField(default=False)
    high_risk_flags = ArrayField(
        models.CharField(max_length=32, choices=_choice(HIGH_RISK)),
        default=list,
        blank=True,
    )
    caution_text = models.TextField(null=True, blank=True)
    energy_profile = models.CharField(
        max_length=16, choices=_choice(ENERGY_PROFILE), default="standard"
    )
    equipment = models.CharField(
        max_length=32, choices=_choice(EQUIPMENT), null=True, blank=True
    )
    allowed_cuts = ArrayField(
        models.CharField(max_length=32, choices=_choice(CUT)),
        default=list,
        blank=True,
    )
    protein_bases_extra = ArrayField(
        models.CharField(max_length=32, choices=_choice(PROTEIN_BASE)),
        default=list,
        blank=True,
    )
    notes = models.JSONField(default=list, blank=True)
    prep = models.JSONField(default=list, blank=True)
    time_total_minutes = models.PositiveIntegerField(null=True, blank=True)
    time_active_minutes = models.PositiveIntegerField(null=True, blank=True)
    effort_level = models.PositiveSmallIntegerField(null=True, blank=True)
    washing_level = models.PositiveSmallIntegerField(null=True, blank=True)
    use_cases = ArrayField(
        models.CharField(max_length=32, choices=_choice(USE_CASE)),
        default=list,
        blank=True,
    )
    adaptations = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=_choice(RECIPE_STATUS), default="published"
    )
    # Denormalized for generated FTS: title + ingredient_titles + summary.
    ingredient_titles = models.TextField(default="", blank=True)
    search_vector = GeneratedField(
        expression=ToTsVector(
            "russian",
            NormalizeRu(
                Concat(
                    F("title"),
                    Value(" ", output_field=models.TextField()),
                    F("ingredient_titles"),
                    Value(" ", output_field=models.TextField()),
                    Coalesce(
                        F("summary"),
                        Value("", output_field=models.TextField()),
                    ),
                    output_field=models.TextField(),
                )
            ),
        ),
        output_field=SearchVectorField(),
        db_persist=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    axis_snapshots = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(
                OpClass(NormalizeRu("title"), name="gin_trgm_ops"),
                name="recipe_title_trgm",
            ),
        ]

    def __str__(self) -> str:
        return self.slug

    def clean(self) -> None:
        flags = list(self.high_risk_flags or [])
        if self.status == "published" and flags and not (self.caution_text or "").strip():
            raise ValidationError(
                "Нельзя публиковать high-risk рецепт без текста «Осторожно»."
            )
        unknown_flags = set(flags) - HIGH_RISK
        if unknown_flags:
            raise ValidationError(f"Неизвестный high-risk флаг: {sorted(unknown_flags)}")
        unknown_cases = set(self.use_cases or []) - USE_CASE
        if unknown_cases:
            raise ValidationError(f"Неизвестный use_case: {sorted(unknown_cases)}")
        for field in ("effort_level", "washing_level"):
            value = getattr(self, field)
            if value is not None and not 1 <= value <= 5:
                raise ValidationError(f"{field} должен быть 1–5.")
        total = self.time_total_minutes
        active = self.time_active_minutes
        if total is not None and active is not None and active > total:
            raise ValidationError("active_minutes не больше total_minutes.")
        if self.yield_weight_g is not None and self.yield_weight_g <= 0:
            raise ValidationError("yield_weight_g должен быть > 0.")
        if self.yield_kind and self.yield_kind not in YIELD_KIND:
            raise ValidationError(f"Неизвестный yield_kind: {self.yield_kind}")
        if self.yield_kind and self.yield_weight_g is None:
            raise ValidationError("yield_kind без yield_weight_g.")
        extra = list(self.protein_bases_extra or [])
        unknown_extra = set(extra) - PROTEIN_BASE
        if unknown_extra:
            raise ValidationError(f"Неизвестная extra-основа: {sorted(unknown_extra)}")
        if self.protein_base in extra:
            raise ValidationError("protein_bases_extra не дублирует protein_base.")

    def anchor_row(self) -> RecipeIngredient | None:
        return self.ingredients.filter(is_anchor=True).select_related("ingredient").first()


class RecipeVariant(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="variants")
    axis = models.CharField(max_length=16, choices=_choice(VARIANT_AXIS))
    code = models.SlugField(max_length=80)
    title = models.TextField()
    has_delta = models.BooleanField(default=False)
    legacy_text = models.TextField(null=True, blank=True)
    ingredient_delta = models.JSONField(null=True, blank=True)
    step_delta = models.JSONField(null=True, blank=True)
    allergen_delta = models.JSONField(null=True, blank=True)
    high_risk_delta = models.JSONField(default=dict, blank=True)
    cook_method_override = models.CharField(
        max_length=32, choices=_choice(COOK_METHOD), null=True, blank=True
    )
    protein_base_override = models.CharField(
        max_length=32, choices=_choice(PROTEIN_BASE), null=True, blank=True
    )
    equipment = models.CharField(
        max_length=32, choices=_choice(EQUIPMENT), null=True, blank=True
    )
    caution_text_override = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["axis", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "axis", "code"],
                name="recipes_variant_unique_axis_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipe.slug}:{self.axis}:{self.code}"


class RecipeRevision(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="revisions"
    )
    payload_json = models.JSONField()
    status = models.CharField(max_length=16, choices=_choice(RECIPE_STATUS))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Ingredient(models.Model):
    canonical_id = models.SlugField(max_length=80, unique=True)
    title = models.TextField()
    aliases = ArrayField(models.TextField(), default=list, blank=True)
    density_g_per_ml = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    kcal_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    protein_g_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    fat_g_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    carbs_g_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    nutrition_basis = models.CharField(
        max_length=16, choices=_choice(NUTRITION_BASIS), null=True, blank=True
    )
    nutrition_source = models.CharField(
        max_length=32, choices=_choice(NUTRITION_SOURCE), null=True, blank=True
    )
    nutrition_source_id = models.TextField(null=True, blank=True)
    g_per_tsp = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_tbsp = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_pcs = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_clove = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_bunch = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_slice = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    allergens_contains = ArrayField(models.CharField(max_length=32), default=list, blank=True)
    allergens_may_contain = ArrayField(
        models.CharField(max_length=32), default=list, blank=True
    )
    allergens_unknown = ArrayField(models.CharField(max_length=32), default=list, blank=True)

    def __str__(self) -> str:
        return self.canonical_id


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="recipe_lines"
    )
    position = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    amount_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=16, choices=_choice(UNIT))
    detail = models.TextField(null=True, blank=True)
    scale_mode = models.CharField(
        max_length=16, choices=_choice(SCALE_MODE), default="linear"
    )
    scalable = models.BooleanField(default=True)
    is_anchor = models.BooleanField(default=False)
    optional = models.BooleanField(default=False)
    nutrition_exclude = models.BooleanField(default=False)
    nutrition_factor = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    choice_group = models.TextField(null=True, blank=True)
    display_name = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe"],
                condition=models.Q(is_anchor=True),
                name="recipes_one_anchor_per_recipe",
            ),
        ]

    def clean(self) -> None:
        if self.unit in {"to_taste", "pinch"}:
            if self.amount is not None:
                raise ValidationError("Для «по вкусу»/щепотки amount должен быть пустым.")
            if self.scalable:
                raise ValidationError("to_taste/pinch не масштабируются.")
        if self.nutrition_exclude and self.nutrition_factor is not None:
            raise ValidationError("nutrition_factor не вместе с nutrition_exclude.")
        if self.nutrition_factor is not None and not (
            Decimal("0.01") <= self.nutrition_factor <= Decimal("1")
        ):
            raise ValidationError("nutrition_factor должен быть 0.01–1.")


class SubstitutionRule(models.Model):
    from_ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="substitutions_from"
    )
    to_ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="substitutions_to"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="substitution_rules",
        null=True,
        blank=True,
    )
    quality = models.DecimalField(max_digits=3, decimal_places=2)
    forbidden = models.BooleanField(default=False)
    note = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_ingredient", "to_ingredient"],
                condition=models.Q(recipe__isnull=True),
                name="recipes_sub_unique_global",
            ),
            models.UniqueConstraint(
                fields=["from_ingredient", "to_ingredient", "recipe"],
                condition=models.Q(recipe__isnull=False),
                name="recipes_sub_unique_recipe",
            ),
        ]

    def __str__(self) -> str:
        scope = self.recipe.slug if self.recipe_id else "global"
        return f"{self.from_ingredient_id}->{self.to_ingredient_id}@{scope}"


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    position = models.PositiveIntegerField()
    text = models.TextField()
    timer_seconds = models.PositiveIntegerField(null=True, blank=True)
    timer_label = models.TextField(null=True, blank=True)
    timer_note = models.TextField(null=True, blank=True)
    pull_internal_temperature_c = models.PositiveIntegerField(null=True, blank=True)
    target_internal_temperature_c = models.PositiveIntegerField(null=True, blank=True)
    hold_seconds = models.PositiveIntegerField(null=True, blank=True)
    equipment_note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["position"]

    def clean(self) -> None:
        if (
            self.pull_internal_temperature_c is not None
            and self.target_internal_temperature_c is None
        ):
            raise ValidationError("Заполнен pull без target — ошибка SAFETY.")
```

---

## 20. `backend/apps/recipes/pantry_vocab.py`

- Путь: `v2/backend/apps/recipes/pantry_vocab.py`
- Классы и функции: shopping_ids, shopping_label, likely_items_for_have_group, items_for_have_group, groups_to_expand, availability_class
- Строк: 729

```python
"""Supermarket pantry dictionary for the calculator.

Not protein_base VOCAB. UI shows coarse HAVE_UI_GROUPS, then likely items.
Canonical IDs may exist before any recipe uses them.
"""

from __future__ import annotations

PANTRY_ASSUMED = frozenset(
    {
        "water",
        "salt",
        "coarse_salt",
        "sugar",
        "black_pepper",
        "vegetable_oil",
    }
)

PANTRY_COMMON = frozenset(
    {
        "paprika",
        "dried_garlic",
        "dried_dill",
        "dried_parsley",
        "oregano",
        "dried_basil",
        "bay_leaf",
        "cumin",
        "curry",
        "mustard",
        "soy_sauce",
        "vinegar",
    }
)

# Not ordinary cupboard, not assumed, do not fail a recipe.
PANTRY_EXOTIC = frozenset(
    {
        "cardamom",
        "garam_masala",
        "kashmiri_chili",
        "ginger_paste",
        "rosemary",
        "fresh_basil",
        "mint",
        "cloves",
        "cinnamon",
        "turmeric",
        "coriander",
        "cilantro",
        "parsley",
        "sesame",
        "msg",
        "ginger",
    }
)

# ETL blobs: recipe instructions, not products. Skip shopping; do not treat as "in the cupboard".
PANTRY_LEGACY_OR = frozenset(
    {
        "water_or_stock",
        "stock_or_water",
        "water_and_apple_vinegar",
    }
)

PANTRY_SPICES = PANTRY_COMMON | PANTRY_EXOTIC

SHOPPING_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "meat",
        "Мясо и птица",
        (
            "chicken_breast",
            "chicken_thighs",
            "chicken_drumsticks",
            "chicken_wings",
            "whole_chicken",
            "chicken_mince",
            "pork_mince",
            "pork_neck",
            "pork_shoulder",
            "pork_loin",
            "pork_tenderloin",
            "pork_chops",
            "pork_ribs",
            "pork_belly",
            "pork_knuckle",
            "pork_leg",
            "bacon",
            "ham",
            "beef_mince",
            "beef_tenderloin",
            "steak",
            "beef_thick_rib",
            "ribeye",
            "beef_thin_rib",
            "beef_chuck",
            "beef_neck",
            "beef",
            "beef_round",
            "beef_rump",
            "beef_brisket",
            "beef_ribs",
            "beef_flank",
            "beef_shank",
            "beef_shank_bone_in",
            "beef_tail",
            "lamb_mince",
            "lamb_shoulder",
            "lamb_neck",
            "lamb_chops",
            "lamb_ribs",
            "lamb_shank",
            "lamb_leg",
            "beef_liver",
            "pork_liver",
            "chicken_liver",
            "beef_heart",
            "chicken_hearts",
            "beef_tongue",
            "kidney",
            "chicken_gizzards",
            "rabbit",
        ),
    ),
    (
        "fish",
        "Рыба",
        (
            "pollock",
            "hake",
            "cod",
            "mackerel",
            "herring",
            "pink_salmon",
            "salmon",
            "trout",
            "river_fish",
            "canned_tuna",
            "canned_sardine",
        ),
    ),
    (
        "grains",
        "Крупы и паста",
        (
            "buckwheat",
            "rice",
            "oatmeal",
            "millet",
            "pearl_barley",
            "bulgur",
            "couscous",
            "pasta",
            "spaghetti",
            "noodles",
            "wheat_flour",
        ),
    ),
    (
        "potatoes",
        "Картофель и гарнир",
        ("potato", "mashed_potato", "french_fries"),
    ),
    (
        "veg",
        "Овощи",
        (
            "onion",
            "red_onion",
            "green_onion",
            "shallot",
            "carrot",
            "garlic",
            "cabbage",
            "red_cabbage",
            "bell_pepper",
            "tomato",
            "cucumber",
            "zucchini",
            "eggplant",
            "beetroot",
            "pumpkin",
            "broccoli",
            "cauliflower",
            "green_beans",
            "corn",
        ),
    ),
    (
        "frozen",
        "Заморозка",
        (
            "frozen_vegetables",
            "frozen_peas",
            "frozen_corn",
            "frozen_green_beans",
            "frozen_spinach",
        ),
    ),
    (
        "dairy",
        "Молочное и яйца",
        (
            "eggs",
            "egg",
            "milk",
            "sour_cream",
            "yogurt",
            "cream",
            "butter",
            "cottage_cheese",
            "hard_cheese",
            "parmesan",
            "cream_cheese",
        ),
    ),
    (
        "legumes",
        "Бобовые",
        (
            "beans",
            "chickpeas",
            "lentils",
            "peas",
            "canned_beans",
            "canned_chickpeas",
        ),
    ),
    (
        "canned",
        "Консервы",
        (
            "canned_tomatoes",
            "tomato_paste",
            "tomato_puree",
            "canned_corn",
            "canned_green_peas",
            "canned_beans",
            "canned_fish",
            "canned_tuna",
            "olives",
            "pickles",
        ),
    ),
    (
        "fats",
        "Масло и жиры",
        ("sunflower_oil", "vegetable_oil", "olive_oil", "butter"),
    ),
    (
        "sauces",
        "Соусы и заправки",
        (
            "tomato_sauce",
            "ketchup",
            "mayonnaise",
            "soy_sauce",
            "mustard",
            "sour_cream",
        ),
    ),
    (
        "bakery",
        "Хлеб и выпечка",
        ("bread", "white_bread", "rye_bread", "lavash", "breadcrumbs"),
    ),
)

SHOPPING_GROUP_LABEL_RU = {code: title for code, title, _ids in SHOPPING_GROUPS}
SHOPPING_GROUP_IDS = {code: ids for code, _title, ids in SHOPPING_GROUPS}

FISH_FRESH = frozenset(
    {
        "pollock",
        "hake",
        "cod",
        "mackerel",
        "herring",
        "pink_salmon",
        "salmon",
        "trout",
        "river_fish",
    }
)
FISH_CANNED = frozenset({"canned_tuna", "canned_sardine", "canned_fish"})
FISH_PROTEIN = frozenset({"fish_white_sea", "fish_red_sea", "fish_river", "fish_canned", "seafood"})

_CHICKEN = (
    "chicken_breast",
    "chicken_thighs",
    "chicken_drumsticks",
    "chicken_wings",
    "whole_chicken",
    "chicken_mince",
)
_PORK = (
    "pork_mince",
    "pork_neck",
    "pork_shoulder",
    "pork_loin",
    "pork_tenderloin",
    "pork_chops",
    "pork_ribs",
    "pork_belly",
    "pork_knuckle",
    "pork_leg",
    "bacon",
    "ham",
)
_BEEF = (
    "beef_mince",
    "beef_tenderloin",
    "steak",
    "beef_thick_rib",
    "ribeye",
    "beef_thin_rib",
    "beef_chuck",
    "beef_neck",
    "beef",
    "beef_round",
    "beef_rump",
    "beef_brisket",
    "beef_ribs",
    "beef_flank",
    "beef_shank",
    "beef_shank_bone_in",
    "beef_tail",
)
_LAMB = (
    "lamb_mince",
    "lamb_shoulder",
    "lamb_neck",
    "lamb_chops",
    "lamb_ribs",
    "lamb_shank",
    "lamb_leg",
)
_OFFAL = (
    "beef_liver",
    "pork_liver",
    "chicken_liver",
    "beef_heart",
    "chicken_hearts",
    "beef_tongue",
    "kidney",
    "chicken_gizzards",
    "rabbit",
)

HAVE_GROUPS: dict[str, tuple[str, ...]] = {
    "chicken": _CHICKEN,
    "pork": _PORK,
    "beef": _BEEF,
    "lamb": _LAMB,
    "offal": _OFFAL,
    "meat": _PORK + _BEEF + _LAMB + _OFFAL,
    "fish": SHOPPING_GROUP_IDS["fish"],
    "veg": SHOPPING_GROUP_IDS["veg"] + SHOPPING_GROUP_IDS["potatoes"],
    "grains": SHOPPING_GROUP_IDS["grains"],
    "dairy": tuple(cid for cid in SHOPPING_GROUP_IDS["dairy"] if cid not in {"eggs", "egg"}),
    "eggs": ("eggs", "egg"),
    "legumes": SHOPPING_GROUP_IDS["legumes"],
    "canned": SHOPPING_GROUP_IDS["canned"],
    "frozen": SHOPPING_GROUP_IDS["frozen"],
    "bakery": SHOPPING_GROUP_IDS["bakery"],
    "sauces": SHOPPING_GROUP_IDS["sauces"],
    "fats": SHOPPING_GROUP_IDS["fats"],
}

HAVE_GROUPS["other"] = tuple(
    dict.fromkeys(
        HAVE_GROUPS["legumes"]
        + HAVE_GROUPS["canned"]
        + HAVE_GROUPS["frozen"]
        + HAVE_GROUPS["bakery"]
        + HAVE_GROUPS["sauces"]
        + HAVE_GROUPS["fats"]
    )
)

HAVE_GROUP_LABEL_RU = {
    "chicken": "Курица",
    "pork": "Свинина",
    "beef": "Говядина",
    "lamb": "Баранина",
    "offal": "Другое",
    "meat": "Мясо",
    "fish": "Рыба",
    "veg": "Овощи",
    "grains": "Крупы",
    "dairy": "Молочное",
    "eggs": "Яйца",
    "legumes": "Бобовые",
    "canned": "Консервы",
    "frozen": "Заморозка",
    "bakery": "Хлеб",
    "sauces": "Соусы",
    "fats": "Масло",
    "other": "Другое",
}

HAVE_UI_GROUPS = ("chicken", "meat", "fish", "veg", "grains", "eggs", "dairy", "other")

# First screen: coarse chips. Meat opens species, then supermarket cuts.
HAVE_GROUP_CHILDREN: dict[str, tuple[str, ...]] = {
    "meat": ("pork", "beef", "lamb", "offal"),
}

HAVE_GROUP_PROTEIN = {
    "chicken": frozenset({"poultry"}),
    "pork": frozenset({"pork"}),
    "beef": frozenset({"beef"}),
    "lamb": frozenset({"lamb"}),
    "offal": frozenset({"offal"}),
    "meat": frozenset({"beef", "pork", "lamb", "offal"}),
    "fish": FISH_PROTEIN,
    "eggs": frozenset({"eggs_dairy"}),
    "veg": frozenset({"vegetables", "vegetarian"}),
    "legumes": frozenset({"legumes"}),
}

SHOPPING_LIKELY: dict[str, tuple[str, ...]] = {
    "chicken": ("chicken_thighs", "chicken_breast", "chicken_drumsticks", "whole_chicken"),
    "meat": ("beef_mince", "pork_mince", "pork_neck", "steak", "bacon"),
    "pork": ("pork_neck", "pork_mince", "pork_chops", "bacon"),
    "beef": ("beef_mince", "beef_chuck", "steak"),
    "fish": ("pollock", "hake", "mackerel", "canned_tuna"),
    "veg": (
        "onion",
        "carrot",
        "potato",
        "tomato",
        "cucumber",
        "cabbage",
        "bell_pepper",
        "zucchini",
    ),
    "grains": ("buckwheat", "rice", "oatmeal", "pasta"),
    "eggs": ("eggs",),
    "dairy": ("milk", "sour_cream", "cottage_cheese", "butter", "hard_cheese"),
    "other": (
        "canned_tomatoes",
        "canned_tuna",
        "beans",
        "bread",
        "sunflower_oil",
    ),
}

CANONICAL_INGREDIENT_LABEL_RU: dict[str, str] = {
    "chicken_breast": "куриная грудка",
    "chicken_thighs": "куриные бёдра",
    "chicken_drumsticks": "куриные голени",
    "chicken_wings": "куриные крылья",
    "whole_chicken": "курица целиком",
    "chicken_mince": "куриный фарш",
    "pork_neck": "свиная шея",
    "pork_shoulder": "свиная лопатка",
    "pork_loin": "свиная корейка",
    "pork_chops": "свиные отбивные",
    "pork_ribs": "свиные рёбра",
    "pork_belly": "свиная грудинка",
    "pork_mince": "свиной фарш",
    "pork_tenderloin": "свиная вырезка",
    "pork_knuckle": "рулька",
    "pork_leg": "окорок",
    "bacon": "бекон",
    "ham": "ветчина",
    "beef_mince": "говяжий фарш",
    "beef_tenderloin": "говяжья вырезка",
    "beef": "говядина",
    "beef_thick_rib": "толстый край",
    "beef_thin_rib": "тонкий край",
    "beef_chuck": "говяжья лопатка",
    "beef_neck": "говяжья шея",
    "beef_round": "мякоть",
    "beef_rump": "говяжий огузок",
    "beef_brisket": "говяжья грудинка",
    "beef_ribs": "говяжьи рёбра",
    "beef_flank": "пашина",
    "beef_shank": "говяжья голяшка",
    "beef_shank_bone_in": "голяшка на кости",
    "beef_tail": "говяжий хвост",
    "steak": "стейк",
    "ribeye": "рибай",
    "lamb_mince": "бараний фарш",
    "lamb_shoulder": "баранья лопатка",
    "lamb_neck": "баранья шея",
    "lamb_chops": "бараньи отбивные",
    "lamb_ribs": "бараньи рёбра",
    "lamb_shank": "баранья голяшка",
    "lamb_leg": "бараний окорок",
    "beef_liver": "печень говяжья",
    "pork_liver": "печень свиная",
    "chicken_liver": "печень куриная",
    "beef_heart": "сердце говяжье",
    "chicken_hearts": "куриные сердечки",
    "beef_tongue": "язык говяжий",
    "kidney": "почки",
    "chicken_gizzards": "куриные желудочки",
    "rabbit": "кролик",
    "pollock": "минтай",
    "hake": "хек",
    "cod": "треска",
    "mackerel": "скумбрия",
    "herring": "сельдь",
    "pink_salmon": "горбуша",
    "salmon": "лосось",
    "trout": "форель",
    "river_fish": "речная рыба",
    "canned_tuna": "тунец консервированный",
    "canned_sardine": "сардины консервированные",
    "canned_fish": "рыбные консервы",
    "buckwheat": "гречка",
    "rice": "рис",
    "oatmeal": "овсянка",
    "millet": "пшено",
    "pearl_barley": "перловка",
    "bulgur": "булгур",
    "couscous": "кускус",
    "pasta": "макароны",
    "spaghetti": "спагетти",
    "noodles": "лапша",
    "wheat_flour": "мука",
    "potato": "картофель",
    "mashed_potato": "картофельное пюре",
    "french_fries": "картофель фри",
    "onion": "лук",
    "red_onion": "красный лук",
    "green_onion": "зелёный лук",
    "shallot": "лук-шалот",
    "carrot": "морковь",
    "garlic": "чеснок",
    "cabbage": "капуста",
    "red_cabbage": "красная капуста",
    "bell_pepper": "болгарский перец",
    "tomato": "помидоры",
    "cucumber": "огурец",
    "zucchini": "кабачок",
    "eggplant": "баклажан",
    "beetroot": "свёкла",
    "pumpkin": "тыква",
    "broccoli": "брокколи",
    "cauliflower": "цветная капуста",
    "green_beans": "стручковая фасоль",
    "corn": "кукуруза",
    "frozen_vegetables": "замороженные овощи",
    "frozen_peas": "замороженный горошек",
    "frozen_corn": "замороженная кукуруза",
    "frozen_green_beans": "замороженная стручковая фасоль",
    "frozen_spinach": "замороженный шпинат",
    "eggs": "яйца",
    "egg": "яйцо",
    "milk": "молоко",
    "sour_cream": "сметана",
    "yogurt": "йогурт",
    "cream": "сливки",
    "butter": "сливочное масло",
    "cottage_cheese": "творог",
    "hard_cheese": "твёрдый сыр",
    "parmesan": "пармезан",
    "cream_cheese": "сливочный сыр",
    "beans": "фасоль",
    "chickpeas": "нут",
    "lentils": "чечевица",
    "peas": "горох",
    "canned_beans": "фасоль консервированная",
    "canned_chickpeas": "нут консервированный",
    "canned_tomatoes": "томаты в банке",
    "tomato_paste": "томатная паста",
    "tomato_puree": "томатное пюре",
    "canned_corn": "кукуруза консервированная",
    "canned_green_peas": "зелёный горошек",
    "olives": "оливки",
    "pickles": "соленья",
    "sunflower_oil": "подсолнечное масло",
    "vegetable_oil": "растительное масло",
    "olive_oil": "оливковое масло",
    "tomato_sauce": "томатный соус",
    "ketchup": "кетчуп",
    "mayonnaise": "майонез",
    "soy_sauce": "соевый соус",
    "mustard": "горчица",
    "bread": "хлеб",
    "white_bread": "белый хлеб",
    "rye_bread": "чёрный хлеб",
    "lavash": "лаваш",
    "breadcrumbs": "сухари",
    "stock": "бульон",
    "vegetable_stock": "овощной бульон",
}

HAVE_TEXT_ALIASES = {
    "курица": "chicken",
    "курицу": "chicken",
    "курицы": "chicken",
    "курятина": "chicken",
    "курятину": "chicken",
    "свинина": "pork",
    "свинину": "pork",
    "говядина": "beef",
    "говядину": "beef",
    "говяжий фарш": "beef_mince",
    "говяжья вырезка": "beef_tenderloin",
    "вырезка говяжья": "beef_tenderloin",
    "говяжья шея": "beef_neck",
    "говяжья мякоть": "beef_round",
    "мякоть говядины": "beef_round",
    "толстый край": "beef_thick_rib",
    "тонкий край": "beef_thin_rib",
    "говяжьи ребра": "beef_ribs",
    "говяжья лопатка": "beef_chuck",
    "свиная вырезка": "pork_tenderloin",
    "рулька": "pork_knuckle",
    "окорок": "pork_leg",
    "баранина": "lamb",
    "баранину": "lamb",
    "бараний фарш": "lamb_mince",
    "печень говяжья": "beef_liver",
    "язык говяжий": "beef_tongue",
    "кролик": "rabbit",
    "мясо": "meat",
    "рыба": "fish",
    "рыбу": "fish",
    "минтай": "pollock",
    "хек": "hake",
    "треска": "cod",
    "тунец": "canned_tuna",
    "овощи": "veg",
    "крупа": "grains",
    "крупы": "grains",
    "лук": "onion",
    "луковица": "onion",
    "морковь": "carrot",
    "картошка": "potato",
    "картофель": "potato",
    "помидор": "tomato",
    "помидоры": "tomato",
    "томат": "tomato",
    "томаты": "tomato",
    "перец болгарский": "bell_pepper",
    "болгарский перец": "bell_pepper",
    "капуста": "cabbage",
    "огурец": "cucumber",
    "огурцы": "cucumber",
    "чеснок": "garlic",
    "кабачок": "zucchini",
    "баклажан": "eggplant",
    "свекла": "beetroot",
    "тыква": "pumpkin",
    "гречка": "buckwheat",
    "гречку": "buckwheat",
    "гречневая крупа": "buckwheat",
    "рис": "rice",
    "рисовую крупу": "rice",
    "овсянка": "oatmeal",
    "овсяные хлопья": "oatmeal",
    "макароны": "pasta",
    "спагетти": "spaghetti",
    "перловка": "pearl_barley",
    "пшено": "millet",
    "молоко": "milk",
    "сметана": "sour_cream",
    "сливки": "cream",
    "творог": "cottage_cheese",
    "сыр": "hard_cheese",
    "яйца": "eggs",
    "яйцо": "egg",
    "растительное масло": "vegetable_oil",
    "подсолнечное масло": "sunflower_oil",
    "сливочное масло": "butter",
    "оливковое масло": "olive_oil",
    "фасоль": "beans",
    "нут": "chickpeas",
    "чечевица": "lentils",
    "горох": "peas",
    "кукуруза": "canned_corn",
    "горошек": "canned_green_peas",
    "хлеб": "bread",
    "молочное": "dairy",
    "молочка": "dairy",
}


def shopping_ids() -> set[str]:
    ids: set[str] = set(CANONICAL_INGREDIENT_LABEL_RU)
    for group_ids in HAVE_GROUPS.values():
        ids.update(group_ids)
    for _code, _title, group_ids in SHOPPING_GROUPS:
        ids.update(group_ids)
    return ids


def shopping_label(cid: str, titles: dict[str, str] | None = None) -> str:
    if titles and cid in titles:
        return titles[cid]
    return CANONICAL_INGREDIENT_LABEL_RU.get(cid, cid)


def likely_items_for_have_group(code: str) -> tuple[str, ...]:
    return SHOPPING_LIKELY.get(code, ())


def items_for_have_group(code: str) -> tuple[str, ...]:
    return tuple(HAVE_GROUPS.get(code, ()))


def groups_to_expand(have_groups: list[str]) -> list[str]:
    """Skip parent group if a child species is already selected."""
    selected = set(have_groups)
    skip = {
        parent
        for parent, children in HAVE_GROUP_CHILDREN.items()
        if selected & set(children)
    }
    return [code for code in have_groups if code not in skip]


def availability_class(canonical_id: str) -> str:
    if canonical_id in PANTRY_ASSUMED or canonical_id in PANTRY_LEGACY_OR:
        return "assumed"
    if canonical_id in PANTRY_COMMON:
        return "common"
    if canonical_id in PANTRY_EXOTIC:
        return "exotic"
    return "explicit"
```

---

## 21. `backend/apps/recipes/query.py`

- Путь: `v2/backend/apps/recipes/query.py`
- Классы и функции: BadQuery, split_query_values, parse_codes, parse_optional_code, parse_have, parse_have_groups, parse_intent, parse_without_allergens, parse_sample, parse_optional_decimal
- Строк: 157

```python
"""Query helpers for catalog filters (same key OR, different keys AND)."""

from __future__ import annotations

from rest_framework.exceptions import APIException

from apps.recipes.constants import (
    ALLERGEN,
    COOK_METHOD,
    CUT,
    DISH_TYPE,
    EQUIPMENT,
    HAVE_GROUPS,
    INTENT,
    PROTEIN_BASE,
)


class BadQuery(APIException):
    status_code = 400
    default_detail = "Некорректный запрос."
    default_code = "bad_query"

FILTER_VOCAB = {
    "protein_base": PROTEIN_BASE,
    "cook_method": COOK_METHOD,
    "dish_type": DISH_TYPE,
    "equipment": EQUIPMENT,
    "cuts": CUT,
}


def split_query_values(request, key: str) -> list[str]:
    values: list[str] = []
    for raw in request.query_params.getlist(key):
        values.extend(part.strip() for part in raw.split(",") if part.strip())
    return values


def parse_codes(request, key: str) -> list[str]:
    allowed = FILTER_VOCAB[key]
    values = split_query_values(request, key)
    unknown = [code for code in values if code not in allowed]
    if unknown:
        raise BadQuery(f"Неизвестный код {key}: {', '.join(unknown)}")
    return values


def parse_optional_code(request, key: str, allowed: set[str]) -> str | None:
    raw = request.query_params.get(key)
    if raw is None or raw == "":
        return None
    value = str(raw).strip()
    if value not in allowed:
        raise BadQuery(f"Неизвестный код {key}: {value}")
    return value


def parse_have(
    request, known: set[str] | None = None, titles: dict[str, str] | None = None
) -> list[str]:
    """Pantry: shopping canonical, group, or Russian alias. Unknown → 400."""
    from apps.recipes.models import Ingredient
    from apps.recipes.pantry_vocab import CANONICAL_INGREDIENT_LABEL_RU, shopping_ids
    from apps.recipes.services.pantry import resolve_pantry_text, resolve_token

    values = split_query_values(request, "have")
    if not values:
        return []
    db_ids: set[str] = set()
    db_titles: dict[str, str] = {}
    if known is None:
        db_ids = set(Ingredient.objects.values_list("canonical_id", flat=True))
        db_titles = dict(Ingredient.objects.values_list("canonical_id", "title"))
    else:
        db_ids = set(known)
        db_titles = dict(titles or {})
    known = shopping_ids() | db_ids
    titles = {**CANONICAL_INGREDIENT_LABEL_RU, **db_titles}
    found: list[str] = []
    seen: set[str] = set()
    unknown: list[str] = []
    for raw in values:
        ids = resolve_token(raw, titles=titles, known=known)
        extra_unknown: list[str] = []
        if not ids:
            ids, extra_unknown = resolve_pantry_text(raw, titles=titles, known=known)
        if not ids:
            unknown.append(raw)
            continue
        unknown.extend(extra_unknown)
        for cid in ids:
            if cid not in seen:
                seen.add(cid)
                found.append(cid)
    if unknown:
        raise BadQuery(f"Неизвестный продукт: {', '.join(unknown)}")
    return found


def parse_have_groups(request) -> list[str]:
    values = split_query_values(request, "have_group")
    unknown = [code for code in values if code not in HAVE_GROUPS]
    if unknown:
        raise BadQuery(f"Неизвестный код have_group: {', '.join(unknown)}")
    return values


def parse_intent(request) -> list[str]:
    values = split_query_values(request, "intent")
    unknown = [code for code in values if code not in INTENT]
    if unknown:
        raise BadQuery(f"Неизвестный код intent: {', '.join(unknown)}")
    return values


def parse_without_allergens(request) -> list[str]:
    """«без чего»: `without` (preferred CSV) or `exclude_allergen`.

    Recipe is dropped if allergens.contains OR allergens.unknown includes the code.
    may_contain does not drop.
    """
    values = split_query_values(request, "without") or split_query_values(
        request, "exclude_allergen"
    )
    unknown = [code for code in values if code not in ALLERGEN]
    if unknown:
        raise BadQuery(f"Неизвестный код аллергена: {', '.join(unknown)}")
    return values


def parse_sample(request) -> int | None:
    raw = request.query_params.get("sample")
    if raw is None or raw == "":
        return None
    try:
        n = int(raw)
    except (TypeError, ValueError):
        raise BadQuery("Некорректный sample") from None
    if n < 1 or n > 24:
        raise BadQuery("sample должен быть от 1 до 24")
    return n


def parse_optional_decimal(request, key: str):
    raw = request.query_params.get(key)
    if raw is None or raw == "":
        return None
    from decimal import Decimal, InvalidOperation

    try:
        value = Decimal(str(raw).replace(",", "."))
    except (InvalidOperation, ValueError) as exc:
        raise BadQuery(f"Некорректное значение {key}.") from exc
    if value <= 0:
        raise BadQuery(f"{key} должен быть больше нуля.")
    return value
```

---

## 22. `backend/apps/recipes/serializers.py`

- Путь: `v2/backend/apps/recipes/serializers.py`
- Классы и функции: catalog_scaling, serialize_recipe_list_item, serialize_display_line, serialize_display_step, serialize_recipe_detail
- Строк: 185

```python
from __future__ import annotations

from decimal import Decimal

from apps.recipes.models import Recipe
from apps.recipes.services.assemble import (
    AssembledRecipe,
    catalog_allergens,
    catalog_protein_bases,
    catalog_protein_variants,
    pick_anchor,
)
from apps.recipes.services.nutrition import (
    compute_recipe_nutrition,
    nutrition_line_projection,
    nutrition_skip_hint,
)
from apps.recipes.services.scale import (
    ScaleResult,
    format_display_amount,
    scale_line,
)


def _num(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def catalog_scaling(recipe: Recipe) -> dict:
    has_anchor = any(line.is_anchor for line in recipe.ingredients.all())
    enabled = bool(recipe.scalable) and (recipe.servings is not None or has_anchor)
    return {"enabled": enabled}


def serialize_recipe_list_item(recipe: Recipe) -> dict:
    variants = list(recipe.variants.all())
    return {
        "slug": recipe.slug,
        "title": recipe.title,
        "protein_base": recipe.protein_base,
        "protein_bases": catalog_protein_bases(recipe),
        "protein_variants": catalog_protein_variants(recipe),
        "cook_method": recipe.cook_method,
        "dish_type": recipe.dish_type,
        "equipment": recipe.equipment,
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "summary": recipe.summary,
        "editorial_tested": recipe.editorial_tested,
        "high_risk_flags": list(recipe.high_risk_flags or []),
        "allergens": catalog_allergens(recipe),
        "has_delta_variants": any(
            item.axis == "addon" and item.has_delta for item in variants
        ),
        "scaling": catalog_scaling(recipe),
        "time_profile": {
            "total_minutes": recipe.time_total_minutes,
            "active_minutes": recipe.time_active_minutes,
        },
        "effort_level": recipe.effort_level,
        "washing_level": recipe.washing_level,
        "use_cases": list(recipe.use_cases or []),
    }


def serialize_display_line(line: dict, scale: ScaleResult) -> dict:
    amount, amount_max = scale_line(
        amount=line.get("amount"),
        amount_max=line.get("amount_max"),
        unit=line["unit"],
        scale_mode=line.get("scale_mode") or "linear",
        scalable=bool(line.get("scalable", True)),
        ratio=scale.ratio,
        scaling_enabled=scale.enabled,
    )
    return {
        "name": line["name"],
        "amount": _num(amount),
        "amount_max": _num(amount_max),
        "unit": line["unit"],
        "detail": line.get("detail"),
        "scalable": bool(line.get("scalable", True)),
        "scale_mode": line.get("scale_mode") or "linear",
        "is_anchor": bool(line.get("is_anchor")),
        "optional": bool(line.get("optional")),
        "nutrition_exclude": bool(line.get("nutrition_exclude")),
        "nutrition_skip_hint": nutrition_skip_hint(line),
        "display_amount": format_display_amount(amount, line["unit"], amount_max),
        "nutrition_line": nutrition_line_projection(line),
    }


def serialize_display_step(step: dict) -> dict:
    return {
        "text": step.get("text") or "",
        "timer_seconds": step.get("timer_seconds"),
        "timer_label": step.get("timer_label"),
        "timer_note": step.get("timer_note"),
        "pull_internal_temperature_c": step.get("pull_internal_temperature_c"),
        "target_internal_temperature_c": step.get("target_internal_temperature_c"),
        "hold_seconds": step.get("hold_seconds"),
    }


def serialize_recipe_detail(
    recipe: Recipe, assembled: AssembledRecipe, scale: ScaleResult
) -> dict:
    ingredients = [serialize_display_line(line, scale) for line in assembled.ingredients]
    steps = [serialize_display_step(step) for step in assembled.steps]
    anchor = pick_anchor(assembled.ingredients)
    base_anchor = scale.base_anchor
    if base_anchor is None and anchor and anchor.get("amount") is not None:
        from apps.recipes.services.scale import base_anchor_amount

        converted = base_anchor_amount(anchor["amount"], anchor["unit"])
        if converted:
            base_val, base_unit = converted
            base_anchor = {
                "amount": _num(base_val),
                "unit": base_unit,
                "name": anchor.get("name") or "",
            }
    can_scale = bool(recipe.scalable) and (
        recipe.servings is not None or base_anchor is not None
    )
    if not can_scale:
        scaling = {"enabled": False, "mode": "off", "ratio": 1, "base_anchor": base_anchor}
    else:
        scaling = {
            "enabled": True,
            "mode": scale.mode,
            "ratio": float(scale.ratio),
            "base_anchor": base_anchor,
            "applied": scale.applied,
        }
    nutrition = compute_recipe_nutrition(
        assembled.ingredients,
        servings=recipe.servings,
        ratio=scale.ratio,
        scaling_enabled=scale.enabled,
        yield_weight_g=recipe.yield_weight_g,
    )
    return {
        "slug": recipe.slug,
        "title": recipe.title,
        "protein_base": assembled.protein_base,
        "home_protein_base": recipe.protein_base,
        "cook_method": assembled.cook_method,
        "dish_type": recipe.dish_type,
        "equipment": assembled.equipment,
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "applied_axes": assembled.applied_axes,
        "available_variants": assembled.available_variants,
        "available_equipment": assembled.available_equipment,
        "summary": recipe.summary,
        "source_name": recipe.source_name,
        "source_url": recipe.source_url or None,
        "editorial_tested": recipe.editorial_tested,
        "high_risk_flags": assembled.high_risk_flags,
        "caution_text": assembled.caution_text,
        "allergens": assembled.allergens,
        "nutrition": nutrition,
        "scaling": scaling,
        "servings": recipe.servings,
        "yield_weight_g": _num(recipe.yield_weight_g),
        "yield_kind": recipe.yield_kind,
        "ingredients": ingredients,
        "steps": steps,
        "variations": assembled.variations,
        "notes": assembled.notes,
        "prep": assembled.prep,
        "time_profile": {
            "total_minutes": recipe.time_total_minutes,
            "active_minutes": recipe.time_active_minutes,
        },
        "effort_level": recipe.effort_level,
        "washing_level": recipe.washing_level,
        "use_cases": list(recipe.use_cases or []),
        "adaptations": recipe.adaptations if isinstance(recipe.adaptations, list) else [],
    }
```

---

## 23. `backend/apps/recipes/services/__init__.py`

- Путь: `v2/backend/apps/recipes/services/__init__.py`
- Классы и функции: нет классов/функций верхнего уровня
- Строк: 1

```python
# domain services
```

---

## 24. `backend/apps/recipes/services/allergens.py`

- Путь: `v2/backend/apps/recipes/services/allergens.py`
- Классы и функции: merge_allergen_lists, recipe_allergens_from_ingredients, normalize_ru
- Строк: 41

```python
"""Allergen merge. unknown never collapses to «нет»."""

from __future__ import annotations

from collections.abc import Iterable


def merge_allergen_lists(
    rows: Iterable[tuple[list[str], list[str], list[str]]],
) -> dict[str, list[str]]:
    contains: set[str] = set()
    may_contain: set[str] = set()
    unknown: set[str] = set()
    for c, m, u in rows:
        contains.update(c or [])
        may_contain.update(m or [])
        unknown.update(u or [])
    may_contain -= contains
    unknown -= contains
    return {
        "contains": sorted(contains),
        "may_contain": sorted(may_contain),
        "unknown": sorted(unknown),
    }


def recipe_allergens_from_ingredients(ingredients) -> dict[str, list[str]]:
    rows = (
        (
            list(ing.allergens_contains or []),
            list(ing.allergens_may_contain or []),
            list(ing.allergens_unknown or []),
        )
        for ing in ingredients
    )
    return merge_allergen_lists(rows)


def normalize_ru(text: str) -> str:
    """Mirror of SQL normalize_ru: lower + ё→е. Not unaccent."""
    return (text or "").translate(str.maketrans("Ёё", "Ее")).lower()
```

---

## 25. `backend/apps/recipes/services/assemble.py`

- Путь: `v2/backend/apps/recipes/services/assemble.py`
- Классы и функции: VariantError, AssembledRecipe, lines_from_recipe, allergen_lines_from_recipe, steps_from_recipe, apply_ingredient_delta, apply_step_delta, apply_allergen_delta, allergens_from_lines, apply_high_risk, count_anchors, pick_anchor, available_equipment_codes, resolve_axes, assemble_display, assemble_recipe, catalog_allergens, catalog_protein_bases, catalog_protein_variants
- Строк: 572

```python
"""Assemble display recipe: base → addon → equipment, then scale separately."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from apps.recipes.services.allergens import merge_allergen_lists
from apps.recipes.services.nutrition import CANON_NUTRITION_FIELDS, enrich_lines_from_db


class VariantError(Exception):
    """Unknown or illegal variant / equipment query — API 400."""


def _d(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _copy_line(line: dict) -> dict:
    out = deepcopy(line)
    if out.get("amount") is not None:
        out["amount"] = _d(out["amount"])
    if out.get("amount_max") is not None:
        out["amount_max"] = _d(out["amount_max"])
    return out


def _nutrition_from_ingredient(ing) -> dict:
    return {field: getattr(ing, field) for field in CANON_NUTRITION_FIELDS}


def lines_from_recipe(recipe, *, include_nutrition: bool = True) -> list[dict]:
    rows = []
    for line in recipe.ingredients.all():
        ing = line.ingredient
        row = {
            "canonical_id": ing.canonical_id,
            "name": line.display_name or ing.title,
            "amount": line.amount,
            "amount_max": line.amount_max,
            "unit": line.unit,
            "detail": line.detail,
            "scalable": line.scalable,
            "scale_mode": line.scale_mode,
            "is_anchor": line.is_anchor,
            "optional": bool(line.optional),
            "nutrition_exclude": bool(line.nutrition_exclude),
            "nutrition_factor": line.nutrition_factor,
            "position": line.position,
            "allergens_contains": list(ing.allergens_contains or []),
            "allergens_may_contain": list(ing.allergens_may_contain or []),
            "allergens_unknown": list(ing.allergens_unknown or []),
        }
        if include_nutrition:
            row.update(_nutrition_from_ingredient(ing))
        rows.append(row)
    return rows


def allergen_lines_from_recipe(recipe) -> list[dict]:
    """List/catalog worst-case allergens: no nutrition, no step payload."""
    rows = []
    for line in recipe.ingredients.all():
        ing = line.ingredient
        rows.append(
            {
                "canonical_id": ing.canonical_id,
                "name": line.display_name or ing.title,
                "position": line.position,
                "optional": bool(line.optional),
                "allergens_contains": list(ing.allergens_contains or []),
                "allergens_may_contain": list(ing.allergens_may_contain or []),
                "allergens_unknown": list(ing.allergens_unknown or []),
            }
        )
    return rows


def steps_from_recipe(recipe) -> list[dict]:
    return [
        {
            "position": step.position,
            "text": step.text,
            "timer_seconds": step.timer_seconds,
            "timer_label": step.timer_label,
            "timer_note": step.timer_note,
            "pull_internal_temperature_c": step.pull_internal_temperature_c,
            "target_internal_temperature_c": step.target_internal_temperature_c,
            "hold_seconds": step.hold_seconds,
        }
        for step in recipe.steps.all()
    ]


def _find_line(lines: list[dict], spec: dict) -> int | None:
    if spec.get("position") is not None:
        pos = int(spec["position"])
        for i, line in enumerate(lines):
            if line.get("position") == pos:
                return i
        if 0 <= pos < len(lines):
            return pos
        return None
    cid = spec.get("canonical_id")
    if not cid:
        return None
    hits = [i for i, line in enumerate(lines) if line.get("canonical_id") == cid]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return None
    return None


def apply_ingredient_delta(lines: list[dict], delta: dict | None) -> list[dict]:
    if not delta:
        return [_copy_line(line) for line in lines]
    out = [_copy_line(line) for line in lines]
    for spec in delta.get("remove") or []:
        idx = _find_line(out, spec)
        if idx is not None:
            out.pop(idx)
    for spec in delta.get("replace") or []:
        idx = _find_line(out, spec)
        if idx is None:
            continue
        current = out[idx]
        merged = _copy_line(current)
        old_cid = current.get("canonical_id")
        for key in (
            "canonical_id",
            "name",
            "amount",
            "amount_max",
            "unit",
            "detail",
            "scalable",
            "scale_mode",
            "optional",
            "allergens_contains",
            "allergens_may_contain",
            "allergens_unknown",
        ):
            if key in spec and spec[key] is not None:
                merged[key] = spec[key]
        if merged.get("amount") is not None:
            merged["amount"] = _d(merged["amount"])
        if merged.get("amount_max") is not None:
            merged["amount_max"] = _d(merged["amount_max"])
        if "is_anchor" in spec:
            merged["is_anchor"] = bool(spec["is_anchor"])
        else:
            merged["is_anchor"] = bool(current.get("is_anchor"))
        if "optional" in spec:
            merged["optional"] = bool(spec["optional"])
        else:
            merged["optional"] = bool(current.get("optional"))
        if "nutrition_exclude" in spec:
            merged["nutrition_exclude"] = bool(spec["nutrition_exclude"])
        else:
            merged["nutrition_exclude"] = bool(current.get("nutrition_exclude"))
        if "nutrition_factor" in spec:
            merged["nutrition_factor"] = _d(spec.get("nutrition_factor"))
        elif "nutrition_factor" not in merged:
            merged["nutrition_factor"] = current.get("nutrition_factor")
        if merged.get("canonical_id") != old_cid:
            for field in CANON_NUTRITION_FIELDS:
                merged[field] = spec.get(field)
        else:
            for field in CANON_NUTRITION_FIELDS:
                if field in spec:
                    merged[field] = spec[field]
        out[idx] = merged
    next_pos = max((line.get("position") or 0) for line in out) + 1 if out else 0
    for spec in delta.get("add") or []:
        added = {
            "canonical_id": spec.get("canonical_id") or "",
            "name": spec.get("name") or spec.get("display_name") or spec.get("canonical_id") or "",
            "amount": _d(spec.get("amount")),
            "amount_max": _d(spec.get("amount_max")),
            "unit": spec.get("unit") or "g",
            "detail": spec.get("detail"),
            "scalable": spec.get("scalable", True),
            "scale_mode": spec.get("scale_mode") or "linear",
            "is_anchor": False,
            "optional": bool(spec.get("optional", False)),
            "nutrition_exclude": bool(spec.get("nutrition_exclude", False)),
            "nutrition_factor": _d(spec.get("nutrition_factor")),
            "position": spec.get("position", next_pos),
            "allergens_contains": list(
                spec.get("allergens_contains") or spec.get("contains") or []
            ),
            "allergens_may_contain": list(
                spec.get("allergens_may_contain") or spec.get("may_contain") or []
            ),
            "allergens_unknown": list(spec.get("allergens_unknown") or spec.get("unknown") or []),
        }
        for field in CANON_NUTRITION_FIELDS:
            added[field] = spec.get(field)
        next_pos = max(next_pos, int(added["position"]) + 1)
        out.append(added)
    return out


def apply_step_delta(steps: list[dict], delta: dict | None) -> list[dict]:
    if not delta:
        return [deepcopy(step) for step in steps]
    out = [deepcopy(step) for step in steps]
    for spec in delta.get("replace") or []:
        pos = spec.get("position")
        if pos is None:
            continue
        for step in out:
            if step.get("position") == pos:
                for key in (
                    "text",
                    "timer_seconds",
                    "timer_label",
                    "timer_note",
                    "pull_internal_temperature_c",
                    "target_internal_temperature_c",
                    "hold_seconds",
                ):
                    if key in spec:
                        step[key] = spec[key]
                break
    for spec in delta.get("insert") or []:
        after = spec.get("after_position", len(out))
        inserted = {
            "position": -1,
            "text": spec.get("text") or "",
            "timer_seconds": spec.get("timer_seconds"),
            "timer_label": spec.get("timer_label"),
            "timer_note": spec.get("timer_note"),
            "pull_internal_temperature_c": spec.get("pull_internal_temperature_c"),
            "target_internal_temperature_c": spec.get("target_internal_temperature_c"),
            "hold_seconds": spec.get("hold_seconds"),
        }
        insert_at = 0 if after == 0 else len(out)
        for i, step in enumerate(out):
            if step.get("position") == after:
                insert_at = i + 1
                break
        out.insert(insert_at, inserted)
    for i, step in enumerate(out):
        step["position"] = i
    return out


def apply_allergen_delta(base: dict[str, list[str]], delta: dict | None) -> dict[str, list[str]]:
    if not delta:
        return {
            "contains": list(base.get("contains") or []),
            "may_contain": list(base.get("may_contain") or []),
            "unknown": list(base.get("unknown") or []),
        }
    contains = set(base.get("contains") or [])
    may_contain = set(base.get("may_contain") or [])
    unknown = set(base.get("unknown") or [])
    contains.update(delta.get("contains_add") or [])
    contains -= set(delta.get("contains_remove") or [])
    may_contain.update(delta.get("may_contain_add") or [])
    may_contain -= set(delta.get("may_contain_remove") or [])
    unknown.update(delta.get("unknown_add") or [])
    unknown -= set(delta.get("unknown_remove") or [])
    return merge_allergen_lists(
        [(sorted(contains), sorted(may_contain), sorted(unknown))]
    )


def allergens_from_lines(lines: list[dict]) -> dict[str, list[str]]:
    """Required lines only. Garnish / «для подачи» do not mark the dish."""
    rows = (
        (
            list(line.get("allergens_contains") or []),
            list(line.get("allergens_may_contain") or []),
            list(line.get("allergens_unknown") or []),
        )
        for line in lines
        if not line.get("optional")
    )
    return merge_allergen_lists(rows)


def apply_high_risk(base_flags: list[str], delta: dict | None) -> list[str]:
    flags = set(base_flags or [])
    if delta:
        flags.update(delta.get("add") or [])
        flags -= set(delta.get("remove") or [])
    return sorted(flags)


def count_anchors(lines: list[dict]) -> int:
    return sum(1 for line in lines if line.get("is_anchor"))


def pick_anchor(lines: list[dict]) -> dict | None:
    hits = [line for line in lines if line.get("is_anchor")]
    if len(hits) > 1:
        raise VariantError("После сборки больше одного якоря.")
    return hits[0] if hits else None


@dataclass
class AssembledRecipe:
    ingredients: list[dict]
    steps: list[dict]
    allergens: dict[str, list[str]]
    high_risk_flags: list[str]
    caution_text: str | None
    cook_method: str
    protein_base: str
    equipment: str | None
    applied_axes: dict[str, str | None]
    available_variants: list[dict]
    available_equipment: list[str]
    variations: list[dict]
    notes: list[dict]
    prep: list
    has_delta_variants: bool = False
    extra: dict = field(default_factory=dict)


def _variant_payload(item) -> dict:
    return {
        "code": item.code,
        "title": item.title,
        "axis": item.axis,
        "has_delta": bool(item.has_delta),
        "legacy_text": item.legacy_text,
        "ingredient_delta": item.ingredient_delta,
        "step_delta": item.step_delta,
        "allergen_delta": item.allergen_delta,
        "high_risk_delta": item.high_risk_delta or {},
        "cook_method_override": getattr(item, "cook_method_override", None),
        "protein_base_override": getattr(item, "protein_base_override", None),
        "equipment": getattr(item, "equipment", None),
        "caution_text_override": getattr(item, "caution_text_override", None),
    }


def available_equipment_codes(recipe, variants: list) -> list[str]:
    codes: list[str] = []
    if recipe.equipment:
        codes.append(recipe.equipment)
    for item in variants:
        if item.axis != "equipment" or not item.has_delta:
            continue
        code = item.equipment or item.code
        if code and code not in codes:
            codes.append(code)
    return codes


def resolve_axes(
    *,
    recipe,
    variants: list,
    variant_code: str | None,
    equipment_code: str | None,
) -> tuple[Any | None, Any | None, str | None]:
    addons = [item for item in variants if item.axis == "addon"]
    addon = None
    if variant_code:
        addon = next((item for item in addons if item.code == variant_code), None)
        if addon is None:
            raise VariantError(f"Неизвестный код variant: {variant_code}")

    available = available_equipment_codes(recipe, variants)
    applied_equipment = recipe.equipment
    equipment_variant = None
    if equipment_code:
        # Family axis, not VOCAB equipment-only: air_fryer / steam live here
        # as cook_method codes with no vessel field (VOCAB, overlay axes).
        if equipment_code not in available:
            raise VariantError(f"Неизвестный код equipment: {equipment_code}")
        applied_equipment = equipment_code
        if equipment_code != recipe.equipment:
            equipment_variant = next(
                (
                    item
                    for item in variants
                    if item.axis == "equipment"
                    and item.has_delta
                    and (item.equipment or item.code) == equipment_code
                ),
                None,
            )
            if equipment_variant is None:
                raise VariantError(f"Неизвестный код equipment: {equipment_code}")
    return addon, equipment_variant, applied_equipment


def assemble_display(
    *,
    base_lines: list[dict],
    base_steps: list[dict],
    base_allergens: dict[str, list[str]],
    base_flags: list[str],
    base_caution: str | None,
    base_cook_method: str,
    base_protein_base: str,
    addon: dict | None,
    equipment: dict | None,
) -> tuple[list[dict], list[dict], dict[str, list[str]], list[str], str | None, str, str]:
    lines = [_copy_line(line) for line in base_lines]
    steps = [deepcopy(step) for step in base_steps]
    flags = list(base_flags or [])
    caution = base_caution
    cook_method = base_cook_method
    protein_base = base_protein_base
    allergen_deltas: list[dict] = []

    for axis in (addon, equipment):
        if not axis or not axis.get("has_delta"):
            continue
        lines = apply_ingredient_delta(lines, axis.get("ingredient_delta"))
        steps = apply_step_delta(steps, axis.get("step_delta"))
        flags = apply_high_risk(flags, axis.get("high_risk_delta"))
        if axis.get("allergen_delta"):
            allergen_deltas.append(axis["allergen_delta"])
        if axis.get("cook_method_override"):
            cook_method = axis["cook_method_override"]
        if axis.get("protein_base_override"):
            protein_base = axis["protein_base_override"]
        if axis.get("caution_text_override"):
            caution = axis["caution_text_override"]

    if count_anchors(lines) > 1:
        raise VariantError("После сборки больше одного якоря.")

    allergens = allergens_from_lines(lines)
    for delta in allergen_deltas:
        allergens = apply_allergen_delta(allergens, delta)
    return lines, steps, allergens, flags, caution, cook_method, protein_base


def assemble_recipe(
    recipe,
    *,
    variant_code: str | None = None,
    equipment_code: str | None = None,
    enrich: bool = True,
) -> AssembledRecipe:
    variants = list(recipe.variants.all())
    addon_obj, equipment_obj, applied_equipment = resolve_axes(
        recipe=recipe,
        variants=variants,
        variant_code=variant_code,
        equipment_code=equipment_code,
    )
    addon = _variant_payload(addon_obj) if addon_obj else None
    equipment = _variant_payload(equipment_obj) if equipment_obj else None
    lines, steps, allergens, flags, caution, cook_method, protein_base = assemble_display(
        base_lines=lines_from_recipe(recipe, include_nutrition=enrich),
        base_steps=steps_from_recipe(recipe),
        base_allergens={},
        base_flags=list(recipe.high_risk_flags or []),
        base_caution=recipe.caution_text,
        base_cook_method=recipe.cook_method,
        base_protein_base=recipe.protein_base,
        addon=addon,
        equipment=equipment,
    )
    if enrich:
        lines = enrich_lines_from_db(lines)
    addons = [item for item in variants if item.axis == "addon"]
    notes = recipe.notes if isinstance(recipe.notes, list) else []
    prep = recipe.prep if isinstance(recipe.prep, list) else []
    return AssembledRecipe(
        ingredients=lines,
        steps=steps,
        allergens=allergens,
        high_risk_flags=flags,
        caution_text=caution,
        cook_method=cook_method,
        protein_base=protein_base,
        equipment=applied_equipment,
        applied_axes={
            "variant": addon_obj.code if addon_obj else None,
            "equipment": applied_equipment,
        },
        available_variants=[
            {
                "code": item.code,
                "title": item.title,
                "axis": "addon",
                "has_delta": bool(item.has_delta),
                "protein_base": getattr(item, "protein_base_override", None),
            }
            for item in addons
        ],
        available_equipment=available_equipment_codes(recipe, variants),
        variations=[
            {"title": item.title, "text": item.legacy_text or ""}
            for item in addons
            if not item.has_delta
        ],
        notes=notes,
        prep=prep,
        has_delta_variants=any(item.has_delta for item in addons),
    )


def catalog_allergens(recipe) -> dict[str, list[str]]:
    """Worst case: base ∪ every addon with a real delta."""
    base_lines = allergen_lines_from_recipe(recipe)
    merged = [allergens_from_lines(base_lines)]
    for item in recipe.variants.all():
        if item.axis != "addon" or not item.has_delta:
            continue
        payload = _variant_payload(item)
        lines, _steps, allergens, _flags, _caution, _method, _protein = assemble_display(
            base_lines=base_lines,
            base_steps=[],
            base_allergens={},
            base_flags=[],
            base_caution=None,
            base_cook_method=recipe.cook_method,
            base_protein_base=recipe.protein_base,
            addon=payload,
            equipment=None,
        )
        merged.append(allergens)
        merged.append(allergens_from_lines(lines))
    rows = (
        (
            item.get("contains") or [],
            item.get("may_contain") or [],
            item.get("unknown") or [],
        )
        for item in merged
    )
    return merge_allergen_lists(rows)


def catalog_protein_bases(recipe) -> list[str]:
    ordered: list[str] = []

    def add(code: str | None) -> None:
        if code and code not in ordered:
            ordered.append(code)

    add(getattr(recipe, "protein_base", None))
    for code in getattr(recipe, "protein_bases_extra", None) or []:
        add(code)
    for item in recipe.variants.all():
        if getattr(item, "axis", None) != "addon" or not getattr(item, "has_delta", False):
            continue
        add(getattr(item, "protein_base_override", None))
    return ordered


def catalog_protein_variants(recipe) -> list[dict]:
    rows: list[dict] = []
    for item in recipe.variants.all():
        if getattr(item, "axis", None) != "addon" or not getattr(item, "has_delta", False):
            continue
        override = getattr(item, "protein_base_override", None)
        if not override:
            continue
        rows.append(
            {"code": item.code, "title": item.title, "protein_base": override}
        )
    return rows
```

---

## 26. `backend/apps/recipes/services/notes.py`

- Путь: `v2/backend/apps/recipes/services/notes.py`
- Классы и функции: split_notes_blob, normalize_notes
- Строк: 36

```python
"""Split V1 notes blob into the JSON list DATA-MODEL expects."""

from __future__ import annotations


def split_notes_blob(blob: str | None) -> list[dict]:
    """NULL → []; no blank line → one item; else split on \\n\\n. Titles stay null."""
    if blob is None:
        return []
    text = str(blob).strip()
    if not text:
        return []
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    return [{"title": None, "text": part} for part in parts]


def normalize_notes(value) -> list[dict]:
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict) and (item.get("text") or "").strip():
                title = item.get("title")
                out.append(
                    {
                        "title": title if isinstance(title, str) and title.strip() else None,
                        "text": str(item["text"]).strip(),
                    }
                )
            elif isinstance(item, str) and item.strip():
                out.append({"title": None, "text": item.strip()})
        return out
    if isinstance(value, str):
        return split_notes_blob(value)
    return []
```

---

## 27. `backend/apps/recipes/services/nutrition.py`

- Путь: `v2/backend/apps/recipes/services/nutrition.py`
- Классы и функции: line_skipped, nutrition_skip_hint, has_full_macros, grams_per_unit, line_nutrition_factor, nutrition_line_projection, compute_recipe_nutrition, enrich_lines_from_db
- Строк: 241

```python
"""Recipe nutrition after assemble + apply_mode. kcal from the canon, never Atwater."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from apps.recipes.services.scale import apply_mode

SKIP_UNITS = frozenset({"to_taste", "pinch"})
MACRO_KEYS = (
    "kcal_per_100g",
    "protein_g_per_100g",
    "fat_g_per_100g",
    "carbs_g_per_100g",
)
CANON_NUTRITION_FIELDS = (
    *MACRO_KEYS,
    "density_g_per_ml",
    "g_per_tsp",
    "g_per_tbsp",
    "g_per_pcs",
    "g_per_clove",
    "g_per_bunch",
    "g_per_slice",
)
UNIT_MASS_FIELD = {
    "tsp": "g_per_tsp",
    "tbsp": "g_per_tbsp",
    "pcs": "g_per_pcs",
    "clove": "g_per_clove",
    "bunch": "g_per_bunch",
    "slice": "g_per_slice",
}
KCAL_QUANT = Decimal("1")
MACRO_QUANT = Decimal("0.1")


def _d(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _json_num(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _round_kcal(value: Decimal) -> int:
    return int(value.quantize(KCAL_QUANT, rounding=ROUND_HALF_UP))


def _round_macro(value: Decimal) -> float:
    return float(value.quantize(MACRO_QUANT, rounding=ROUND_HALF_UP))


def _macros_payload(kcal: Decimal, protein: Decimal, fat: Decimal, carbs: Decimal) -> dict:
    return {
        "kcal": _round_kcal(kcal),
        "protein_g": _round_macro(protein),
        "fat_g": _round_macro(fat),
        "carbs_g": _round_macro(carbs),
    }


def line_skipped(line: dict) -> bool:
    if line.get("optional"):
        return True
    if line.get("unit") in SKIP_UNITS:
        return True
    if line.get("nutrition_exclude"):
        return True
    return False


def nutrition_skip_hint(line: dict) -> bool:
    """Icon when to_taste/pinch hid concentrated kcal. Salt and spices stay quiet."""
    if line.get("unit") not in SKIP_UNITS:
        return False
    kcal = _d(line.get("kcal_per_100g"))
    if kcal is None or kcal <= 0:
        return False
    fat = _d(line.get("fat_g_per_100g")) or Decimal("0")
    return kcal >= 300 or fat >= 20


def has_full_macros(line: dict) -> bool:
    return all(_d(line.get(key)) is not None for key in MACRO_KEYS)


def grams_per_unit(line: dict) -> Decimal | None:
    unit = line.get("unit")
    if unit == "g":
        return Decimal("1")
    if unit == "kg":
        return Decimal("1000")
    if unit == "ml":
        density = _d(line.get("density_g_per_ml"))
        return density
    if unit == "l":
        density = _d(line.get("density_g_per_ml"))
        if density is None:
            return None
        return density * Decimal("1000")
    field = UNIT_MASS_FIELD.get(unit or "")
    if field:
        return _d(line.get(field))
    return None


def line_nutrition_factor(line: dict) -> Decimal:
    raw = _d(line.get("nutrition_factor"))
    if raw is None:
        return Decimal("1")
    return raw


def nutrition_line_projection(line: dict) -> dict | None:
    """Per-row payload for the recipe card. Null if the line is out of the sum."""
    if line_skipped(line) or not has_full_macros(line):
        return None
    unit_grams = grams_per_unit(line)
    if unit_grams is None:
        return None
    factor = line_nutrition_factor(line)
    return {
        "kcal_per_100g": _json_num(_d(line["kcal_per_100g"])),
        "protein_g_per_100g": _json_num(_d(line["protein_g_per_100g"])),
        "fat_g_per_100g": _json_num(_d(line["fat_g_per_100g"])),
        "carbs_g_per_100g": _json_num(_d(line["carbs_g_per_100g"])),
        "grams_per_unit": _json_num(unit_grams),
        "nutrition_factor": _json_num(factor),
    }


def compute_recipe_nutrition(
    lines: list[dict],
    *,
    servings: int | None,
    ratio: Decimal,
    scaling_enabled: bool,
    yield_weight_g: Decimal | None = None,
) -> dict:
    incomplete = False
    total_kcal = Decimal("0")
    total_protein = Decimal("0")
    total_fat = Decimal("0")
    total_carbs = Decimal("0")
    mass_g = Decimal("0")
    scale_ratio = ratio if isinstance(ratio, Decimal) else Decimal(str(ratio))

    for line in lines:
        if line_skipped(line):
            continue
        amount = _d(line.get("amount"))
        unit_grams = grams_per_unit(line)
        if amount is None or unit_grams is None or not has_full_macros(line):
            incomplete = True
            continue
        if scaling_enabled:
            amount = apply_mode(
                amount,
                scale_ratio,
                line.get("scale_mode") or "linear",
                bool(line.get("scalable", True)),
            )
        grams = amount * unit_grams * line_nutrition_factor(line)
        mass_g += grams
        contrib = grams / Decimal("100")
        total_kcal += _d(line["kcal_per_100g"]) * contrib
        total_protein += _d(line["protein_g_per_100g"]) * contrib
        total_fat += _d(line["fat_g_per_100g"]) * contrib
        total_carbs += _d(line["carbs_g_per_100g"]) * contrib

    total = _macros_payload(total_kcal, total_protein, total_fat, total_carbs)
    if mass_g > 0:
        hundred = Decimal("100") / mass_g
        per_100g_input = _macros_payload(
            total_kcal * hundred,
            total_protein * hundred,
            total_fat * hundred,
            total_carbs * hundred,
        )
    else:
        per_100g_input = None

    per_serving = None
    if isinstance(servings, int) and not isinstance(servings, bool) and servings >= 1:
        denom = Decimal(servings)
        per_serving = _macros_payload(
            total_kcal / denom,
            total_protein / denom,
            total_fat / denom,
            total_carbs / denom,
        )

    per_100g_cooked = None
    base_yield = _d(yield_weight_g)
    if base_yield is not None and base_yield > 0:
        cooked_mass = base_yield * (scale_ratio if scaling_enabled else Decimal("1"))
        if cooked_mass > 0:
            hundred = Decimal("100") / cooked_mass
            per_100g_cooked = _macros_payload(
                total_kcal * hundred,
                total_protein * hundred,
                total_fat * hundred,
                total_carbs * hundred,
            )

    return {
        "basis": "raw_input",
        "incomplete": incomplete,
        "total": total,
        "per_100g_input": per_100g_input,
        "per_100g_cooked": per_100g_cooked,
        "per_serving": per_serving,
    }


def enrich_lines_from_db(lines: list[dict]) -> list[dict]:
    """Fill canon nutrient / unit-mass fields after variant add/replace."""
    ids = {line.get("canonical_id") for line in lines if line.get("canonical_id")}
    if not ids:
        return lines
    from apps.recipes.models import Ingredient

    found = {
        ing.canonical_id: ing
        for ing in Ingredient.objects.filter(canonical_id__in=ids)
    }
    for line in lines:
        ing = found.get(line.get("canonical_id"))
        if ing is None:
            continue
        for field in CANON_NUTRITION_FIELDS:
            line[field] = getattr(ing, field)
    return lines
```

---

## 28. `backend/apps/recipes/services/pantry.py`

- Путь: `v2/backend/apps/recipes/services/pantry.py`
- Классы и функции: norm_ru, split_pantry_text, expand_have_group, pantry_universe, resolve_token, resolve_pantry_text
- Строк: 92

```python
"""Resolve pantry text and coarse groups. No runtime LLM."""

from __future__ import annotations

from apps.recipes.pantry_vocab import (
    CANONICAL_INGREDIENT_LABEL_RU,
    HAVE_GROUPS,
    HAVE_TEXT_ALIASES,
    shopping_ids,
)


def norm_ru(text: str) -> str:
    return (text or "").strip().lower().replace("ё", "е")


def split_pantry_text(text: str) -> list[str]:
    raw = (text or "").replace(";", ",")
    return [part.strip() for part in raw.split(",") if part.strip()]


def expand_have_group(code: str) -> list[str]:
    return list(HAVE_GROUPS.get(code, ()))


def pantry_universe(known: set[str] | None = None, titles: dict[str, str] | None = None):
    ids = shopping_ids() | (known or set())
    labels = {**CANONICAL_INGREDIENT_LABEL_RU, **(titles or {})}
    return ids, labels


def resolve_token(token: str, *, titles: dict[str, str], known: set[str]) -> list[str]:
    """Return canonical_ids. Empty = unknown. Ambiguous words like «масло» stay unknown."""
    raw = token.strip()
    if not raw:
        return []
    universe, labels = pantry_universe(known, titles)
    if raw in universe:
        return [raw]
    key = norm_ru(raw)
    alias = HAVE_TEXT_ALIASES.get(key)
    if alias:
        if alias in HAVE_GROUPS:
            return list(HAVE_GROUPS[alias])
        if alias in universe:
            return [alias]
    for cid, title in labels.items():
        if norm_ru(title) == key:
            return [cid]
    return []


def resolve_pantry_text(text: str, *, titles: dict[str, str], known: set[str]) -> tuple[list[str], list[str]]:
    found: list[str] = []
    unknown: list[str] = []
    seen: set[str] = set()

    def add_ids(ids: list[str]) -> None:
        for cid in ids:
            if cid not in seen:
                seen.add(cid)
                found.append(cid)

    for phrase in split_pantry_text(text):
        ids = resolve_token(phrase, titles=titles, known=known)
        if ids:
            add_ids(ids)
            continue
        words = [word.strip(" .") for word in phrase.split() if word.strip(" .")]
        if len(words) <= 1:
            unknown.append(phrase)
            continue
        i = 0
        leftover: list[str] = []
        while i < len(words):
            matched: list[str] | None = None
            taken = 1
            for length in range(len(words) - i, 0, -1):
                chunk = " ".join(words[i : i + length])
                chunk_ids = resolve_token(chunk, titles=titles, known=known)
                if chunk_ids:
                    matched = chunk_ids
                    taken = length
                    break
            if matched:
                add_ids(matched)
                i += taken
            else:
                leftover.append(words[i])
                i += 1
        unknown.extend(leftover)
    return found, unknown
```

---

## 29. `backend/apps/recipes/services/ranking.py`

- Путь: `v2/backend/apps/recipes/services/ranking.py`
- Классы и функции: score_and_why
- Строк: 45

```python
"""Ranking v0 — DEFAULTS weights. Hard filters drop, they do not score."""

from __future__ import annotations

from django.conf import settings

from apps.recipes.constants import PROTEIN_BASE_LABEL_RU, label_equipment_axis


def score_and_why(
    *,
    protein_base: str,
    cook_method: str,
    dish_type: str,
    equipment: str | None,
    editorial_tested: bool,
    filter_protein: list[str],
    filter_method: list[str],
    filter_dish: list[str],
    filter_equipment: list[str],
    protein_bases: list[str] | None = None,
) -> tuple[int, list[str]]:
    weights = settings.RANKING_WEIGHTS
    score = 0
    why: list[str] = []
    candidates = protein_bases or [protein_base]
    matched_protein = next((code for code in filter_protein if code in candidates), None)
    if filter_protein and matched_protein:
        score += int(weights["protein_base"])
        label = PROTEIN_BASE_LABEL_RU.get(matched_protein, matched_protein)
        why.append(f"основа — {label}")
    if filter_method and cook_method in filter_method:
        score += int(weights["cook_method"])
        why.append("совпал метод")
    if filter_dish and dish_type in filter_dish:
        score += int(weights["dish_type"])
        why.append("совпал тип блюда")
    if filter_equipment and equipment in filter_equipment:
        score += int(weights.get("equipment", weights["dish_type"]))
        label = label_equipment_axis(equipment)
        why.append(f"совпала посуда — {label}")
    if editorial_tested:
        score += int(weights["editorial_tested"])
        why.append("проверено редакцией")
    return score, why
```

---

## 30. `backend/apps/recipes/services/scale.py`

- Путь: `v2/backend/apps/recipes/services/scale.py`
- Классы и функции: ScaleConflict, ScaleResult, round_scaled, apply_mode, format_display_amount, base_anchor_amount, resolve_scale, scale_line
- Строк: 216

```python
"""Scaling domain service. Next.js does not compute ratio ** 0.7."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from apps.recipes.constants import UNIT_LABEL_RU

GENTLE_EXPONENT = Decimal("0.7")
# V1 used 1+(ratio-1)*0.5 — never use that here.


class ScaleConflict(Exception):
    """Both servings and anchor_weight were provided — API 400."""


@dataclass(frozen=True)
class ScaleResult:
    enabled: bool
    mode: str  # anchor | servings | off
    ratio: Decimal
    base_anchor: dict[str, Any] | None
    applied: dict[str, Any] | None


def _d(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _quantize(value: Decimal, quant: Decimal) -> Decimal:
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def round_scaled(amount: Decimal, unit: str, *, whole: bool = False) -> Decimal:
    """UI rounding from DEFAULTS (port of V1 roundScaled, not the gentle formula)."""
    if whole:
        rounded = _quantize(amount, Decimal("1"))
        return max(Decimal("1"), rounded)

    if unit in {"g", "ml"}:
        if amount >= 200:
            return _quantize(amount / Decimal("10"), Decimal("1")) * Decimal("10")
        if amount >= 50:
            return _quantize(amount / Decimal("5"), Decimal("1")) * Decimal("5")
        return _quantize(amount, Decimal("1"))

    if unit in {"kg", "l"}:
        return _quantize(amount, Decimal("0.01"))

    if unit in {"pcs", "clove", "bunch", "slice"}:
        half = _quantize(amount * 2, Decimal("1")) / Decimal("2")
        return max(Decimal("0.5"), half)

    if unit in {"tsp", "tbsp"}:
        return _quantize(amount * 4, Decimal("1")) / Decimal("4")

    return _quantize(amount, Decimal("0.1"))


def apply_mode(amount: Decimal, ratio: Decimal, scale_mode: str, scalable: bool) -> Decimal:
    if not scalable:
        return amount
    if scale_mode == "manual":
        return amount
    if scale_mode == "gentle":
        return amount * (ratio ** GENTLE_EXPONENT)
    return amount * ratio


SPOON_ML = {"tsp": Decimal("5"), "tbsp": Decimal("15")}


def _spoon_ml(amount: Decimal, unit: str) -> str:
    ml = (amount * SPOON_ML[unit]).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return _format_number(ml)


def format_display_amount(
    amount: Decimal | None, unit: str, amount_max: Decimal | None = None
) -> str:
    label = UNIT_LABEL_RU.get(unit, unit)
    if unit in {"to_taste", "pinch"} or amount is None:
        return label
    text = _format_number(amount)
    if amount_max is not None:
        text = f"{text}–{_format_number(amount_max)}"
    shown = f"{text} {label}"
    if unit in SPOON_ML:
        hint = _spoon_ml(amount, unit)
        if amount_max is not None:
            hint = f"{hint}–{_spoon_ml(amount_max, unit)}"
        shown = f"{shown} (~{hint} мл)"
    return shown


def _format_number(value: Decimal) -> str:
    normalized = value
    if normalized == normalized.to_integral_value():
        return str(int(normalized))
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", ",")


def base_anchor_amount(amount: Decimal, unit: str) -> tuple[Decimal, str] | None:
    """Convert kg/l to g/ml for ratio. Returns (amount, base_unit)."""
    if unit == "kg":
        return amount * Decimal("1000"), "g"
    if unit == "l":
        return amount * Decimal("1000"), "ml"
    if unit in {"g", "ml"}:
        return amount, unit
    return None


def _json_number(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def resolve_scale(
    *,
    recipe_scalable: bool,
    recipe_servings: int | None,
    anchor_amount: Decimal | None,
    anchor_unit: str | None,
    servings: Decimal | None,
    anchor_weight: Decimal | None,
    anchor_name: str | None = None,
) -> ScaleResult:
    """Compute ratio from servings XOR anchor_weight.

    No servings and no anchor on the recipe → scaling off; do not invent 4 portions.
    recipe.scalable=false → ignore query, enabled=false.
    """
    if servings is not None and anchor_weight is not None:
        raise ScaleConflict("Нельзя передавать servings и anchor_weight одновременно.")

    off = ScaleResult(
        enabled=False, mode="off", ratio=Decimal("1"), base_anchor=None, applied=None
    )

    if not recipe_scalable:
        return off

    base = None
    if anchor_amount is not None and anchor_unit:
        converted = base_anchor_amount(anchor_amount, anchor_unit)
        if converted:
            base_val, base_unit = converted
            base = {
                "amount": _json_number(base_val),
                "unit": base_unit,
                "name": anchor_name or "",
            }

    has_servings_base = recipe_servings is not None and recipe_servings > 0
    has_anchor_base = base is not None

    if servings is None and anchor_weight is None:
        return off

    if servings is not None:
        if not has_servings_base:
            return off
        ratio = _d(servings) / Decimal(recipe_servings)
        return ScaleResult(
            enabled=True,
            mode="servings",
            ratio=ratio,
            base_anchor=base,
            applied={"servings": _json_number(_d(servings))},
        )

    if not has_anchor_base:
        return off
    ratio = _d(anchor_weight) / _d(base["amount"])
    return ScaleResult(
        enabled=True,
        mode="anchor",
        ratio=ratio,
        base_anchor=base,
        applied={"anchor_weight": _json_number(_d(anchor_weight))},
    )


def scale_line(
    *,
    amount: Decimal | None,
    amount_max: Decimal | None,
    unit: str,
    scale_mode: str,
    scalable: bool,
    ratio: Decimal,
    scaling_enabled: bool,
) -> tuple[Decimal | None, Decimal | None]:
    """Return scaled (and rounded) amount / amount_max. Timers/temps are never scaled."""
    if amount is None:
        return None, None
    if not scaling_enabled:
        return amount, amount_max

    whole = scale_mode == "whole" and scalable
    raw = apply_mode(amount, ratio, scale_mode, scalable)
    out = round_scaled(raw, unit, whole=whole)
    out_max = None
    if amount_max is not None:
        raw_max = apply_mode(amount_max, ratio, scale_mode, scalable)
        out_max = round_scaled(raw_max, unit, whole=whole)
    return out, out_max
```

---

## 31. `backend/apps/recipes/services/search.py`

- Путь: `v2/backend/apps/recipes/services/search.py`
- Классы и функции: PgNormalizeRu, Similarity, apply_catalog_search
- Строк: 35

```python
"""Catalog FTS: russian config + normalize_ru. Do not use icontains lookups."""

from __future__ import annotations

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, FloatField, Func, Q, TextField, Value

from apps.recipes.services.allergens import normalize_ru


class PgNormalizeRu(Func):
    function = "normalize_ru"
    output_field = TextField()
    arity = 1


class Similarity(Func):
    function = "similarity"
    output_field = FloatField()
    arity = 2


def apply_catalog_search(queryset, raw_q: str):
    qn = normalize_ru(raw_q).strip()
    if not qn:
        return queryset
    query = SearchQuery(qn, config="russian", search_type="plain")
    return (
        queryset.annotate(
            search_rank=SearchRank(F("search_vector"), query),
            title_trgm=Similarity(PgNormalizeRu(F("title")), Value(qn)),
        )
        .filter(Q(search_vector=query) | Q(title_trgm__gt=0.2))
        .order_by("-search_rank", "-title_trgm", "title")
    )
```

---

## 32. `backend/apps/recipes/services/snapshots.py`

- Путь: `v2/backend/apps/recipes/services/snapshots.py`
- Классы и функции: snapshot_from_assembled, snapshot_fits, refresh_axis_snapshots
- Строк: 78

```python
"""Precomputed axis snapshots so the calculator can rank without assemble."""

from __future__ import annotations

from typing import Any

LINE_KEYS = ("canonical_id", "name", "optional", "unit", "is_anchor")


def _line_stub(line: dict) -> dict[str, Any]:
    return {key: line.get(key) for key in LINE_KEYS}


def snapshot_from_assembled(recipe, assembled, addon, equipment_variant) -> dict[str, Any]:
    from apps.recipes.services.solve import combo_protein_bases, combo_time_minutes

    time_total, time_active = combo_time_minutes(recipe)
    variant_code = addon.code if addon is not None else None
    return {
        "variant": variant_code,
        "equipment": assembled.equipment,
        "home": addon is None and equipment_variant is None,
        "protein_base": assembled.protein_base,
        "protein_bases": combo_protein_bases(recipe, addon),
        "cook_method": assembled.cook_method,
        "lines": [_line_stub(line) for line in assembled.ingredients],
        "allergens": dict(assembled.allergens or {}),
        "high_risk_flags": list(assembled.high_risk_flags or []),
        "step_count": len(assembled.steps),
        "time_total_minutes": time_total,
        "time_active_minutes": time_active,
        "addon_penalty": 0 if addon is None else 1,
        "equipment_penalty": 0 if equipment_variant is None else 1,
    }


def snapshot_fits(
    snap: dict,
    methods: list[str],
    equipments: list[str],
    proteins: list[str] | None = None,
) -> bool:
    if methods and snap.get("cook_method") not in methods:
        return False
    if equipments and snap.get("equipment") not in equipments:
        return False
    if proteins:
        bases = list(snap.get("protein_bases") or [])
        if not any(code in proteins for code in bases):
            return False
    return True


def refresh_axis_snapshots(recipe) -> list[dict[str, Any]]:
    """Assemble every delta combo once and store stubs on the recipe row."""
    from apps.recipes.models import Recipe
    from apps.recipes.services.assemble import VariantError, assemble_recipe
    from apps.recipes.services.solve import axis_combos

    out: list[dict[str, Any]] = []
    for addon, equipment_variant in axis_combos(recipe, explore=True):
        variant_code = addon.code if addon is not None else None
        equipment_code = None
        if equipment_variant is not None:
            equipment_code = equipment_variant.equipment or equipment_variant.code
        try:
            assembled = assemble_recipe(
                recipe,
                variant_code=variant_code,
                equipment_code=equipment_code,
                enrich=False,
            )
        except VariantError:
            continue
        out.append(snapshot_from_assembled(recipe, assembled, addon, equipment_variant))
    Recipe.objects.filter(pk=recipe.pk).update(axis_snapshots=out)
    recipe.axis_snapshots = out
    return out
```

---

## 33. `backend/apps/recipes/services/solve.py`

- Путь: `v2/backend/apps/recipes/services/solve.py`
- Классы и функции: CookingSolution, is_core_line, is_desirable_line, combo_method_equipment, combo_time_minutes, intent_adjust, combo_protein_bases, combo_fits, axis_combos, match_pantry, pantry_score, pantry_why, protein_from_pantry, axes_why, solve_recipe, is_standalone_dish, assign_buckets, build_board, serialize_solution
- Строк: 701

```python
"""CookingSolution: pick axes, apply pantry/substitutions, rank, bucket."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

from django.conf import settings

from apps.recipes.constants import (
    BEST_BUCKET_LIMIT,
    COMPONENT_DISH_TYPES,
    COOK_METHOD_LABEL_RU,
    PROTEIN_BASE_LABEL_RU,
    label_equipment_axis,
)
from apps.recipes.pantry_vocab import (
    FISH_CANNED,
    FISH_FRESH,
    FISH_PROTEIN,
    HAVE_GROUP_PROTEIN,
    HAVE_GROUPS,
    availability_class,
    shopping_label,
)
from apps.recipes.services.assemble import VariantError, assemble_recipe
from apps.recipes.services.ranking import score_and_why
from apps.recipes.services.snapshots import snapshot_fits
from apps.recipes.services.substitutions import SubRule, cover_need, rules_for_recipe


@dataclass
class CookingSolution:
    slug: str
    title: str
    protein_base: str
    cook_method: str
    dish_type: str
    equipment: str | None
    applied_axes: dict[str, str | None]
    bucket: str
    why: list[str]
    score: int
    shopping_delta: list[dict]
    substitutions: list[dict]
    allergens: dict
    high_risk_flags: list[str]
    has_delta_variants: bool
    allowed_cuts: list[str] = field(default_factory=list)
    pantry_hits: int = 0
    step_count: int = 0
    have_used: int = 0
    have_all: bool = False
    protein_bases: list[str] = field(default_factory=list)
    protein_variants: list[dict] = field(default_factory=list)
    time_total_minutes: int | None = None
    time_active_minutes: int | None = None


def is_core_line(line: dict) -> bool:
    if line.get("optional"):
        return False
    cid = (line.get("canonical_id") or "").strip()
    if not cid:
        return False
    klass = availability_class(cid)
    if klass in {"assumed", "common", "exotic"}:
        return False
    if line.get("is_anchor"):
        return True
    if line.get("unit") in {"pinch", "tsp"}:
        return False
    return True


def is_desirable_line(line: dict) -> bool:
    if line.get("optional"):
        return False
    cid = (line.get("canonical_id") or "").strip()
    if not cid:
        return False
    return availability_class(cid) == "common"


def combo_method_equipment(recipe, addon, equipment_variant) -> tuple[str, str | None]:
    method = recipe.cook_method
    equipment = recipe.equipment
    if equipment_variant is not None:
        if equipment_variant.cook_method_override:
            method = equipment_variant.cook_method_override
        equipment = equipment_variant.equipment or equipment_variant.code
    return method, equipment


def combo_time_minutes(recipe) -> tuple[int | None, int | None]:
    total = getattr(recipe, "time_total_minutes", None)
    active = getattr(recipe, "time_active_minutes", None)
    return (
        int(total) if total is not None else None,
        int(active) if active is not None else None,
    )


def intent_adjust(
    recipe,
    assembled,
    intents: list[str],
    step_count: int,
    *,
    time_total_minutes: int | None = None,
) -> tuple[int, list[str]]:
    if not intents:
        return 0, []
    score = 0
    why: list[str] = []
    method = assembled.cook_method
    if "fast" in intents:
        if method in {"pan_fry", "no_cook", "grill"}:
            score += 8
            why.append("быстрее на плите")
        elif method in {"stew", "oven"}:
            score -= 3
        score -= min(step_count, 6)
        if time_total_minutes is not None:
            score -= min(int(time_total_minutes) // 15, 6)
            if time_total_minutes <= 30:
                why.append("быстрее по времени")
    if "oven" in intents:
        if method == "oven":
            score += 10
            why.append("духовка")
    if "light" in intents and getattr(recipe, "energy_profile", "standard") == "light":
        score += 8
        why.append("полегче по составу")
    if "easy" in intents:
        score -= min(step_count, 8)
        if method in {"oven", "stew", "no_cook"}:
            score += 4
            why.append("меньше стоять у плиты")
    if "batch" in intents and method in {"stew", "oven"}:
        score += 8
        why.append("можно на несколько дней")
    return score, why


def combo_protein_bases(recipe, addon) -> list[str]:
    override = getattr(addon, "protein_base_override", None) if addon is not None else None
    if override:
        return [override]
    ordered: list[str] = []
    home = getattr(recipe, "protein_base", None)
    if home:
        ordered.append(home)
    for code in getattr(recipe, "protein_bases_extra", None) or []:
        if code and code not in ordered:
            ordered.append(code)
    return ordered


def combo_fits(
    recipe,
    addon,
    equipment_variant,
    methods: list[str],
    equipments: list[str],
    proteins: list[str] | None = None,
) -> bool:
    method, equipment = combo_method_equipment(recipe, addon, equipment_variant)
    if methods and method not in methods:
        return False
    if equipments and equipment not in equipments:
        return False
    if proteins:
        bases = combo_protein_bases(recipe, addon)
        if not any(code in proteins for code in bases):
            return False
    return True


def axis_combos(recipe, *, explore: bool) -> list[tuple[object | None, object | None]]:
    variants = list(recipe.variants.all())
    if not explore:
        return [(None, None)]
    addons: list[object | None] = [None]
    addons.extend(item for item in variants if item.axis == "addon" and item.has_delta)
    equipments: list[object | None] = [None]
    equipments.extend(item for item in variants if item.axis == "equipment" and item.has_delta)
    return [(addon, eq) for addon in addons for eq in equipments]


def match_pantry(
    lines: list[dict],
    have: list[str],
    rules: list[SubRule],
    titles: dict[str, str] | None = None,
) -> tuple[list[dict], list[dict], int, int, list[dict], set[str], set[str]]:
    """Return shopping, substitutions, hits, missing, desirable, covered needs, used have ids."""
    have_set = set(have)
    titles = titles or {}
    shopping: list[dict] = []
    substitutions: list[dict] = []
    desirable: list[dict] = []
    covered_ids: set[str] = set()
    used_have: set[str] = set()
    hits = 0
    for line in lines:
        need = (line.get("canonical_id") or "").strip()
        title = line.get("name") or shopping_label(need, titles)
        if not need:
            continue
        if is_desirable_line(line):
            if need not in have_set:
                desirable.append({"canonical_id": need, "title": title})
            continue
        if not is_core_line(line):
            continue
        covered, quality = cover_need(need, have_set, rules)
        if covered is None:
            shopping.append({"canonical_id": need, "title": title})
            continue
        hits += 1
        covered_ids.add(need)
        if need in have_set:
            used_have.add(need)
        if covered in have_set:
            used_have.add(covered)
        if covered != need and quality is not None:
            to_title = shopping_label(covered, titles)
            substitutions.append(
                {
                    "from_id": need,
                    "from_title": title,
                    "to_id": covered,
                    "to_title": to_title,
                    "quality": quality,
                }
            )
    return shopping, substitutions, hits, len(shopping), desirable, covered_ids, used_have


def pantry_score(hits: int, missing: int, substitutions: list[dict], *, has_have: bool) -> int:
    if not has_have:
        return 0
    weights = settings.RANKING_WEIGHTS
    score = hits * int(weights["pantry_hit"])
    score += missing * int(weights["pantry_missing"])
    score += len(substitutions) * int(weights["substitution_friction"])
    if missing == 0:
        score += int(weights["pantry_complete"])
    return score


def pantry_why(
    shopping: list[dict],
    substitutions: list[dict],
    *,
    has_have: bool,
    desirable: list[dict] | None = None,
) -> list[str]:
    if not has_have:
        return []
    why: list[str] = []
    if not shopping:
        if substitutions:
            why.append("можно приготовить с заменой")
        else:
            why.append("можно приготовить сейчас")
    elif len(shopping) == 1:
        why.append(f"нужно докупить: {shopping[0]['title']}")
    else:
        names = ", ".join(item["title"] for item in shopping[:3])
        extra = f" и ещё {len(shopping) - 3}" if len(shopping) > 3 else ""
        why.append(f"нужно докупить: {names}{extra}")
    for item in substitutions:
        why.append(f"вместо {item['from_title']} — {item['to_title']}")
    if desirable:
        names = ", ".join(item["title"] for item in desirable[:3])
        why.append(f"желательно: {names}, но можно без этого")
    return why


def protein_from_pantry(
    recipe,
    have: list[str],
    *,
    covered_ids: set[str],
    titles: dict[str, str] | None = None,
    protein_base: str | None = None,
) -> tuple[int, list[str]]:
    """Bonus only if a core line from `have` actually covers this recipe.

    Ground beef in the cupboard is not a steak, a chuck roast, or butter.
    """
    if not have or not covered_ids:
        return 0, []
    score = 0
    why: list[str] = []
    titles = titles or {}
    covered = set(covered_ids)
    fresh = bool(covered & FISH_FRESH)
    canned = bool(covered & FISH_CANNED)
    base = protein_base or recipe.protein_base
    if fresh and base in FISH_PROTEIN:
        score += 8
        why.append("есть рыба")
    elif canned and not fresh and base in FISH_PROTEIN:
        score += 3
        why.append("есть рыбные консервы")
    preference = (
        "chicken",
        "pork",
        "beef",
        "lamb",
        "eggs",
        "veg",
        "legumes",
        "meat",
    )
    for group in preference:
        bases = HAVE_GROUP_PROTEIN.get(group)
        if not bases:
            continue
        matched = covered & set(HAVE_GROUPS[group])
        if matched and base in bases:
            score += 6
            label = shopping_label(sorted(matched)[0], titles)
            why.append(f"есть {label}")
            break
    return score, why


def axes_why(
    recipe, assembled, methods: list[str], equipments: list[str], proteins: list[str] | None = None
) -> list[str]:
    extra: list[str] = []
    proteins = proteins or []
    if (
        proteins
        and assembled.protein_base in proteins
        and assembled.protein_base != recipe.protein_base
    ):
        label = PROTEIN_BASE_LABEL_RU.get(assembled.protein_base, assembled.protein_base)
        extra.append(f"{label} — вариант")
    if methods and assembled.cook_method in methods and assembled.cook_method != recipe.cook_method:
        label = COOK_METHOD_LABEL_RU.get(assembled.cook_method, assembled.cook_method)
        extra.append(f"{label} — вариант посуды")
    if (
        equipments
        and assembled.equipment in equipments
        and assembled.equipment
        and assembled.equipment != recipe.equipment
    ):
        extra.append(f"посуда — {label_equipment_axis(assembled.equipment)} (вариант)")
    return extra


def _combo_key(addon, equipment_variant) -> tuple[int, int]:
    """Prefer base (no addon, no equipment variant) on ties."""
    return (0 if addon is None else 1, 0 if equipment_variant is None else 1)


def solve_recipe(
    recipe,
    *,
    filter_protein: list[str],
    filter_method: list[str],
    filter_dish: list[str],
    filter_equipment: list[str],
    have: list[str],
    catalog_item: dict,
    rules: list[SubRule],
    titles: dict[str, str] | None = None,
    intents: list[str] | None = None,
    explicit_have: list[str] | None = None,
) -> CookingSolution | None:
    intents = intents or []
    explicit = [cid for cid in (explicit_have or []) if cid]
    explicit_set = set(explicit)
    explore = bool(have or filter_method or filter_equipment or filter_protein or intents)
    best: CookingSolution | None = None
    best_key: tuple | None = None
    recipe_rules = rules_for_recipe(recipe.slug, rules)
    titles = titles or {}

    scored: list[tuple[tuple, object, object]] = []
    snaps = list(getattr(recipe, "axis_snapshots", None) or [])
    if snaps:
        for snap in snaps:
            if not explore and not snap.get("home"):
                continue
            if not snapshot_fits(snap, filter_method, filter_equipment, filter_protein):
                continue
            assembled = SimpleNamespace(
                ingredients=list(snap.get("lines") or []),
                allergens=snap.get("allergens") or {},
                high_risk_flags=list(snap.get("high_risk_flags") or []),
                cook_method=snap.get("cook_method") or recipe.cook_method,
                protein_base=snap.get("protein_base") or recipe.protein_base,
                equipment=snap.get("equipment"),
                applied_axes={
                    "variant": snap.get("variant"),
                    "equipment": snap.get("equipment"),
                },
            )
            protein_bases = list(snap.get("protein_bases") or [assembled.protein_base])
            combo_key = (
                int(snap.get("addon_penalty") or 0),
                int(snap.get("equipment_penalty") or 0),
            )
            step_count = int(snap.get("step_count") or 0)
            time_total = snap.get("time_total_minutes")
            time_active = snap.get("time_active_minutes")
            scored.append(
                (assembled, protein_bases, combo_key, step_count, time_total, time_active)
            )
    else:
        for addon, equipment_variant in axis_combos(recipe, explore=explore):
            if not combo_fits(
                recipe, addon, equipment_variant, filter_method, filter_equipment, filter_protein
            ):
                continue
            variant_code = addon.code if addon is not None else None
            equipment_code = None
            if equipment_variant is not None:
                equipment_code = equipment_variant.equipment or equipment_variant.code
            elif filter_equipment and recipe.equipment in filter_equipment:
                equipment_code = recipe.equipment
            try:
                assembled = assemble_recipe(
                    recipe,
                    variant_code=variant_code,
                    equipment_code=equipment_code,
                    enrich=False,
                )
            except VariantError:
                continue
            protein_bases = combo_protein_bases(recipe, addon)
            combo_key = _combo_key(addon, equipment_variant)
            time_total, time_active = combo_time_minutes(recipe)
            scored.append(
                (
                    assembled,
                    protein_bases,
                    combo_key,
                    len(assembled.steps),
                    time_total,
                    time_active,
                )
            )

    for assembled, protein_bases, combo_key, step_count, time_total, time_active in scored:
        if have:
            (
                shopping,
                substitutions,
                hits,
                missing,
                desirable,
                covered_ids,
                used_have,
            ) = match_pantry(assembled.ingredients, have, recipe_rules, titles)
        else:
            shopping, substitutions, desirable = [], [], []
            hits = missing = 0
            covered_ids, used_have = set(), set()
        chip_score, chip_why = score_and_why(
            protein_base=assembled.protein_base,
            cook_method=assembled.cook_method,
            dish_type=recipe.dish_type,
            equipment=assembled.equipment,
            editorial_tested=recipe.editorial_tested,
            filter_protein=filter_protein,
            filter_method=filter_method,
            filter_dish=filter_dish,
            filter_equipment=filter_equipment,
            protein_bases=protein_bases,
        )
        why = list(chip_why)
        axis_lines = axes_why(
            recipe, assembled, filter_method, filter_equipment, filter_protein
        )
        if any(line.endswith(" — вариант") for line in axis_lines):
            why = [line for line in why if not line.startswith("основа — ")]
        if any("вариант посуды" in line for line in axis_lines):
            why = [line for line in why if line != "совпал метод"]
        if any(" (вариант)" in line for line in axis_lines):
            why = [line for line in why if not line.startswith("совпала посуда")]
        why.extend(axis_lines)
        why.extend(pantry_why(shopping, substitutions, has_have=bool(have), desirable=desirable))
        protein_pts, protein_why = protein_from_pantry(
            recipe,
            have,
            covered_ids=covered_ids,
            titles=titles,
            protein_base=assembled.protein_base,
        )
        why.extend(protein_why)
        intent_pts, intent_why = intent_adjust(
            recipe,
            assembled,
            intents,
            step_count,
            time_total_minutes=time_total,
        )
        why.extend(intent_why)
        if "pantry" in intents and have:
            if missing == 0:
                intent_pts += 12
                if substitutions:
                    why.append("из того, что есть, с заменой")
                else:
                    why.append("из того, что есть")
            else:
                intent_pts -= missing * 3
        have_used = len(used_have & explicit_set) if explicit_set else 0
        have_all = bool(explicit_set) and explicit_set <= used_have
        if have_all and len(explicit_set) >= 2:
            intent_pts += 16
            why.append("из всего выбранного")
        score = (
            chip_score
            + pantry_score(hits, missing, substitutions, has_have=bool(have))
            + intent_pts
            + protein_pts
        )
        solution = CookingSolution(
            slug=recipe.slug,
            title=recipe.title,
            protein_base=assembled.protein_base,
            cook_method=assembled.cook_method,
            dish_type=recipe.dish_type,
            equipment=assembled.equipment,
            applied_axes={
                "variant": assembled.applied_axes.get("variant"),
                "equipment": assembled.applied_axes.get("equipment"),
            },
            bucket="match",
            why=why,
            score=score,
            shopping_delta=shopping,
            substitutions=[
                {key: item[key] for key in ("from_id", "from_title", "to_id", "to_title")}
                for item in substitutions
            ],
            allergens=dict(assembled.allergens),
            high_risk_flags=list(assembled.high_risk_flags),
            has_delta_variants=bool(catalog_item["has_delta_variants"]),
            allowed_cuts=list(catalog_item.get("allowed_cuts") or []),
            pantry_hits=hits,
            step_count=step_count,
            have_used=have_used,
            have_all=have_all,
            protein_bases=list(catalog_item.get("protein_bases") or [recipe.protein_base]),
            protein_variants=list(catalog_item.get("protein_variants") or []),
            time_total_minutes=time_total,
            time_active_minutes=time_active,
        )
        key = (
            -int(have_all),
            -have_used,
            -score,
            missing,
            len(substitutions),
            *combo_key,
            recipe.title,
        )
        if best_key is None or key < best_key:
            best = solution
            best_key = key
    return best


def is_standalone_dish(dish_type: str) -> bool:
    return dish_type not in COMPONENT_DISH_TYPES


def _board_sort(item: CookingSolution) -> tuple:
    return (
        int(not is_standalone_dish(item.dish_type)),
        -int(item.have_all),
        -item.have_used,
        -item.pantry_hits,
        -item.score,
        item.title,
    )


def assign_buckets(solutions: list[CookingSolution], *, has_have: bool) -> dict[str, list[CookingSolution]]:
    if not has_have:
        for item in solutions:
            item.bucket = "match"
        return {"now": [], "almost": [], "best": []}

    now: list[CookingSolution] = []
    almost: list[CookingSolution] = []
    rest: list[CookingSolution] = []
    for item in solutions:
        missing = len(item.shopping_delta)
        hits = item.pantry_hits
        if hits <= 0:
            item.bucket = "rest"
            continue
        if missing == 0:
            item.bucket = "now"
            now.append(item)
        elif missing <= 2:
            item.bucket = "almost"
            almost.append(item)
        else:
            rest.append(item)
    now.sort(key=_board_sort)
    almost.sort(key=_board_sort)
    rest.sort(key=_board_sort)
    best = rest[:BEST_BUCKET_LIMIT]
    for item in best:
        item.bucket = "best"
    for item in rest[BEST_BUCKET_LIMIT:]:
        item.bucket = "rest"
    return {"now": now, "almost": almost, "best": best}


def build_board(
    solutions: list[CookingSolution],
    buckets: dict[str, list[CookingSolution]],
    *,
    has_have: bool,
) -> tuple[CookingSolution | None, list[tuple[str, CookingSolution]]]:
    if has_have:
        # Only dishes that use something from `have`. Unused pantry (steak
        # while you have mince, whipped butter, …) stays off the board.
        pool = buckets["now"] + buckets["almost"] + buckets["best"]
    else:
        pool = list(solutions)
    meals = [item for item in pool if is_standalone_dish(item.dish_type)]
    if meals:
        pool = meals
    if not has_have:
        pool = pool[:8]
    if not pool:
        return None, []
    complete = [item for item in pool if item.have_all]
    if complete:
        complete.sort(key=_board_sort)
        featured = complete[0]
    else:
        featured = pool[0]
    rest = [item for item in pool if item.slug != featured.slug]
    alts: list[tuple[str, CookingSolution]] = []

    def take(label: str, predicate) -> None:
        for index, item in enumerate(rest):
            if predicate(item):
                alts.append((label, item))
                rest.pop(index)
                return

    feat_time = featured.time_total_minutes
    take(
        "Быстрее",
        lambda item: feat_time is not None
        and item.time_total_minutes is not None
        and item.time_total_minutes < feat_time,
    )
    take(
        "На плите",
        lambda item: item.cook_method in {"pan_fry", "no_cook", "grill"},
    )
    take("В духовке", lambda item: item.cook_method == "oven")
    take("На несколько дней", lambda item: item.cook_method == "stew")
    while len(alts) < 3 and rest:
        alts.append(("Ещё вариант", rest.pop(0)))
    return featured, alts[:3]


def serialize_solution(item: CookingSolution) -> dict:
    return {
        "slug": item.slug,
        "title": item.title,
        "protein_base": item.protein_base,
        "protein_bases": item.protein_bases or [item.protein_base],
        "protein_variants": item.protein_variants,
        "cook_method": item.cook_method,
        "dish_type": item.dish_type,
        "equipment": item.equipment,
        "allowed_cuts": item.allowed_cuts,
        "applied_axes": item.applied_axes,
        "bucket": item.bucket,
        "why": item.why,
        "score": item.score,
        "shopping_delta": item.shopping_delta,
        "substitutions": item.substitutions,
        "allergens": item.allergens,
        "high_risk_flags": item.high_risk_flags,
        "has_delta_variants": item.has_delta_variants,
        "step_count": item.step_count,
        "time_profile": {
            "total_minutes": item.time_total_minutes,
            "active_minutes": item.time_active_minutes,
        },
    }
```

---

## 34. `backend/apps/recipes/services/substitutions.py`

- Путь: `v2/backend/apps/recipes/services/substitutions.py`
- Классы и функции: SubRule, load_seed_rows, upsert_substitution_rules, rules_for_recipe, stored_rules_from_db, cover_need
- Строк: 104

```python
"""Load and match substitution rules. Runtime LLM is forbidden."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from apps.recipes.constants import SUBSTITUTION_QUALITY_MIN

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "substitution_rules.json"


@dataclass(frozen=True)
class SubRule:
    frm: str
    to: str
    quality: float
    forbidden: bool
    recipe_slug: str | None = None


def load_seed_rows() -> list[dict]:
    if not FIXTURE.is_file():
        return []
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return list(payload or [])


def upsert_substitution_rules() -> int:
    """Create global rules from seed. Missing canonical_id → skip, do not fail import."""
    from apps.recipes.models import Ingredient, SubstitutionRule

    rows = load_seed_rows()
    ids = {row["from"] for row in rows} | {row["to"] for row in rows}
    found = {
        item.canonical_id: item
        for item in Ingredient.objects.filter(canonical_id__in=ids)
    }
    written = 0
    for row in rows:
        src = found.get(row["from"])
        dst = found.get(row["to"])
        if src is None or dst is None:
            continue
        _, created = SubstitutionRule.objects.update_or_create(
            from_ingredient=src,
            to_ingredient=dst,
            recipe=None,
            defaults={
                "quality": Decimal(str(row.get("quality") or 0)),
                "forbidden": bool(row.get("forbidden")),
                "note": row.get("note") or "",
            },
        )
        if created:
            written += 1
        else:
            written += 1
    return written


def rules_for_recipe(recipe_slug: str | None, stored: list[SubRule]) -> list[SubRule]:
    specific = [rule for rule in stored if rule.recipe_slug == recipe_slug]
    global_rules = [rule for rule in stored if rule.recipe_slug is None]
    overridden = {(rule.frm, rule.to) for rule in specific}
    return specific + [rule for rule in global_rules if (rule.frm, rule.to) not in overridden]


def stored_rules_from_db() -> list[SubRule]:
    from apps.recipes.models import SubstitutionRule

    out: list[SubRule] = []
    for row in SubstitutionRule.objects.select_related(
        "from_ingredient", "to_ingredient", "recipe"
    ):
        out.append(
            SubRule(
                frm=row.from_ingredient.canonical_id,
                to=row.to_ingredient.canonical_id,
                quality=float(row.quality),
                forbidden=bool(row.forbidden),
                recipe_slug=row.recipe.slug if row.recipe_id else None,
            )
        )
    return out


def cover_need(need: str, have: set[str], rules: list[SubRule]) -> tuple[str | None, float | None]:
    if need in have:
        return need, 1.0
    candidates = [
        rule
        for rule in rules
        if rule.frm == need
        and rule.to in have
        and not rule.forbidden
        and rule.quality >= SUBSTITUTION_QUALITY_MIN
    ]
    if not candidates:
        return None, None
    best = max(candidates, key=lambda rule: rule.quality)
    return best.to, best.quality
```

---

## 35. `backend/apps/recipes/urls.py`

- Путь: `v2/backend/apps/recipes/urls.py`
- Классы и функции: нет классов/функций верхнего уровня
- Строк: 15

```python
from django.urls import path

from apps.recipes.views import (
    IngredientListView,
    RecipeDetailView,
    RecipeListView,
    RecommendationListView,
)

urlpatterns = [
    path("recipes/", RecipeListView.as_view(), name="recipe-list"),
    path("recipes/<slug:slug>/", RecipeDetailView.as_view(), name="recipe-detail"),
    path("recommendations/", RecommendationListView.as_view(), name="recommendations"),
    path("ingredients/", IngredientListView.as_view(), name="ingredient-list"),
]
```

---

## 36. `backend/apps/recipes/views.py`

- Путь: `v2/backend/apps/recipes/views.py`
- Классы и функции: CatalogPagination, RecipeListView, RecipeDetailView, IngredientListView, RecommendationListView
- Строк: 439

```python
import random
from hashlib import sha1

from django.core.cache import cache
from django.db.models import Exists, OuterRef, Prefetch, Q
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeVariant
from apps.recipes.pantry_vocab import CANONICAL_INGREDIENT_LABEL_RU, groups_to_expand
from apps.recipes.query import (
    parse_codes,
    parse_have,
    parse_have_groups,
    parse_intent,
    parse_optional_decimal,
    parse_sample,
    parse_without_allergens,
)
from apps.recipes.serializers import serialize_recipe_detail, serialize_recipe_list_item
from apps.recipes.services.assemble import (
    assemble_recipe,
    catalog_allergens,
    catalog_protein_bases,
    catalog_protein_variants,
    pick_anchor,
)
from apps.recipes.services.pantry import (
    expand_have_group,
    resolve_pantry_text,
)
from apps.recipes.services.scale import resolve_scale
from apps.recipes.services.search import apply_catalog_search
from apps.recipes.services.solve import (
    assign_buckets,
    build_board,
    is_standalone_dish,
    serialize_solution,
    solve_recipe,
)
from apps.recipes.services.substitutions import stored_rules_from_db

REC_CACHE_TTL = 45


def _solver_card(recipe) -> dict:
    return {
        "has_delta_variants": any(
            item.axis == "addon" and item.has_delta for item in recipe.variants.all()
        ),
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "protein_bases": catalog_protein_bases(recipe),
        "protein_variants": catalog_protein_variants(recipe),
    }


def _rec_cache_key(
    *,
    protein: list[str],
    method: list[str],
    dish: list[str],
    equipment: list[str],
    cuts: list[str],
    without: list[str],
    have: list[str],
    have_groups: list[str],
    intents: list[str],
) -> str:
    raw = "|".join(
        [
            ",".join(protein),
            ",".join(method),
            ",".join(dish),
            ",".join(equipment),
            ",".join(cuts),
            ",".join(without),
            ",".join(sorted(have)),
            ",".join(have_groups),
            ",".join(intents),
        ]
    )
    return "rec:v4:" + sha1(raw.encode("utf-8")).hexdigest()


def _idle_recommendations(filters: dict) -> dict:
    return {
        "filters": filters,
        "featured": None,
        "alternatives": [],
        "buckets": {"now": [], "almost": [], "best": []},
        "results": [],
    }


class CatalogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 500


def _published():
    return Recipe.objects.filter(status="published").prefetch_related(
        Prefetch(
            "ingredients",
            queryset=RecipeIngredient.objects.select_related("ingredient").order_by(
                "position"
            ),
        ),
        "steps",
        "variants",
    )


def _list_cards():
    return Recipe.objects.filter(status="published").prefetch_related(
        Prefetch(
            "ingredients",
            queryset=RecipeIngredient.objects.select_related("ingredient").order_by(
                "position"
            ),
        ),
        "variants",
    )


def _solver_qs(*, with_ingredients: bool = False):
    """Published families for ranking. Snapshots live on the row; steps are unused."""
    qs = Recipe.objects.filter(status="published").prefetch_related("variants")
    if with_ingredients:
        qs = qs.prefetch_related(
            Prefetch(
                "ingredients",
                queryset=RecipeIngredient.objects.select_related("ingredient").order_by(
                    "position"
                ),
            )
        )
    return qs


def _apply_filters(qs, request, *, with_search: bool):
    protein = parse_codes(request, "protein_base")
    method = parse_codes(request, "cook_method")
    dish = parse_codes(request, "dish_type")
    equipment = parse_codes(request, "equipment")
    cuts = parse_codes(request, "cuts")
    if protein:
        qs = qs.filter(
            Q(protein_base__in=protein)
            | Q(protein_bases_extra__overlap=protein)
            | Exists(
                RecipeVariant.objects.filter(
                    recipe_id=OuterRef("pk"),
                    axis="addon",
                    has_delta=True,
                    protein_base_override__in=protein,
                )
            )
        )
    if method:
        qs = qs.filter(
            Q(cook_method__in=method)
            | Exists(
                RecipeVariant.objects.filter(
                    recipe_id=OuterRef("pk"),
                    axis="equipment",
                    has_delta=True,
                    cook_method_override__in=method,
                )
            )
        )
    if dish:
        qs = qs.filter(dish_type__in=dish)
    if equipment:
        qs = qs.filter(
            Q(equipment__in=equipment)
            | Exists(
                RecipeVariant.objects.filter(
                    recipe_id=OuterRef("pk"),
                    axis="equipment",
                    has_delta=True,
                    equipment__in=equipment,
                )
            )
        )
    if cuts:
        qs = qs.filter(allowed_cuts__overlap=cuts)
    if with_search:
        q = request.query_params.get("q", "").strip()
        if q:
            qs = apply_catalog_search(qs, q)
    return qs.distinct(), protein, method, dish, equipment, cuts


def _exclude_allergens(recipes: list[Recipe], codes: list[str]) -> list[Recipe]:
    if not codes:
        return recipes
    kept = []
    for recipe in recipes:
        allergens = catalog_allergens(recipe)
        hit = False
        for code in codes:
            if code in allergens.get("contains", []) or code in allergens.get("unknown", []):
                hit = True
                break
        if not hit:
            kept.append(recipe)
    return kept


class RecipeListView(APIView):
    def get(self, request):
        qs, _, _, _, _, _ = _apply_filters(_list_cards(), request, with_search=True)
        without = parse_without_allergens(request)
        sample_n = parse_sample(request)
        if sample_n is not None:
            if without:
                recipes = _exclude_allergens(list(qs), without)
                recipes = random.sample(recipes, min(sample_n, len(recipes)))
            else:
                pks = list(qs.order_by("?").values_list("pk", flat=True)[:sample_n])
                by_id = {recipe.pk: recipe for recipe in _list_cards().filter(pk__in=pks)}
                recipes = [by_id[pk] for pk in pks if pk in by_id]
            data = [serialize_recipe_list_item(recipe) for recipe in recipes]
            return Response({"count": len(data), "next": None, "previous": None, "results": data})
        qs = qs.order_by("title")
        paginator = CatalogPagination()
        if without:
            recipes = _exclude_allergens(list(qs), without)
            page = paginator.paginate_queryset(recipes, request, view=self)
        else:
            page = paginator.paginate_queryset(qs, request, view=self)
        data = [serialize_recipe_list_item(recipe) for recipe in page]
        return paginator.get_paginated_response(data)


class RecipeDetailView(APIView):
    def get(self, request, slug: str):
        recipe = _published().filter(slug=slug).first()
        if recipe is None:
            raise NotFound("Рецепт не найден.")
        from apps.prep.services.context import resolve_prep_for_recipe

        prep_pack = resolve_prep_for_recipe(recipe, request)
        variant = (request.query_params.get("variant") or "").strip() or None
        equipment = (request.query_params.get("equipment") or "").strip() or None
        assembled = assemble_recipe(recipe, variant_code=variant, equipment_code=equipment)
        servings = None if prep_pack else parse_optional_decimal(request, "servings")
        anchor_weight = None if prep_pack else parse_optional_decimal(request, "anchor_weight")
        anchor = pick_anchor(assembled.ingredients)
        scale = resolve_scale(
            recipe_scalable=recipe.scalable,
            recipe_servings=recipe.servings,
            anchor_amount=anchor["amount"] if anchor else None,
            anchor_unit=anchor["unit"] if anchor else None,
            servings=servings,
            anchor_weight=anchor_weight,
            anchor_name=(anchor.get("name") if anchor else None),
        )
        data = serialize_recipe_detail(recipe, assembled, scale)
        if prep_pack:
            data["steps"] = prep_pack["steps"]
            data["prep"] = prep_pack["prep"]
            data["prep_context"] = prep_pack["prep_context"]
            data["scaling"] = prep_pack["scaling"]
        return Response(data)


class IngredientListView(APIView):
    def get(self, request):
        from apps.recipes.models import Ingredient
        from apps.recipes.pantry_vocab import (
            CANONICAL_INGREDIENT_LABEL_RU,
            HAVE_GROUP_CHILDREN,
            HAVE_GROUP_LABEL_RU,
            HAVE_UI_GROUPS,
            items_for_have_group,
            shopping_label,
        )

        text = (request.query_params.get("text") or "").strip()
        titles = {
            **CANONICAL_INGREDIENT_LABEL_RU,
            **dict(Ingredient.objects.values_list("canonical_id", "title")),
        }
        known = set(titles)
        if text:
            found, unknown = resolve_pantry_text(text, titles=titles, known=known)
            items = [{"canonical_id": cid, "title": shopping_label(cid, titles)} for cid in found]
            return Response({"items": items, "unknown": unknown})

        def group_payload(code: str) -> dict:
            children = HAVE_GROUP_CHILDREN.get(code, ())
            payload: dict = {
                "id": code,
                "title": HAVE_GROUP_LABEL_RU[code],
                "items": [
                    {"canonical_id": cid, "title": shopping_label(cid, {**titles, **CANONICAL_INGREDIENT_LABEL_RU})}
                    for cid in items_for_have_group(code)
                ],
            }
            if children:
                payload["items"] = []
                payload["children"] = [group_payload(child) for child in children]
            return payload

        return Response({"groups": [group_payload(code) for code in HAVE_UI_GROUPS]})


class RecommendationListView(APIView):
    def get(self, request):
        protein = parse_codes(request, "protein_base")
        method = parse_codes(request, "cook_method")
        dish = parse_codes(request, "dish_type")
        equipment = parse_codes(request, "equipment")
        cuts = parse_codes(request, "cuts")
        without = parse_without_allergens(request)
        have = parse_have(request)
        explicit_have = list(have)
        have_groups = parse_have_groups(request)
        chosen = set(have)
        for group in groups_to_expand(have_groups):
            group_ids = expand_have_group(group)
            if chosen & set(group_ids):
                continue
            for cid in group_ids:
                if cid not in have:
                    have.append(cid)
        intents = parse_intent(request)
        have = list(dict.fromkeys(have))
        filters = {
            "protein_base": protein,
            "cook_method": method,
            "dish_type": dish,
            "equipment": equipment,
            "cuts": cuts,
            "have": have,
            "have_group": have_groups,
            "intent": intents,
        }
        asked = bool(
            protein
            or method
            or dish
            or equipment
            or cuts
            or without
            or have
            or have_groups
            or intents
        )
        if not asked:
            return Response(_idle_recommendations(filters))
        cache_key = _rec_cache_key(
            protein=protein,
            method=method,
            dish=dish,
            equipment=equipment,
            cuts=cuts,
            without=without,
            have=have,
            have_groups=have_groups,
            intents=intents,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        qs, protein, method, dish, equipment, cuts = _apply_filters(
            _solver_qs(with_ingredients=bool(without)),
            request,
            with_search=False,
        )
        recipes = _exclude_allergens(list(qs), without)
        rules = stored_rules_from_db() if have else []
        titles = {
            **CANONICAL_INGREDIENT_LABEL_RU,
            **dict(Ingredient.objects.values_list("canonical_id", "title")),
        }
        solutions = []
        for recipe in recipes:
            item = _solver_card(recipe)
            solved = solve_recipe(
                recipe,
                filter_protein=protein,
                filter_method=method,
                filter_dish=dish,
                filter_equipment=equipment,
                have=have,
                catalog_item=item,
                rules=rules,
                titles=titles,
                intents=intents,
                explicit_have=explicit_have,
            )
            if solved is not None:
                solutions.append(solved)
        solutions.sort(
            key=lambda row: (
                (
                    int(not is_standalone_dish(row.dish_type)),
                    -int(row.have_all),
                    -row.have_used,
                    -row.pantry_hits,
                    -row.score,
                    row.title,
                )
                if have
                else (
                    int(not is_standalone_dish(row.dish_type)),
                    -row.score,
                    row.title,
                )
            )
        )
        buckets = assign_buckets(solutions, has_have=bool(have))
        featured, alternatives = build_board(solutions, buckets, has_have=bool(have))
        if have:
            visible = buckets["now"] + buckets["almost"] + buckets["best"]
        else:
            visible = [featured] if featured else []
            visible.extend(item for _, item in alternatives)
        payload = {
            "filters": filters,
            "featured": serialize_solution(featured) if featured else None,
            "alternatives": [
                {**serialize_solution(item), "label": label}
                for label, item in alternatives
            ],
            "buckets": {
                "now": [serialize_solution(item) for item in buckets["now"]],
                "almost": [serialize_solution(item) for item in buckets["almost"]],
                "best": [serialize_solution(item) for item in buckets["best"]],
            },
            "results": [serialize_solution(item) for item in visible],
        }
        cache.set(cache_key, payload, REC_CACHE_TTL)
        return Response(payload)
```

---
