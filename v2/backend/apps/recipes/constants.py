"""VOCAB codes and display labels (API UI strings in Russian).

Frozensets re-export domain.enums values so existing imports keep working.
Pantry taxonomy lives in pantry_vocab; constants only lazy-reexports for
callers that still import HAVE_GROUPS from here.
"""

from __future__ import annotations

from apps.recipes.domain.enums import (
    AdaptationType,
    Allergen,
    CookMethod,
    Cut,
    DishType,
    EnergyProfile,
    Equipment,
    HighRisk,
    NutritionBasis,
    NutritionSource,
    ProteinBase,
    RecipeStatus,
    ScaleMode,
    Unit,
    UseCase,
    VariantAxis,
    YieldKind,
)

PROTEIN_BASE = frozenset(ProteinBase.values)
COOK_METHOD = frozenset(CookMethod.values)
DISH_TYPE = frozenset(DishType.values)
SCALE_MODE = frozenset(ScaleMode.values)
UNIT = frozenset(Unit.values)
ALLERGEN = frozenset(Allergen.values)
HIGH_RISK = frozenset(HighRisk.values)
ENERGY_PROFILE = frozenset(EnergyProfile.values)
NUTRITION_BASIS = frozenset(NutritionBasis.values)
YIELD_KIND = frozenset(YieldKind.values)
NUTRITION_SOURCE = frozenset(NutritionSource.values)
EQUIPMENT = frozenset(Equipment.values)
# Vessel plus method-only family codes that live on the equipment axis
# (air_fryer / steam: VOCAB cook_method, no Equipment column).
EQUIPMENT_AXIS = EQUIPMENT | frozenset({CookMethod.AIR_FRYER, CookMethod.STEAM})
CUT = frozenset(Cut.values)
VARIANT_AXIS = frozenset(VariantAxis.values)
USE_CASE = frozenset(UseCase.values)
ADAPTATION_TYPE = frozenset(AdaptationType.values)
RECIPE_STATUS = frozenset(RecipeStatus.values)

# Not a plate of food: compound butter, flavored oil, fried onions, jam.
# Calculator "what should I cook" skips these while a standalone dish exists.
COMPONENT_DISH_TYPES = frozenset({DishType.SAUCE, DishType.PRESERVE})

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

INTENT = frozenset({"fast", "pantry", "oven", "light", "easy", "batch"})

_PANTRY_EXPORTS = frozenset(
    {
        "CANONICAL_INGREDIENT_LABEL_RU",
        "HAVE_GROUP_LABEL_RU",
        "HAVE_GROUPS",
        "HAVE_TEXT_ALIASES",
        "HAVE_UI_GROUPS",
        "PANTRY_ASSUMED",
        "PANTRY_COMMON",
        "PANTRY_EXOTIC",
        "PANTRY_LEGACY_OR",
        "PANTRY_PREP",
        "PANTRY_SPICES",
        "SHOPPING_GROUPS",
        "SHOPPING_GROUP_LABEL_RU",
    }
)


def __getattr__(name: str):
    """Lazy pantry re-export so query.py/solve imports keep working."""
    if name == "PANTRY_CHIP_GROUPS":
        from apps.recipes.pantry_vocab import SHOPPING_GROUPS

        return SHOPPING_GROUPS
    if name in _PANTRY_EXPORTS:
        from apps.recipes import pantry_vocab

        return getattr(pantry_vocab, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

INTENT_LABEL_RU = {
    "fast": "Быстро",
    "pantry": "Из того, что есть",
    "oven": "В духовке",
    "light": "Полегче",
    "easy": "Проще",
    "batch": "На несколько дней",
}

