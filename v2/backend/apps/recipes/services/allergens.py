"""Allergen merge. unknown never collapses to «нет»."""

from __future__ import annotations

from collections.abc import Iterable


def merge_allergen_lists(
    rows: Iterable[tuple[list[str], list[str], list[str]]],
) -> dict[str, list[str]]:
    contains: set[str] = set()
    may_contain: set[str] = set()
    unknown: set[str] = set()
    for c, m, u in rows:
        contains.update(c or [])
        may_contain.update(m or [])
        unknown.update(u or [])
    may_contain -= contains
    unknown -= contains
    return {
        "contains": sorted(contains),
        "may_contain": sorted(may_contain),
        "unknown": sorted(unknown),
    }


def recipe_allergens_from_ingredients(ingredients) -> dict[str, list[str]]:
    rows = (
        (
            list(ing.allergens_contains or []),
            list(ing.allergens_may_contain or []),
            list(ing.allergens_unknown or []),
        )
        for ing in ingredients
    )
    return merge_allergen_lists(rows)


def normalize_ru(text: str) -> str:
    """Mirror of SQL normalize_ru: lower + ё→е. Not unaccent."""
    return (text or "").translate(str.maketrans("Ёё", "Ее")).lower()
