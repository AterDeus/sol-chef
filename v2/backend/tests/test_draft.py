import json
from copy import deepcopy
from pathlib import Path

from apps.recipes.etl.draft import known_from_v1_map, load_json, validate_draft

def _gold_path() -> Path:
    name = "barhatnaya-govyadina-po-kitajski.json"
    here = Path(__file__).resolve()
    candidates = [
        here.parents[2] / "docs" / "drafts" / "recipes" / name,
        Path("/v1-src/v2/docs/drafts/recipes") / name,
    ]
    for path in candidates:
        if path.is_file():
            return path
    return candidates[0]


GOLD = _gold_path()
INGREDIENT_MAP = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "recipes"
    / "fixtures"
    / "v1_ingredient_map.json"
)


def _known() -> dict:
    return known_from_v1_map(json.loads(INGREDIENT_MAP.read_text(encoding="utf-8")))


def _overlay_min() -> dict:
    return {
        "id": "x",
        "title": "X",
        "protein_base": "beef",
        "cook_method": "pan_fry",
        "dish_type": "main",
        "equipment": "skillet",
        "time_profile": {"total_minutes": 20, "active_minutes": 10},
        "effort_level": 2,
        "washing_level": 1,
        "use_cases": ["easy"],
        "adaptations": [],
        "ingredients": [
            {
                "canonical_id": "beef",
                "amount": 500,
                "unit": "g",
                "scale_mode": "linear",
                "is_anchor": True,
            }
        ],
        "steps": [
            {
                "text": "Обжарить порциями, не перегружать сковороду.",
                "equipment_note": "Порциями.",
            }
        ],
        "notes": [
            {"title": "A", "text": "один"},
            {"title": "B", "text": "два"},
            {"title": "C", "text": "три"},
        ],
    }


def test_gold_overlay_validates():
    raw = load_json(GOLD)
    assert validate_draft(raw, overlay=True, known_ingredients=_known()) == []


def test_soda_gentle_is_error():
    raw = load_json(GOLD)
    payload = deepcopy(raw)
    for line in payload["ingredients"]:
        if line["canonical_id"] == "baking_soda":
            line["scale_mode"] = "gentle"
    errors = validate_draft(payload, overlay=True, known_ingredients=_known())
    assert any("manual" in item for item in errors)


def test_sol_chef_url_is_critical():
    raw = load_json(GOLD)
    payload = deepcopy(raw)
    payload["source_url"] = "https://sol-chef.ru"
    errors = validate_draft(payload, overlay=True, known_ingredients=_known())
    assert any("sol-chef.ru" in item for item in errors)


def test_legacy_variation_text_without_delta_fails():
    payload = _overlay_min()
    payload["variations"] = [{"title": "С грибами", "text": "Добавить 200 г грибов."}]
    errors = validate_draft(payload, overlay=True)
    assert any("без дельты" in item for item in errors)


def test_ingredient_delta_requires_allergen_delta():
    raw = load_json(GOLD)
    payload = deepcopy(raw)
    payload["variants"][0].pop("allergen_delta")
    errors = validate_draft(payload, overlay=True, known_ingredients=_known())
    assert any("allergen_delta" in item for item in errors)


def test_zero_variants_ok_with_profile():
    errors = validate_draft(_overlay_min(), overlay=True)
    assert errors == []


def test_missing_time_profile_fails():
    payload = _overlay_min()
    payload.pop("time_profile")
    errors = validate_draft(payload, overlay=True)
    assert any("time_profile" in item for item in errors)


def test_unknown_use_case_fails():
    payload = _overlay_min()
    payload["use_cases"] = ["dinner"]
    errors = validate_draft(payload, overlay=True)
    assert any("use_case" in item for item in errors)


def test_empty_prep_key_fails():
    payload = _overlay_min()
    payload["prep"] = []
    errors = validate_draft(payload, overlay=True)
    assert any("prep" in item for item in errors)


def test_allergens_on_recipe_line_fail():
    payload = _overlay_min()
    payload["ingredients"][0]["allergens_contains"] = ["soy"]
    errors = validate_draft(payload, overlay=True)
    assert any("реестре" in item for item in errors)
