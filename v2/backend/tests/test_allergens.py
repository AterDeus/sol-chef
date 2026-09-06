from apps.recipes.etl.ingredients import is_optional_line
from apps.recipes.services.allergens import merge_allergen_lists, normalize_ru
from apps.recipes.services.assemble import allergens_from_lines


def test_u6_normalize_ru_yo_equals_ye():
    assert normalize_ru("ёлка") == normalize_ru("елка")
    assert normalize_ru("Ёлка") == "елка"


def test_u7_unknown_allergen_is_not_none():
    merged = merge_allergen_lists(
        [
            ([], [], ["celery"]),
            (["milk"], [], []),
        ]
    )
    assert "celery" in merged["unknown"]
    assert merged["unknown"] != []
    assert "milk" in merged["contains"]
    assert "celery" not in merged["contains"]


def test_serving_yogurt_is_optional_not_dish_allergen():
    assert is_optional_line("натуральный — для подачи")
    assert is_optional_line("по желанию, для корочки")
    assert not is_optional_line("нарезать кусками")
    lines = [
        {
            "canonical_id": "chicken",
            "optional": False,
            "allergens_contains": [],
            "allergens_may_contain": [],
            "allergens_unknown": [],
        },
        {
            "canonical_id": "yogurt",
            "optional": True,
            "allergens_contains": ["milk"],
            "allergens_may_contain": [],
            "allergens_unknown": [],
        },
    ]
    assert allergens_from_lines(lines)["contains"] == []


def test_required_yogurt_counts_as_milk():
    lines = [
        {
            "canonical_id": "yogurt",
            "optional": False,
            "allergens_contains": ["milk"],
            "allergens_may_contain": [],
            "allergens_unknown": [],
        }
    ]
    assert "milk" in allergens_from_lines(lines)["contains"]
