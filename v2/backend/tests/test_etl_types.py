"""Strict draft types, Decimal JSON, nutrition seed validation."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from apps.core.numbers import decimal_json
from apps.recipes.etl.draft import parse_draft, validate_draft
from apps.recipes.etl.normalizers import DraftValidationError, as_bool, as_int
from apps.recipes.etl.nutrition import _row_defaults, load_ingredient_nutrition
from apps.recipes.etl.serialize import _num


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


def test_as_bool_rejects_strings_and_ints():
    with pytest.raises(DraftValidationError):
        as_bool("false", field="scalable")
    with pytest.raises(DraftValidationError):
        as_bool("0", field="scalable")
    with pytest.raises(DraftValidationError):
        as_bool(1, field="scalable")
    with pytest.raises(DraftValidationError):
        as_bool(0, field="scalable")
    assert as_bool(True, field="scalable") is True
    assert as_bool(False, field="optional") is False
    assert as_bool(None, field="optional", default=False) is False


def test_as_int_rejects_bool_and_float():
    with pytest.raises(DraftValidationError):
        as_int(True, field="position")
    with pytest.raises(DraftValidationError):
        as_int(1.0, field="position")
    with pytest.raises(DraftValidationError):
        as_int("2", field="position")
    assert as_int(2, field="position") == 2


def test_validate_rejects_false_strings_on_booleans():
    for raw_value in ("false", "0", 1, 0):
        payload = _overlay_min()
        payload["ingredients"][0]["scalable"] = raw_value
        errors = validate_draft(payload, overlay=True)
        assert any("scalable" in item for item in errors)


def test_validate_rejects_nan_and_negative_amount():
    payload = _overlay_min()
    payload["ingredients"][0]["amount"] = float("nan")
    errors = validate_draft(payload, overlay=True)
    assert any("NaN" in item or "amount" in item for item in errors)

    payload = _overlay_min()
    payload["ingredients"][0]["amount"] = -1
    errors = validate_draft(payload, overlay=True)
    assert any("amount" in item for item in errors)


def test_parse_draft_does_not_publish():
    item = parse_draft(_overlay_min(), known_ingredients={"beef": {"title": "говядина"}})
    assert "status" not in item or item.get("status") != "published"
    assert item["scalable"] is True
    assert item["lines"][0]["is_anchor"] is True


def test_parse_draft_rejects_bool_as_int_position():
    payload = _overlay_min()
    payload["ingredients"][0]["position"] = True
    errors = validate_draft(payload, overlay=True)
    assert any("integer" in item or "position" in item for item in errors)


def test_decimal_json_not_float():
    assert decimal_json(Decimal("0.1")) == "0.1"
    assert decimal_json(Decimal("500")) == 500
    assert _num(Decimal("0.3")) == "0.3"
    assert not isinstance(_num(Decimal("0.3")), float)


def test_nutrition_row_rejects_nan_and_negative():
    base = {
        "kcal": 100,
        "protein_g": 10,
        "fat_g": 1,
        "carbs_g": 2,
        "source": "editorial",
    }
    with pytest.raises(ValueError, match="конечное"):
        _row_defaults("x", {**base, "kcal": "NaN"})
    with pytest.raises(ValueError, match="конечное"):
        _row_defaults("x", {**base, "kcal": "Infinity"})
    with pytest.raises(ValueError, match="конечное"):
        _row_defaults("x", {**base, "protein_g": -1})


def test_nutrition_seed_invalid_does_not_update(tmp_path: Path):
    seed = tmp_path / "seed.json"
    seed.write_text(
        json.dumps(
            {
                "ok": {
                    "kcal": 1,
                    "protein_g": 1,
                    "fat_g": 1,
                    "carbs_g": 1,
                    "source": "editorial",
                },
                "bad": {
                    "kcal": "NaN",
                    "protein_g": 1,
                    "fat_g": 1,
                    "carbs_g": 1,
                    "source": "editorial",
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="NaN|конечное"):
        load_ingredient_nutrition(seed)
