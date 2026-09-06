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
