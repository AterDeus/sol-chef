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
