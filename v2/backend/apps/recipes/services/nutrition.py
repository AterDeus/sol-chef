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
