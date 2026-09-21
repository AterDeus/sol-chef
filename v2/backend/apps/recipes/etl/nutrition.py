"""Load Ingredient nutrition from the git seed. No HTTP, no FDC at runtime."""

from __future__ import annotations

import json
from pathlib import Path

from apps.recipes.constants import NUTRITION_BASIS, NUTRITION_SOURCE
from apps.recipes.etl.normalizers import finite_nonnegative
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
NUTRITION_UPDATE_FIELDS = (
    "kcal_per_100g",
    "protein_g_per_100g",
    "fat_g_per_100g",
    "carbs_g_per_100g",
    "nutrition_basis",
    "nutrition_source",
    "nutrition_source_id",
    "density_g_per_ml",
    *G_PER_FIELDS,
)
BULK_BATCH = 500


def seed_path() -> Path:
    return FIXTURE


def load_seed(path: Path | None = None) -> dict:
    target = path or FIXTURE
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{target.name}: нужен объект canonical_id → нутриенты")
    return payload


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
        "kcal_per_100g": finite_nonnegative(row["kcal"], field=f"{cid}:kcal"),
        "protein_g_per_100g": finite_nonnegative(row["protein_g"], field=f"{cid}:protein_g"),
        "fat_g_per_100g": finite_nonnegative(row["fat_g"], field=f"{cid}:fat_g"),
        "carbs_g_per_100g": finite_nonnegative(row["carbs_g"], field=f"{cid}:carbs_g"),
        "nutrition_basis": "raw_100g",
        "nutrition_source": source,
        "nutrition_source_id": row.get("source_id") or None,
    }
    if defaults["nutrition_basis"] not in NUTRITION_BASIS:
        raise ValueError(f"{cid}: nutrition_basis")
    if row.get("density_g_per_ml") is not None:
        defaults["density_g_per_ml"] = finite_nonnegative(
            row["density_g_per_ml"], field=f"{cid}:density_g_per_ml"
        )
    for field in G_PER_FIELDS:
        if row.get(field) is not None:
            defaults[field] = finite_nonnegative(row[field], field=f"{cid}:{field}")
    return defaults


def load_ingredient_nutrition(path: Path | None = None) -> dict:
    """Validate the whole seed, then bulk_update existing Ingredient rows."""
    payload = load_seed(path)
    validated: dict[str, dict] = {}
    invalid: list[str] = []
    for cid, row in payload.items():
        if not cid or cid.startswith("_"):
            continue
        try:
            validated[cid] = _row_defaults(cid, row)
        except ValueError as exc:
            invalid.append(str(exc))
    if invalid:
        extra = f" (+{len(invalid) - 12})" if len(invalid) > 12 else ""
        raise ValueError("; ".join(invalid[:12]) + extra)

    seed_ids = list(validated)
    rows = list(Ingredient.objects.filter(canonical_id__in=seed_ids))
    found = {obj.canonical_id for obj in rows}
    not_found = sorted(cid for cid in seed_ids if cid not in found)
    for obj in rows:
        for field, value in validated[obj.canonical_id].items():
            setattr(obj, field, value)
    update_fields = [name for name in NUTRITION_UPDATE_FIELDS if name]
    if rows:
        Ingredient.objects.bulk_update(rows, update_fields, batch_size=BULK_BATCH)
    return {"updated": len(rows), "not_found": not_found, "invalid": []}
