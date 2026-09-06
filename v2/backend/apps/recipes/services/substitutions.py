"""Load and match substitution rules. Runtime LLM is forbidden."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from apps.recipes.constants import SUBSTITUTION_QUALITY_MIN

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "substitution_rules.json"


@dataclass(frozen=True)
class SubRule:
    frm: str
    to: str
    quality: float
    forbidden: bool
    recipe_slug: str | None = None


def load_seed_rows() -> list[dict]:
    if not FIXTURE.is_file():
        return []
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return list(payload or [])


def upsert_substitution_rules() -> int:
    """Create global rules from seed. Missing canonical_id → skip, do not fail import."""
    from apps.recipes.models import Ingredient, SubstitutionRule

    rows = load_seed_rows()
    ids = {row["from"] for row in rows} | {row["to"] for row in rows}
    found = {
        item.canonical_id: item
        for item in Ingredient.objects.filter(canonical_id__in=ids)
    }
    written = 0
    for row in rows:
        src = found.get(row["from"])
        dst = found.get(row["to"])
        if src is None or dst is None:
            continue
        _, created = SubstitutionRule.objects.update_or_create(
            from_ingredient=src,
            to_ingredient=dst,
            recipe=None,
            defaults={
                "quality": Decimal(str(row.get("quality") or 0)),
                "forbidden": bool(row.get("forbidden")),
                "note": row.get("note") or "",
            },
        )
        if created:
            written += 1
        else:
            written += 1
    return written


def rules_for_recipe(recipe_slug: str | None, stored: list[SubRule]) -> list[SubRule]:
    specific = [rule for rule in stored if rule.recipe_slug == recipe_slug]
    global_rules = [rule for rule in stored if rule.recipe_slug is None]
    overridden = {(rule.frm, rule.to) for rule in specific}
    return specific + [rule for rule in global_rules if (rule.frm, rule.to) not in overridden]


def stored_rules_from_db() -> list[SubRule]:
    from apps.recipes.models import SubstitutionRule

    out: list[SubRule] = []
    for row in SubstitutionRule.objects.select_related(
        "from_ingredient", "to_ingredient", "recipe"
    ):
        out.append(
            SubRule(
                frm=row.from_ingredient.canonical_id,
                to=row.to_ingredient.canonical_id,
                quality=float(row.quality),
                forbidden=bool(row.forbidden),
                recipe_slug=row.recipe.slug if row.recipe_id else None,
            )
        )
    return out


def cover_need(need: str, have: set[str], rules: list[SubRule]) -> tuple[str | None, float | None]:
    if need in have:
        return need, 1.0
    candidates = [
        rule
        for rule in rules
        if rule.frm == need
        and rule.to in have
        and not rule.forbidden
        and rule.quality >= SUBSTITUTION_QUALITY_MIN
    ]
    if not candidates:
        return None, None
    best = max(candidates, key=lambda rule: rule.quality)
    return best.to, best.quality
