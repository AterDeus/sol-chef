"""Ranking v0 — DEFAULTS weights. Hard filters drop, they do not score."""

from __future__ import annotations

from django.conf import settings

from apps.recipes.constants import PROTEIN_BASE_LABEL_RU, label_equipment_axis


def score_and_why(
    *,
    protein_base: str,
    cook_method: str,
    dish_type: str,
    equipment: str | None,
    editorial_tested: bool,
    filter_protein: list[str],
    filter_method: list[str],
    filter_dish: list[str],
    filter_equipment: list[str],
) -> tuple[int, list[str]]:
    weights = settings.RANKING_WEIGHTS
    score = 0
    why: list[str] = []
    if filter_protein and protein_base in filter_protein:
        score += int(weights["protein_base"])
        label = PROTEIN_BASE_LABEL_RU.get(protein_base, protein_base)
        why.append(f"основа — {label}")
    if filter_method and cook_method in filter_method:
        score += int(weights["cook_method"])
        why.append("совпал метод")
    if filter_dish and dish_type in filter_dish:
        score += int(weights["dish_type"])
        why.append("совпал тип блюда")
    if filter_equipment and equipment in filter_equipment:
        score += int(weights.get("equipment", weights["dish_type"]))
        label = label_equipment_axis(equipment)
        why.append(f"совпала посуда — {label}")
    if editorial_tested:
        score += int(weights["editorial_tested"])
        why.append("проверено редакцией")
    return score, why
