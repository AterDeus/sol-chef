"""Load Ingredient nutrition from the git seed. No HTTP, no FDC at runtime."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from apps.recipes.constants import NUTRITION_BASIS, NUTRITION_SOURCE
from apps.recipes.models import Ingredient

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "ingredient_nutrition.json"
MACRO_KEYS = ("kcal", "protein_g", "fat_g", "carbs_g")
G_PER_FIELDS = (
    "g_per_tsp",
    "g_per_tbsp",
    "g_per_pcs",
    "g_per_clove",
    "g_per_bunch",
    "g_per_slice",
)


def seed_path() -> Path:
    return FIXTURE


def load_seed(path: Path | None = None) -> dict:
    target = path or FIXTURE
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{target.name}: нужен объект canonical_id → нутриенты")
    return payload


def _dec(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Некорректное число {value!r}") from exc


def _row_defaults(cid: str, row: dict) -> dict:
    if not isinstance(row, dict):
        raise ValueError(f"{cid}: значение сида не объект")
    missing = [key for key in MACRO_KEYS if row.get(key) is None]
    if missing:
        raise ValueError(f"{cid}: в сиде нет {', '.join(missing)}")
    source = row.get("source")
    if source not in NUTRITION_SOURCE:
        raise ValueError(f"{cid}: nutrition_source {source!r}")
    defaults = {
        "kcal_per_100g": _dec(row["kcal"]),
        "protein_g_per_100g": _dec(row["protein_g"]),
        "fat_g_per_100g": _dec(row["fat_g"]),
        "carbs_g_per_100g": _dec(row["carbs_g"]),
        "nutrition_basis": "raw_100g",
        "nutrition_source": source,
        "nutrition_source_id": row.get("source_id") or None,
    }
    if defaults["nutrition_basis"] not in NUTRITION_BASIS:
        raise ValueError(f"{cid}: nutrition_basis")
    if row.get("density_g_per_ml") is not None:
        defaults["density_g_per_ml"] = _dec(row["density_g_per_ml"])
    for field in G_PER_FIELDS:
        if row.get(field) is not None:
            defaults[field] = _dec(row[field])
    return defaults


def load_ingredient_nutrition(path: Path | None = None) -> int:
    """Update existing Ingredient rows. Does not touch title/allergens."""
    payload = load_seed(path)
    updated = 0
    for cid, row in payload.items():
        if not cid or cid.startswith("_"):
            continue
        fields = _row_defaults(cid, row)
        count = Ingredient.objects.filter(canonical_id=cid).update(**fields)
        if count:
            updated += count
    return updated
