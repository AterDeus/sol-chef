"""Assemble display recipe: base → addon → equipment, then scale separately."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
from types import SimpleNamespace
from typing import Any

from apps.core.exceptions import DomainValidationError
from apps.recipes.services.allergens import merge_allergen_lists
from apps.recipes.services.nutrition import CANON_NUTRITION_FIELDS, enrich_lines_from_db


class VariantError(DomainValidationError):
    """Unknown or illegal variant / equipment query — API 400."""


def _d(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _copy_line(line: dict) -> dict:
    out = deepcopy(line)
    if out.get("amount") is not None:
        out["amount"] = _d(out["amount"])
    if out.get("amount_max") is not None:
        out["amount_max"] = _d(out["amount_max"])
    return out


def _nutrition_from_ingredient(ing) -> dict:
    return {field: getattr(ing, field) for field in CANON_NUTRITION_FIELDS}


def lines_from_recipe(recipe, *, include_nutrition: bool = True) -> list[dict]:
    rows = []
    for line in recipe.ingredients.all():
        ing = line.ingredient
        row = {
            "canonical_id": ing.canonical_id,
            "name": line.display_name or ing.title,
            "amount": line.amount,
            "amount_max": line.amount_max,
            "unit": line.unit,
            "detail": line.detail,
            "scalable": line.scalable,
            "scale_mode": line.scale_mode,
            "is_anchor": line.is_anchor,
            "optional": bool(line.optional),
            "nutrition_exclude": bool(line.nutrition_exclude),
            "nutrition_factor": line.nutrition_factor,
            "position": line.position,
            "allergens_contains": list(ing.allergens_contains or []),
            "allergens_may_contain": list(ing.allergens_may_contain or []),
            "allergens_unknown": list(ing.allergens_unknown or []),
        }
        if include_nutrition:
            row.update(_nutrition_from_ingredient(ing))
        rows.append(row)
    return rows


def allergen_lines_from_recipe(recipe) -> list[dict]:
    """List/catalog worst-case allergens: no nutrition, no step payload."""
    rows = []
    for line in recipe.ingredients.all():
        ing = line.ingredient
        rows.append(
            {
                "canonical_id": ing.canonical_id,
                "name": line.display_name or ing.title,
                "position": line.position,
                "optional": bool(line.optional),
                "allergens_contains": list(ing.allergens_contains or []),
                "allergens_may_contain": list(ing.allergens_may_contain or []),
                "allergens_unknown": list(ing.allergens_unknown or []),
            }
        )
    return rows


def steps_from_recipe(recipe) -> list[dict]:
    return [
        {
            "position": step.position,
            "text": step.text,
            "timer_seconds": step.timer_seconds,
            "timer_label": step.timer_label,
            "timer_note": step.timer_note,
            "pull_internal_temperature_c": step.pull_internal_temperature_c,
            "target_internal_temperature_c": step.target_internal_temperature_c,
            "hold_seconds": step.hold_seconds,
        }
        for step in recipe.steps.all()
    ]


def _matching_line_indexes(lines: list[dict], spec: dict) -> list[int]:
    if spec.get("position") is not None:
        pos = int(spec["position"])
        hits = [i for i, line in enumerate(lines) if line.get("position") == pos]
        if hits:
            return hits
        if 0 <= pos < len(lines):
            return [pos]
        return []
    cid = spec.get("canonical_id")
    if not cid:
        return []
    return [i for i, line in enumerate(lines) if line.get("canonical_id") == cid]


def require_line_index(lines: list[dict], spec: dict, *, action: str) -> int:
    hits = _matching_line_indexes(lines, spec)
    if not hits:
        raise VariantError(f"{action}: целевой ингредиент не найден")
    if len(hits) > 1:
        raise VariantError(f"{action}: целевой ингредиент неоднозначен")
    return hits[0]


def validate_ingredient_delta(base_lines: list[dict], delta: dict | None) -> None:
    if not delta:
        return
    touched: set[int] = set()
    for action in ("remove", "replace"):
        for spec in delta.get(action) or []:
            index = require_line_index(base_lines, spec, action=action)
            if index in touched:
                raise VariantError(f"{action}: линия изменяется более одного раза")
            touched.add(index)


def _matching_step_indexes(steps: list[dict], spec: dict) -> list[int]:
    pos = spec.get("position")
    if pos is None:
        return []
    return [i for i, step in enumerate(steps) if step.get("position") == pos]


def validate_step_delta(base_steps: list[dict], delta: dict | None) -> None:
    if not delta:
        return
    touched: set[int] = set()
    for spec in delta.get("replace") or []:
        if spec.get("position") is None:
            raise VariantError("replace: целевой шаг не найден")
        hits = _matching_step_indexes(base_steps, spec)
        if not hits:
            raise VariantError("replace: целевой шаг не найден")
        if len(hits) > 1:
            raise VariantError("replace: целевой шаг неоднозначен")
        index = hits[0]
        if index in touched:
            raise VariantError("replace: шаг изменяется более одного раза")
        touched.add(index)


def apply_ingredient_delta(lines: list[dict], delta: dict | None) -> list[dict]:
    if not delta:
        return [_copy_line(line) for line in lines]
    validate_ingredient_delta(lines, delta)
    out = [_copy_line(line) for line in lines]
    for spec in delta.get("remove") or []:
        idx = require_line_index(out, spec, action="remove")
        out.pop(idx)
    for spec in delta.get("replace") or []:
        idx = require_line_index(out, spec, action="replace")
        current = out[idx]
        merged = _copy_line(current)
        old_cid = current.get("canonical_id")
        for key in (
            "canonical_id",
            "name",
            "amount",
            "amount_max",
            "unit",
            "detail",
            "scalable",
            "scale_mode",
            "optional",
            "allergens_contains",
            "allergens_may_contain",
            "allergens_unknown",
        ):
            if key in spec and spec[key] is not None:
                merged[key] = spec[key]
        if merged.get("amount") is not None:
            merged["amount"] = _d(merged["amount"])
        if merged.get("amount_max") is not None:
            merged["amount_max"] = _d(merged["amount_max"])
        if "is_anchor" in spec:
            merged["is_anchor"] = bool(spec["is_anchor"])
        else:
            merged["is_anchor"] = bool(current.get("is_anchor"))
        if "optional" in spec:
            merged["optional"] = bool(spec["optional"])
        else:
            merged["optional"] = bool(current.get("optional"))
        if "nutrition_exclude" in spec:
            merged["nutrition_exclude"] = bool(spec["nutrition_exclude"])
        else:
            merged["nutrition_exclude"] = bool(current.get("nutrition_exclude"))
        if "nutrition_factor" in spec:
            merged["nutrition_factor"] = _d(spec.get("nutrition_factor"))
        elif "nutrition_factor" not in merged:
            merged["nutrition_factor"] = current.get("nutrition_factor")
        if merged.get("canonical_id") != old_cid:
            for field in CANON_NUTRITION_FIELDS:
                merged[field] = spec.get(field)
        else:
            for field in CANON_NUTRITION_FIELDS:
                if field in spec:
                    merged[field] = spec[field]
        out[idx] = merged
    next_pos = max((line.get("position") or 0) for line in out) + 1 if out else 0
    for spec in delta.get("add") or []:
        added = {
            "canonical_id": spec.get("canonical_id") or "",
            "name": spec.get("name") or spec.get("display_name") or spec.get("canonical_id") or "",
            "amount": _d(spec.get("amount")),
            "amount_max": _d(spec.get("amount_max")),
            "unit": spec.get("unit") or "g",
            "detail": spec.get("detail"),
            "scalable": spec.get("scalable", True),
            "scale_mode": spec.get("scale_mode") or "linear",
            "is_anchor": False,
            "optional": bool(spec.get("optional", False)),
            "nutrition_exclude": bool(spec.get("nutrition_exclude", False)),
            "nutrition_factor": _d(spec.get("nutrition_factor")),
            "position": spec.get("position", next_pos),
            "allergens_contains": list(
                spec.get("allergens_contains") or spec.get("contains") or []
            ),
            "allergens_may_contain": list(
                spec.get("allergens_may_contain") or spec.get("may_contain") or []
            ),
            "allergens_unknown": list(spec.get("allergens_unknown") or spec.get("unknown") or []),
        }
        for field in CANON_NUTRITION_FIELDS:
            added[field] = spec.get(field)
        next_pos = max(next_pos, int(added["position"]) + 1)
        out.append(added)
    return out


def apply_step_delta(steps: list[dict], delta: dict | None) -> list[dict]:
    if not delta:
        return [deepcopy(step) for step in steps]
    validate_step_delta(steps, delta)
    out = [deepcopy(step) for step in steps]
    for spec in delta.get("replace") or []:
        pos = spec.get("position")
        idx = None
        for i, step in enumerate(out):
            if step.get("position") == pos:
                idx = i
                break
        if idx is None:
            raise VariantError("replace: целевой шаг не найден")
        step = out[idx]
        for key in (
            "text",
            "timer_seconds",
            "timer_label",
            "timer_note",
            "pull_internal_temperature_c",
            "target_internal_temperature_c",
            "hold_seconds",
        ):
            if key in spec:
                step[key] = spec[key]
    for spec in delta.get("insert") or []:
        after = spec.get("after_position", len(out))
        inserted = {
            "position": -1,
            "text": spec.get("text") or "",
            "timer_seconds": spec.get("timer_seconds"),
            "timer_label": spec.get("timer_label"),
            "timer_note": spec.get("timer_note"),
            "pull_internal_temperature_c": spec.get("pull_internal_temperature_c"),
            "target_internal_temperature_c": spec.get("target_internal_temperature_c"),
            "hold_seconds": spec.get("hold_seconds"),
        }
        insert_at = 0 if after == 0 else len(out)
        for i, step in enumerate(out):
            if step.get("position") == after:
                insert_at = i + 1
                break
        out.insert(insert_at, inserted)
    for i, step in enumerate(out):
        step["position"] = i
    return out


def apply_allergen_delta(base: dict[str, list[str]], delta: dict | None) -> dict[str, list[str]]:
    if not delta:
        return {
            "contains": list(base.get("contains") or []),
            "may_contain": list(base.get("may_contain") or []),
            "unknown": list(base.get("unknown") or []),
        }
    contains = set(base.get("contains") or [])
    may_contain = set(base.get("may_contain") or [])
    unknown = set(base.get("unknown") or [])
    contains.update(delta.get("contains_add") or [])
    contains -= set(delta.get("contains_remove") or [])
    may_contain.update(delta.get("may_contain_add") or [])
    may_contain -= set(delta.get("may_contain_remove") or [])
    unknown.update(delta.get("unknown_add") or [])
    unknown -= set(delta.get("unknown_remove") or [])
    return merge_allergen_lists(
        [(sorted(contains), sorted(may_contain), sorted(unknown))]
    )


def allergens_from_lines(lines: list[dict]) -> dict[str, list[str]]:
    """Required lines only. Garnish / «для подачи» do not mark the dish."""
    rows = (
        (
            list(line.get("allergens_contains") or []),
            list(line.get("allergens_may_contain") or []),
            list(line.get("allergens_unknown") or []),
        )
        for line in lines
        if not line.get("optional")
    )
    return merge_allergen_lists(rows)


def apply_high_risk(base_flags: list[str], delta: dict | None) -> list[str]:
    flags = set(base_flags or [])
    if delta:
        flags.update(delta.get("add") or [])
        flags -= set(delta.get("remove") or [])
    return sorted(flags)


def count_anchors(lines: list[dict]) -> int:
    return sum(1 for line in lines if line.get("is_anchor"))


def pick_anchor(lines: list[dict]) -> dict | None:
    hits = [line for line in lines if line.get("is_anchor")]
    if len(hits) > 1:
        raise VariantError("После сборки больше одного якоря.")
    return hits[0] if hits else None


@dataclass
class AssembledRecipe:
    ingredients: list[dict]
    steps: list[dict]
    allergens: dict[str, list[str]]
    high_risk_flags: list[str]
    caution_text: str | None
    cook_method: str
    protein_base: str
    equipment: str | None
    applied_axes: dict[str, str | None]
    available_variants: list[dict]
    available_equipment: list[str]
    variations: list[dict]
    notes: list[dict]
    prep: list
    has_delta_variants: bool = False
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class VariantData:
    code: str
    title: str
    axis: str
    has_delta: bool
    legacy_text: str | None = None
    ingredient_delta: dict | None = None
    step_delta: dict | None = None
    allergen_delta: dict | None = None
    high_risk_delta: dict = field(default_factory=dict)
    cook_method_override: str | None = None
    protein_base_override: str | None = None
    equipment: str | None = None
    caution_text_override: str | None = None


@dataclass(frozen=True, slots=True)
class VariantSelection:
    variant_code: str | None = None
    equipment_code: str | None = None


@dataclass(frozen=True, slots=True)
class RecipeReadModel:
    slug: str
    protein_base: str
    cook_method: str
    equipment: str | None
    high_risk_flags: tuple[str, ...]
    caution_text: str | None
    ingredients: tuple[dict, ...]
    steps: tuple[dict, ...]
    variants: tuple[VariantData, ...]
    notes: tuple
    prep: tuple


def _variant_data(item) -> VariantData:
    if isinstance(item, VariantData):
        return item
    return VariantData(
        code=item.code,
        title=item.title,
        axis=item.axis,
        has_delta=bool(item.has_delta),
        legacy_text=item.legacy_text,
        ingredient_delta=item.ingredient_delta,
        step_delta=item.step_delta,
        allergen_delta=item.allergen_delta,
        high_risk_delta=item.high_risk_delta or {},
        cook_method_override=getattr(item, "cook_method_override", None),
        protein_base_override=getattr(item, "protein_base_override", None),
        equipment=getattr(item, "equipment", None),
        caution_text_override=getattr(item, "caution_text_override", None),
    )


def _variant_payload(item) -> dict:
    data = _variant_data(item)
    return {
        "code": data.code,
        "title": data.title,
        "axis": data.axis,
        "has_delta": data.has_delta,
        "legacy_text": data.legacy_text,
        "ingredient_delta": data.ingredient_delta,
        "step_delta": data.step_delta,
        "allergen_delta": data.allergen_delta,
        "high_risk_delta": data.high_risk_delta or {},
        "cook_method_override": data.cook_method_override,
        "protein_base_override": data.protein_base_override,
        "equipment": data.equipment,
        "caution_text_override": data.caution_text_override,
    }


def available_equipment_codes(recipe, variants: list) -> list[str]:
    codes: list[str] = []
    if recipe.equipment:
        codes.append(recipe.equipment)
    for item in variants:
        if item.axis != "equipment" or not item.has_delta:
            continue
        code = item.equipment or item.code
        if code and code not in codes:
            codes.append(code)
    return codes


def resolve_axes(
    *,
    recipe,
    variants: list,
    variant_code: str | None,
    equipment_code: str | None,
) -> tuple[Any | None, Any | None, str | None]:
    addons = [item for item in variants if item.axis == "addon"]
    addon = None
    if variant_code:
        addon = next((item for item in addons if item.code == variant_code), None)
        if addon is None:
            raise VariantError(f"Неизвестный код variant: {variant_code}")

    available = available_equipment_codes(recipe, variants)
    applied_equipment = recipe.equipment
    equipment_variant = None
    if equipment_code:
        # Family axis, not VOCAB equipment-only: air_fryer / steam live here
        # as cook_method codes with no vessel field (VOCAB, overlay axes).
        if equipment_code not in available:
            raise VariantError(f"Неизвестный код equipment: {equipment_code}")
        applied_equipment = equipment_code
        if equipment_code != recipe.equipment:
            equipment_variant = next(
                (
                    item
                    for item in variants
                    if item.axis == "equipment"
                    and item.has_delta
                    and (item.equipment or item.code) == equipment_code
                ),
                None,
            )
            if equipment_variant is None:
                raise VariantError(f"Неизвестный код equipment: {equipment_code}")
    return addon, equipment_variant, applied_equipment


def assemble_display(
    *,
    base_lines: list[dict],
    base_steps: list[dict],
    base_allergens: dict[str, list[str]],
    base_flags: list[str],
    base_caution: str | None,
    base_cook_method: str,
    base_protein_base: str,
    addon: dict | None,
    equipment: dict | None,
) -> tuple[list[dict], list[dict], dict[str, list[str]], list[str], str | None, str, str]:
    lines = [_copy_line(line) for line in base_lines]
    steps = [deepcopy(step) for step in base_steps]
    flags = list(base_flags or [])
    caution = base_caution
    cook_method = base_cook_method
    protein_base = base_protein_base
    allergen_deltas: list[dict] = []

    for axis in (addon, equipment):
        if not axis or not axis.get("has_delta"):
            continue
        lines = apply_ingredient_delta(lines, axis.get("ingredient_delta"))
        if steps:
            steps = apply_step_delta(steps, axis.get("step_delta"))
        flags = apply_high_risk(flags, axis.get("high_risk_delta"))
        if axis.get("allergen_delta"):
            allergen_deltas.append(axis["allergen_delta"])
        if axis.get("cook_method_override"):
            cook_method = axis["cook_method_override"]
        if axis.get("protein_base_override"):
            protein_base = axis["protein_base_override"]
        if axis.get("caution_text_override"):
            caution = axis["caution_text_override"]

    if count_anchors(lines) > 1:
        raise VariantError("После сборки больше одного якоря.")

    allergens = allergens_from_lines(lines)
    for delta in allergen_deltas:
        allergens = apply_allergen_delta(allergens, delta)
    return lines, steps, allergens, flags, caution, cook_method, protein_base


def build_read_model(recipe, *, include_nutrition: bool = True) -> RecipeReadModel:
    """Snapshot a prefetched Recipe into an in-memory read model (no extra queries)."""
    notes = recipe.notes if isinstance(recipe.notes, list) else []
    prep = recipe.prep if isinstance(recipe.prep, list) else []
    return RecipeReadModel(
        slug=getattr(recipe, "slug", "") or "",
        protein_base=recipe.protein_base,
        cook_method=recipe.cook_method,
        equipment=recipe.equipment,
        high_risk_flags=tuple(recipe.high_risk_flags or []),
        caution_text=recipe.caution_text,
        ingredients=tuple(lines_from_recipe(recipe, include_nutrition=include_nutrition)),
        steps=tuple(steps_from_recipe(recipe)),
        variants=tuple(_variant_data(item) for item in recipe.variants.all()),
        notes=tuple(notes),
        prep=tuple(prep),
    )


def assemble(
    read_model: RecipeReadModel,
    selection: VariantSelection | None = None,
) -> AssembledRecipe:
    """Pure assemble from a read model. No ORM."""
    selection = selection or VariantSelection()
    variants = list(read_model.variants)
    host = SimpleNamespace(equipment=read_model.equipment)
    addon_obj, equipment_obj, applied_equipment = resolve_axes(
        recipe=host,
        variants=variants,
        variant_code=selection.variant_code,
        equipment_code=selection.equipment_code,
    )
    addon = _variant_payload(addon_obj) if addon_obj else None
    equipment = _variant_payload(equipment_obj) if equipment_obj else None
    lines, steps, allergens, flags, caution, cook_method, protein_base = assemble_display(
        base_lines=list(read_model.ingredients),
        base_steps=list(read_model.steps),
        base_allergens={},
        base_flags=list(read_model.high_risk_flags),
        base_caution=read_model.caution_text,
        base_cook_method=read_model.cook_method,
        base_protein_base=read_model.protein_base,
        addon=addon,
        equipment=equipment,
    )
    addons = [item for item in variants if item.axis == "addon"]
    return AssembledRecipe(
        ingredients=lines,
        steps=steps,
        allergens=allergens,
        high_risk_flags=flags,
        caution_text=caution,
        cook_method=cook_method,
        protein_base=protein_base,
        equipment=applied_equipment,
        applied_axes={
            "variant": addon_obj.code if addon_obj else None,
            "equipment": applied_equipment,
        },
        available_variants=[
            {
                "code": item.code,
                "title": item.title,
                "axis": "addon",
                "has_delta": bool(item.has_delta),
                "protein_base": getattr(item, "protein_base_override", None),
            }
            for item in addons
        ],
        available_equipment=available_equipment_codes(host, variants),
        variations=[
            {"title": item.title, "text": item.legacy_text or ""}
            for item in addons
            if not item.has_delta
        ],
        notes=list(read_model.notes),
        prep=list(read_model.prep),
        has_delta_variants=any(item.has_delta for item in addons),
    )


def assemble_recipe(
    recipe,
    *,
    variant_code: str | None = None,
    equipment_code: str | None = None,
    enrich: bool = True,
) -> AssembledRecipe:
    read_model = build_read_model(recipe, include_nutrition=enrich)
    assembled = assemble(
        read_model,
        VariantSelection(variant_code=variant_code, equipment_code=equipment_code),
    )
    if enrich:
        assembled.ingredients = enrich_lines_from_db(assembled.ingredients)
    return assembled


def catalog_allergens(recipe) -> dict[str, list[str]]:
    """Worst case: base ∪ every addon with a real delta."""
    base_lines = allergen_lines_from_recipe(recipe)
    merged = [allergens_from_lines(base_lines)]
    for item in recipe.variants.all():
        if item.axis != "addon" or not item.has_delta:
            continue
        payload = _variant_payload(item)
        try:
            lines, _steps, allergens, _flags, _caution, _method, _protein = assemble_display(
                base_lines=base_lines,
                base_steps=[],
                base_allergens={},
                base_flags=[],
                base_caution=None,
                base_cook_method=recipe.cook_method,
                base_protein_base=recipe.protein_base,
                addon=payload,
                equipment=None,
            )
        except VariantError:
            continue
        merged.append(allergens)
        merged.append(allergens_from_lines(lines))
    rows = (
        (
            item.get("contains") or [],
            item.get("may_contain") or [],
            item.get("unknown") or [],
        )
        for item in merged
    )
    return merge_allergen_lists(rows)


def catalog_cook_methods(recipe) -> list[str]:
    ordered: list[str] = []

    def add(code: str | None) -> None:
        if code and code not in ordered:
            ordered.append(code)

    add(getattr(recipe, "cook_method", None))
    for item in recipe.variants.all():
        if getattr(item, "axis", None) != "equipment" or not getattr(item, "has_delta", False):
            continue
        add(getattr(item, "cook_method_override", None))
    return ordered


def catalog_protein_bases(recipe) -> list[str]:
    ordered: list[str] = []

    def add(code: str | None) -> None:
        if code and code not in ordered:
            ordered.append(code)

    add(getattr(recipe, "protein_base", None))
    for code in getattr(recipe, "protein_bases_extra", None) or []:
        add(code)
    for item in recipe.variants.all():
        if getattr(item, "axis", None) != "addon" or not getattr(item, "has_delta", False):
            continue
        add(getattr(item, "protein_base_override", None))
    return ordered


def catalog_protein_variants(recipe) -> list[dict]:
    rows: list[dict] = []
    for item in recipe.variants.all():
        if getattr(item, "axis", None) != "addon" or not getattr(item, "has_delta", False):
            continue
        override = getattr(item, "protein_base_override", None)
        if not override:
            continue
        rows.append(
            {"code": item.code, "title": item.title, "protein_base": override}
        )
    return rows
