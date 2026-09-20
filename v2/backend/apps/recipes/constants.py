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

