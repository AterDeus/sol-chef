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

# Homemade leftover/component. Not supermarket raw meat.
# Species chips (beef, pork…) mean raw cuts unless the person names this id.
_PREP = ("shredded_beef",)
PANTRY_PREP = frozenset(_PREP)

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
    "beef",
    "beef_mince",
    "beef_tenderloin",
    "steak",
    "beef_thick_rib",
    "ribeye",
    "beef_thin_rib",
    "beef_chuck",
    "beef_neck",
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
    "prep": _PREP,
    "meat": _PORK + _BEEF + _LAMB + _OFFAL,
    "fish": SHOPPING_GROUP_IDS["fish"],
    "veg": SHOPPING_GROUP_IDS["veg"] + SHOPPING_GROUP_IDS["potatoes"],
    "grains": SHOPPING_GROUP_IDS["grains"],
    "dairy": tuple(cid for cid in SHOPPING_GROUP_IDS["dairy"] if cid not in {"eggs", "egg"}),
    "eggs": ("eggs", "egg"),
    "legumes": ("beans", "chickpeas", "lentils", "peas"),
    "canned": (
        "canned_tomatoes",
        "tomato_paste",
        "tomato_puree",
        "canned_corn",
        "canned_green_peas",
        "canned_beans",
        "canned_chickpeas",
        "olives",
        "pickles",
    ),
    "frozen": SHOPPING_GROUP_IDS["frozen"],
    "bakery": SHOPPING_GROUP_IDS["bakery"],
    "sauces": (
        "tomato_sauce",
        "ketchup",
        "mayonnaise",
        "soy_sauce",
        "mustard",
    ),
    "fats": ("sunflower_oil", "vegetable_oil", "olive_oil"),
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
    "offal": "Субпродукты",
    "prep": "Полуфабрикаты",
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

# First-level chips only open a picker. Not "I have every SKU in this aisle".
HAVE_GROUP_PICKER_ONLY = frozenset(HAVE_UI_GROUPS)

# First screen: coarse chips. Meat opens species, then supermarket cuts.
# Leftovers are a sibling of species, not mixed into raw beef/pork.
HAVE_GROUP_CHILDREN: dict[str, tuple[str, ...]] = {
    "meat": ("pork", "beef", "lamb", "offal", "prep"),
    "other": ("legumes", "canned", "frozen", "bakery", "sauces", "fats"),
}

# Calculator chips: species already in the heading, so drop «говяжья/свиная».
HAVE_CHIP_LABEL_RU: dict[str, str] = {
    "chicken_breast": "Грудка",
    "chicken_thighs": "Бёдра",
    "chicken_drumsticks": "Голени",
    "chicken_wings": "Крылья",
    "whole_chicken": "Целиком",
    "chicken_mince": "Фарш",
    "pork_mince": "Фарш",
    "pork_neck": "Шея",
    "pork_shoulder": "Лопатка",
    "pork_loin": "Корейка",
    "pork_tenderloin": "Вырезка",
    "pork_chops": "Отбивные",
    "pork_ribs": "Рёбра",
    "pork_belly": "Грудинка",
    "beef": "Любая говядина",
    "beef_mince": "Фарш",
    "beef_tenderloin": "Вырезка",
    "beef_chuck": "Лопатка",
    "beef_neck": "Шея",
    "beef_rump": "Огузок",
    "beef_brisket": "Грудинка",
    "beef_ribs": "Рёбра",
    "beef_shank": "Голяшка",
    "beef_tail": "Хвост",
    "lamb_mince": "Фарш",
    "lamb_shoulder": "Лопатка",
    "lamb_neck": "Шея",
    "lamb_chops": "Отбивные",
    "lamb_ribs": "Рёбра",
    "lamb_shank": "Голяшка",
    "lamb_leg": "Окорок",
    "canned_tomatoes": "Томаты",
    "tomato_paste": "Томатная паста",
    "tomato_puree": "Томатное пюре",
    "canned_corn": "Кукуруза",
    "canned_green_peas": "Горошек",
    "canned_beans": "Фасоль в банке",
    "canned_chickpeas": "Нут в банке",
    "frozen_vegetables": "Овощная смесь",
    "frozen_peas": "Горошек",
    "frozen_corn": "Кукуруза",
    "frozen_green_beans": "Стручковая фасоль",
    "frozen_spinach": "Шпинат",
    "sunflower_oil": "Подсолнечное",
    "vegetable_oil": "Растительное",
    "olive_oil": "Оливковое",
    "tomato_sauce": "Томатный",
    "soy_sauce": "Соевый",
    "white_bread": "Белый",
    "rye_bread": "Чёрный",
    "breadcrumbs": "Сухари",
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
    "lamb": ("lamb_shoulder", "lamb_mince"),
    "prep": ("shredded_beef",),
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
    "shredded_beef": "говядина на волокна",
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
    "любая курица": "chicken",
    "свинина": "pork",
    "свинину": "pork",
    "любая свинина": "pork",
    "говядина": "beef",
    "говядину": "beef",
    "любая говядина": "beef",
    "говядина на волокна": "shredded_beef",
    "томленая говядина": "shredded_beef",
    "говядина томеная": "shredded_beef",
    "рваная говядина": "shredded_beef",
    "рваную говядину": "shredded_beef",
    "полуфабрикаты": "prep",
    "заготовка": "prep",
    "заготовки": "prep",
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
    "любая баранина": "lamb",
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
    "бобовые": "legumes",
    "консервы": "canned",
    "заморозка": "frozen",
    "соусы": "sauces",
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


def title_case_ru(label: str) -> str:
    if not label:
        return label
    return label[0].upper() + label[1:]


def chip_title(cid: str, titles: dict[str, str] | None = None) -> str:
    """Calculator chip: short inside a species, first letter capital."""
    if cid in HAVE_CHIP_LABEL_RU:
        return HAVE_CHIP_LABEL_RU[cid]
    return title_case_ru(shopping_label(cid, titles))


def likely_items_for_have_group(code: str) -> tuple[str, ...]:
    return SHOPPING_LIKELY.get(code, ())


def items_for_have_group(code: str) -> tuple[str, ...]:
    return tuple(HAVE_GROUPS.get(code, ()))


def groups_to_expand(have_groups: list[str]) -> list[str]:
    """Species chips may expand; first-level aisle chips never do.

    Skip parent `meat` / `other` if a child shelf is already selected.
    Picker-only chips (chicken, meat, veg, other…) only open the next
    choice — not inventory.
    """
    selected = set(have_groups)
    skip = {
        parent
        for parent, children in HAVE_GROUP_CHILDREN.items()
        if selected & set(children)
    }
    skip |= HAVE_GROUP_PICKER_ONLY
    return [code for code in have_groups if code not in skip]


def availability_class(canonical_id: str) -> str:
    if canonical_id in PANTRY_ASSUMED or canonical_id in PANTRY_LEGACY_OR:
        return "assumed"
    if canonical_id in PANTRY_COMMON:
        return "common"
    if canonical_id in PANTRY_EXOTIC:
        return "exotic"
    if canonical_id in PANTRY_PREP:
        return "prep"
    return "explicit"
