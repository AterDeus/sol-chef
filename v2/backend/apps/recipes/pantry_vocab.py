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
FISH_PROTEIN = frozenset({"fish_white_sea", "fish_red_sea", "fish_river", "seafood"})

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
