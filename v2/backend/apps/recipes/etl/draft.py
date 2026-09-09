"""Validate and parse V2 recipe draft JSON (overlay / waves). No LLM."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from apps.recipes.constants import (
    ADAPTATION_TYPE,
    ALLERGEN,
    COOK_METHOD,
    CUT,
    DISH_TYPE,
    ENERGY_PROFILE,
    EQUIPMENT,
    HIGH_RISK,
    MAX_VARIANTS,
    PROTEIN_BASE,
    SCALE_MODE,
    UNIT,
    USE_CASE,
    VARIANT_AXIS,
    YIELD_KIND,
)
from apps.recipes.etl.taxonomy import TEMP_REQUIRED_SLUGS

FORBIDDEN_METHOD_ALIASES = frozenset({"duhovka", "skovoroda", "kastryulya", "tushenie"})
FORBIDDEN_URL_NEEDLES = ("sol-chef.ru",)
MANUAL_CANONICALS = frozenset(
    {"baking_soda", "yeast", "dry_yeast", "gelatin", "baking_powder"}
)
WEIGHT_VOLUME = frozenset({"g", "kg", "ml", "l"})
ALLERGEN_DELTA_KEYS = (
    "contains_add",
    "contains_remove",
    "may_contain_add",
    "may_contain_remove",
    "unknown_add",
    "unknown_remove",
)
EMPTY_ALLERGEN_DELTA = {key: [] for key in ALLERGEN_DELTA_KEYS}
FORBIDDEN_RECIPE_NUTRITION_KEYS = frozenset(
    {
        "kcal",
        "nutrition",
        "protein_g",
        "fat_g",
        "carbs_g",
        "per_serving",
        "per_100g_cooked",
        "per_100g_input",
    }
)

MIN_NOTES_OVERLAY = 3
MAX_NOTES = 10
LINE_ALLERGEN_KEYS = (
    "allergens_contains",
    "allergens_may_contain",
    "allergens_unknown",
)


class DraftError(Exception):
    pass


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise DraftError(f"Нет файла {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DraftError(f"{path.name}: не JSON ({exc})") from exc
    if not isinstance(payload, dict):
        raise DraftError(f"{path.name}: нужен объект рецепта, не массив")
    return payload


def validate_draft(
    raw: dict,
    *,
    overlay: bool = True,
    known_ingredients: dict[str, dict] | None = None,
) -> list[str]:
    errors: list[str] = []
    slug = (raw.get("id") or raw.get("slug") or "").strip()
    if not slug:
        errors.append("Нет id/slug")
        slug = "?"

    def err(msg: str) -> None:
        errors.append(f"{slug}: {msg}")

    title = (raw.get("title") or "").strip()
    if not title:
        err("нет title")
    if raw.get("editorial_tested") is True:
        err("агент не ставит editorial_tested")
    if raw.get("tags") or raw.get("category"):
        err("tags/category — поля V1, не писать")
    for key in FORBIDDEN_RECIPE_NUTRITION_KEYS:
        if key in raw:
            err(f"ключ {key} на рецепте запрещён")

    _enum("protein_base", raw.get("protein_base"), PROTEIN_BASE, err)
    _enum("cook_method", raw.get("cook_method"), COOK_METHOD, err)
    if raw.get("cook_method") in FORBIDDEN_METHOD_ALIASES:
        err("cook_method V1-алиас запрещён")
    _enum("dish_type", raw.get("dish_type"), DISH_TYPE, err)
    if raw.get("dish_type") in {"pan_fry", "stew", "oven", "grill"}:
        err("dish_type не кодирует способ готовки")
    equipment = raw.get("equipment")
    if equipment is not None and equipment != "":
        _enum("equipment", equipment, EQUIPMENT, err)
    energy = raw.get("energy_profile") or "standard"
    _enum("energy_profile", energy, ENERGY_PROFILE, err)
    if raw.get("scale_mode"):
        _enum("scale_mode", raw.get("scale_mode"), SCALE_MODE, err)
    if raw.get("scale_mode") == "fixed":
        err("scale_mode=fixed нет; это scalable=false")
    _check_yield(raw, err)

    if overlay:
        _check_overlay_profile(raw, err)
        _check_adaptations(raw.get("adaptations"), err)

    if "prep" in raw:
        prep = raw.get("prep")
        if not isinstance(prep, list):
            err("prep должен быть списком {text}")
        elif not prep:
            err("пустой prep — уберите ключ")
        else:
            for index, item in enumerate(prep):
                if not isinstance(item, dict) or not str(item.get("text") or "").strip():
                    err(f"prep[{index}]: нужен text")

    for cut in raw.get("allowed_cuts") or []:
        if cut not in CUT:
            err(f"неизвестный cut {cut!r}")

    url = (raw.get("source_url") or "").strip()
    for needle in FORBIDDEN_URL_NEEDLES:
        if needle in url.lower():
            err("циклический source_url (sol-chef.ru) — Critical")

    flags = raw.get("high_risk_flags") or []
    for flag in flags:
        if flag not in HIGH_RISK:
            err(f"неизвестный high-risk {flag!r}")
    if flags and not (raw.get("caution_text") or "").strip():
        err("high-risk без caution_text")

    notes = raw.get("notes")
    if not isinstance(notes, list):
        err("notes должен быть списком {title,text}")
        notes = []
    titled = 0
    for item in notes:
        if not isinstance(item, dict) or not str(item.get("text") or "").strip():
            err("пустой пункт notes")
            continue
        if item.get("title"):
            titled += 1
    if overlay:
        if len(notes) < MIN_NOTES_OVERLAY:
            err(f"оверлей: notes меньше {MIN_NOTES_OVERLAY}")
        if len(notes) > MAX_NOTES:
            err(f"notes больше {MAX_NOTES}")

    lines = raw.get("ingredients")
    if not isinstance(lines, list) or not lines:
        err("нет ingredients")
        lines = []
    positions: set[int] = set()
    anchors = 0
    weight_lines = 0
    canons: dict[str, dict] = {}
    known = dict(known_ingredients or {})
    for extra in raw.get("new_ingredients") or []:
        if not isinstance(extra, dict) or not extra.get("canonical_id"):
            err("new_ingredients: нужен canonical_id")
            continue
        cid = extra["canonical_id"]
        if cid in known:
            err(f"new_ingredients {cid}: канон уже в реестре — уберите заявку")
        canons[cid] = extra
        for key in ("allergens_contains", "allergens_may_contain", "allergens_unknown"):
            for code in extra.get(key) or extra.get(key.replace("allergens_", "")) or []:
                if code not in ALLERGEN:
                    err(f"new_ingredients {cid}: аллерген {code!r}")

    for index, line in enumerate(lines):
        if not isinstance(line, dict):
            err(f"ингредиент {index} не объект")
            continue
        cid = (line.get("canonical_id") or "").strip()
        if not cid:
            err(f"ингредиент {index}: нет canonical_id")
        unit = line.get("unit")
        if unit not in UNIT:
            err(f"{cid or index}: unit {unit!r} не из VOCAB")
        if unit in {"cup", "стакан", "стакана"}:
            err(f"{cid}: стакан/cup запрещён")
        pos = line.get("position", index)
        try:
            pos = int(pos)
        except (TypeError, ValueError):
            err(f"{cid}: position не число")
            pos = index
        if pos in positions:
            err(f"дубль position ингредиента {pos}")
        positions.add(pos)
        mode = line.get("scale_mode") or "linear"
        if mode not in SCALE_MODE:
            err(f"{cid}: scale_mode {mode!r}")
        if cid in MANUAL_CANONICALS and mode == "gentle":
            err(f"{cid}: сода/дрожжи/желатин — не gentle; linear или manual")
        scalable = bool(line.get("scalable", True))
        amount = line.get("amount")
        if unit in {"to_taste", "pinch"}:
            if amount is not None:
                err(f"{cid}: to_taste/pinch — amount null")
            if scalable:
                err(f"{cid}: to_taste/pinch — scalable=false")
        if line.get("is_anchor"):
            anchors += 1
            if unit not in WEIGHT_VOLUME or amount is None:
                err(f"{cid}: якорь только с количеством г/мл/кг/л")
        if scalable and unit in WEIGHT_VOLUME and amount is not None:
            weight_lines += 1
        if "timer_min" in line:
            err("timer_min у ингредиента")
        for key in LINE_ALLERGEN_KEYS:
            if key in line:
                err(f"{cid}: аллергены только в реестре Ingredient, не в строке рецепта")
        _check_line_nutrition(line, cid, err)

    if anchors > 1:
        err("больше одного is_anchor")
    if overlay and anchors == 0 and raw.get("servings") is None and weight_lines:
        err("нет якоря и нет servings — граммовка на сайте выключена")

    steps = raw.get("steps")
    if not isinstance(steps, list) or not steps:
        err("нет steps")
        steps = []
    step_pos: set[int] = set()
    targets: set[int] = set()
    pan_note = False
    for index, step in enumerate(steps):
        if isinstance(step, str):
            err(f"шаг {index}: строка запрещена, нужен объект")
            continue
        if not isinstance(step, dict):
            err(f"шаг {index}: не объект")
            continue
        if not str(step.get("text") or "").strip():
            err(f"шаг {index}: пустой text")
        if step.get("timer_min") is not None:
            err(f"шаг {index}: timer_min — пишите timer_seconds")
        pos = step.get("position", index)
        try:
            pos = int(pos)
        except (TypeError, ValueError):
            err(f"шаг {index}: position не число")
            pos = index
        if pos in step_pos:
            err(f"дубль position шага {pos}")
        step_pos.add(pos)
        pull = step.get("pull_internal_temperature_c")
        target = step.get("target_internal_temperature_c")
        hold = step.get("hold_seconds")
        if pull is not None and target is None:
            err(f"шаг {pos}: pull без target")
        if target is not None:
            try:
                targets.add(int(target))
            except (TypeError, ValueError):
                err(f"шаг {pos}: target не число")
        text = (step.get("text") or "").lower()
        note = (step.get("equipment_note") or "").lower()
        if "порци" in text or "не перегруз" in text or "не перегруз" in note or "порци" in note:
            pan_note = True
        if step.get("equipment_note"):
            pan_note = True
        if hold is not None and int(hold) < 0:
            err(f"шаг {pos}: hold отрицательный")

    cook = raw.get("cook_method")
    protein = raw.get("protein_base")
    cuts = set(raw.get("allowed_cuts") or [])
    if cook == "pan_fry" and protein in {"beef", "pork", "poultry", "lamb"} and not pan_note:
        err("pan_fry мяса: в шаге жарки нужна оговорка не перегружать сковороду")
    if protein == "poultry":
        if "whole_bird" in cuts:
            if not ({72, 82} <= targets):
                err("целая птица: нужны target 72 и 82")
        elif "drumstick" in cuts:
            if not targets or max(targets) < 82:
                err("голень птицы на кости: target не ниже 82")
        elif "thigh" in cuts:
            if not targets or max(targets) < 74:
                err("бедро птицы: target не ниже 74 (без кости); на кости — 82")
        elif "breast" in cuts:
            if not targets or max(targets) < 72:
                err("грудка птицы: target не ниже 72")
        elif not targets:
            err("птица: нет target_internal_temperature_c")
    elif protein in {"fish_white_sea", "fish_red_sea", "fish_river"}:
        if "raw_fish" not in flags and (not targets or min(targets) < 63):
            err("готовая рыба: target не ниже 63")
    elif protein == "pork" and "mince" not in cuts:
        if not targets:
            err("свинина: нет target")
        else:
            t = min(targets)
            holds = [
                int(s.get("hold_seconds") or 0)
                for s in steps
                if isinstance(s, dict) and s.get("hold_seconds") is not None
            ]
            ok = t >= 71 or (t >= 63 and (max(holds) if holds else 0) >= 180)
            if not ok:
                err("свинина: 63 °C + hold ≥ 180 с или 71 °C")
    elif slug in TEMP_REQUIRED_SLUGS and not targets:
        err("нет target_internal_temperature_c (SAFETY)")

    variants = raw.get("variants") or raw.get("variations") or []
    if raw.get("variations") and not raw.get("variants"):
        for item in raw.get("variations") or []:
            if isinstance(item, dict) and item.get("text") and not item.get("has_delta"):
                err("variations[].text без дельты — для оверлея запрещено")
    codes: set[str] = set()
    for item in variants:
        if not isinstance(item, dict):
            err("вариант не объект")
            continue
        axis = item.get("axis") or "addon"
        if axis not in VARIANT_AXIS:
            err(f"axis {axis!r} не addon/equipment/energy")
        code = (item.get("code") or "").strip()
        if not code:
            err("вариант без code")
        if code in codes:
            err(f"дубль variant code {code}")
        codes.add(code)
        if axis == "energy" and code not in {"light", "rich"}:
            err(f"energy code {code!r} — только light/rich")
        has_delta = bool(item.get("has_delta"))
        ing = item.get("ingredient_delta")
        step_delta = item.get("step_delta")
        if item.get("text") and not has_delta:
            err(f"{code}: текстовая вариация без has_delta")
        if has_delta:
            if not ing and not step_delta:
                err(f"{code}: has_delta без ingredient_delta/step_delta")
            if ing is not None:
                _check_allergen_delta(item.get("allergen_delta"), err, code)
                _check_delta_nutrition(ing, err, code)
        if item.get("cook_method_override"):
            _enum("cook_method_override", item.get("cook_method_override"), COOK_METHOD, err)
        if item.get("equipment"):
            _enum("variant.equipment", item.get("equipment"), EQUIPMENT, err)

    if overlay and len(variants) > MAX_VARIANTS:
        err(f"вариантов больше {MAX_VARIANTS}")

    if overlay and known_ingredients is not None:
        registry = set(known_ingredients) | set(canons)
        for cid in _draft_canonicals(raw):
            if cid and cid not in registry:
                err(f"нет канона {cid} (реестр или new_ingredients)")

    return errors


def _enum(name: str, value, allowed: frozenset[str], err) -> None:
    if value not in allowed:
        err(f"{name}={value!r} не из VOCAB")


def _check_overlay_profile(raw: dict, err) -> None:
    profile = raw.get("time_profile")
    total = None
    active = None
    if isinstance(profile, dict):
        total = profile.get("total_minutes")
        active = profile.get("active_minutes")
    else:
        total = raw.get("time_minutes")
        active = raw.get("active_minutes")
    if total is None or active is None:
        err("оверлей: нужен time_profile {total_minutes, active_minutes}")
    else:
        try:
            total_i = int(total)
            active_i = int(active)
        except (TypeError, ValueError):
            err("time_profile: минуты — целые")
        else:
            if total_i < 1 or active_i < 0:
                err("time_profile: total ≥ 1, active ≥ 0")
            elif active_i > total_i:
                err("active_minutes больше total_minutes")
    effort = raw.get("effort_level", raw.get("effort"))
    washing = raw.get("washing_level", raw.get("washing"))
    for name, value in (("effort_level", effort), ("washing_level", washing)):
        if value is None:
            err(f"оверлей: нужен {name} 1–5")
            continue
        try:
            level = int(value)
        except (TypeError, ValueError):
            err(f"{name} должен быть 1–5")
            continue
        if not 1 <= level <= 5:
            err(f"{name} должен быть 1–5")
    cases = raw.get("use_cases")
    if not isinstance(cases, list):
        err("use_cases должен быть списком (можно [])")
        return
    seen: set[str] = set()
    for code in cases:
        if code not in USE_CASE:
            err(f"use_case {code!r} не из VOCAB")
        elif code in seen:
            err(f"дубль use_case {code}")
        seen.add(code)


def _check_adaptations(adaptations, err) -> None:
    if adaptations is None:
        err("оверлей: нужен adaptations (можно [])")
        return
    if not isinstance(adaptations, list):
        err("adaptations должен быть списком")
        return
    for index, item in enumerate(adaptations):
        if not isinstance(item, dict):
            err(f"adaptation[{index}] не объект")
            continue
        kind = item.get("type")
        if kind not in ADAPTATION_TYPE:
            err(f"adaptation[{index}]: type {kind!r}")
            continue
        quality = item.get("quality")
        if quality is not None:
            try:
                q = float(quality)
            except (TypeError, ValueError):
                err(f"adaptation[{index}]: quality не число")
            else:
                if not 0 <= q <= 1:
                    err(f"adaptation[{index}]: quality 0–1")
        if kind == "substitution":
            if not item.get("from") or not item.get("to"):
                err(f"adaptation[{index}]: substitution нужен from и to")
        elif kind == "omission":
            if not item.get("ingredient"):
                err(f"adaptation[{index}]: omission нужен ingredient")
        else:
            src = item.get("from")
            dest = item.get("to")
            if not src or not dest:
                err(f"adaptation[{index}]: {kind} нужен from и to")
            elif kind == "equipment":
                if src not in EQUIPMENT:
                    err(f"adaptation[{index}]: from {src!r} не equipment")
                if dest not in EQUIPMENT:
                    err(f"adaptation[{index}]: to {dest!r} не equipment")
            elif kind == "method":
                if src not in COOK_METHOD:
                    err(f"adaptation[{index}]: from {src!r} не cook_method")
                if dest not in COOK_METHOD:
                    err(f"adaptation[{index}]: to {dest!r} не cook_method")


def _draft_canonicals(raw: dict) -> set[str]:
    found: set[str] = set()
    for line in raw.get("ingredients") or []:
        if isinstance(line, dict) and line.get("canonical_id"):
            found.add(line["canonical_id"])
    for item in raw.get("variants") or raw.get("variations") or []:
        if not isinstance(item, dict):
            continue
        delta = item.get("ingredient_delta") or {}
        if not isinstance(delta, dict):
            continue
        for spec in [*(delta.get("add") or []), *(delta.get("replace") or [])]:
            if isinstance(spec, dict) and spec.get("canonical_id"):
                found.add(spec["canonical_id"])
    return found


def _check_yield(raw: dict, err) -> None:
    kind = raw.get("yield_kind")
    if kind is not None and kind != "":
        _enum("yield_kind", kind, YIELD_KIND, err)
    weight = raw.get("yield_weight_g")
    if weight is None or weight == "":
        if kind:
            err("yield_kind без yield_weight_g")
        return
    try:
        value = Decimal(str(weight))
    except (InvalidOperation, TypeError, ValueError):
        err("yield_weight_g не число")
        return
    if value <= 0:
        err("yield_weight_g должен быть > 0")


def _check_line_nutrition(line: dict, cid: str, err) -> None:
    if "nutrition_exclude" in line and not isinstance(line.get("nutrition_exclude"), bool):
        err(f"{cid}: nutrition_exclude должен быть bool")
    if line.get("nutrition_exclude") and line.get("nutrition_factor") is not None:
        err(f"{cid}: nutrition_factor не вместе с nutrition_exclude")
    if "nutrition_factor" in line and line.get("nutrition_factor") is not None:
        try:
            factor = Decimal(str(line.get("nutrition_factor")))
        except (InvalidOperation, TypeError, ValueError):
            err(f"{cid}: nutrition_factor не число")
            return
        if not (Decimal("0.01") <= factor <= Decimal("1")):
            err(f"{cid}: nutrition_factor должен быть 0.01–1")


def _check_delta_nutrition(delta, err, code: str) -> None:
    if not isinstance(delta, dict):
        return
    for spec in [*(delta.get("add") or []), *(delta.get("replace") or [])]:
        if not isinstance(spec, dict):
            continue
        cid = (spec.get("canonical_id") or "").strip() or f"{code}:delta"
        _check_line_nutrition(spec, cid, err)


def _check_allergen_delta(delta, err, code: str) -> None:
    if not isinstance(delta, dict):
        err(f"{code}: ingredient_delta требует allergen_delta")
        return
    for key in ALLERGEN_DELTA_KEYS:
        for item in delta.get(key) or []:
            if item not in ALLERGEN:
                err(f"{code}: allergen_delta {key} код {item!r}")


def _dec(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DraftError(f"Некорректное число {value!r}") from exc


def parse_draft(raw: dict, *, known_ingredients: dict[str, dict] | None) -> dict:
    errors = validate_draft(raw, overlay=True, known_ingredients=known_ingredients)
    if errors:
        extra = f" (+{len(errors) - 12})" if len(errors) > 12 else ""
        raise DraftError("; ".join(errors[:12]) + extra)
    slug = (raw.get("id") or raw.get("slug") or "").strip()
    known = dict(known_ingredients or {})
    new_canons: list[dict] = []
    for extra in raw.get("new_ingredients") or []:
        cid = extra["canonical_id"]
        row = {
            "canonical_id": cid,
            "title": extra.get("title") or extra.get("display_name") or cid,
            "aliases": extra.get("aliases") or [],
            "contains": extra.get("allergens_contains") or extra.get("contains") or [],
            "may_contain": extra.get("allergens_may_contain") or extra.get("may_contain") or [],
            "unknown": extra.get("allergens_unknown") or extra.get("unknown") or [],
        }
        known[cid] = row
        new_canons.append(row)

    lines = []
    titles = []
    for index, line in enumerate(raw["ingredients"]):
        cid = line["canonical_id"]
        meta = known.get(cid)
        if meta is None:
            raise DraftError(f"{slug}: нет канона {cid} (сид или new_ingredients)")
        unit = line["unit"]
        amount = _dec(line.get("amount"))
        amount_max = _dec(line.get("amount_max"))
        scalable = bool(line.get("scalable", True))
        if unit in {"to_taste", "pinch"}:
            amount = None
            amount_max = None
            scalable = False
        display = line.get("display_name") or meta.get("title") or cid
        titles.append(display)
        lines.append(
            {
                "canonical_id": cid,
                "ingredient_title": meta.get("title") or display,
                "aliases": meta.get("aliases") or [],
                "contains": meta.get("contains") or [],
                "may_contain": meta.get("may_contain") or [],
                "unknown": meta.get("unknown") or [],
                "position": int(line.get("position", index)),
                "amount": amount,
                "amount_max": amount_max,
                "unit": unit,
                "detail": line.get("detail"),
                "scale_mode": line.get("scale_mode") or "linear",
                "scalable": scalable,
                "is_anchor": bool(line.get("is_anchor")),
                "optional": bool(line.get("optional", False)),
                "nutrition_exclude": bool(line.get("nutrition_exclude", False)),
                "nutrition_factor": _dec(line.get("nutrition_factor")),
                "choice_group": line.get("choice_group"),
                "display_name": display,
            }
        )

    steps = []
    for index, step in enumerate(raw["steps"]):
        pull = step.get("pull_internal_temperature_c")
        target = step.get("target_internal_temperature_c")
        hold = step.get("hold_seconds")
        steps.append(
            {
                "position": int(step.get("position", index)),
                "text": step["text"],
                "timer_seconds": step.get("timer_seconds"),
                "timer_label": step.get("timer_label"),
                "timer_note": step.get("timer_note"),
                "pull_internal_temperature_c": int(pull) if pull is not None else None,
                "target_internal_temperature_c": int(target) if target is not None else None,
                "hold_seconds": int(hold) if hold is not None else None,
                "equipment_note": step.get("equipment_note"),
            }
        )

    variants = []
    for item in raw.get("variants") or []:
        allergen = item.get("allergen_delta")
        if item.get("has_delta") and item.get("ingredient_delta") is not None and allergen is None:
            allergen = dict(EMPTY_ALLERGEN_DELTA)
        variants.append(
            {
                "axis": item.get("axis") or "addon",
                "code": item["code"],
                "title": item["title"],
                "has_delta": bool(item.get("has_delta")),
                "legacy_text": item.get("legacy_text"),
                "ingredient_delta": item.get("ingredient_delta"),
                "step_delta": item.get("step_delta"),
                "allergen_delta": allergen,
                "high_risk_delta": item.get("high_risk_delta") or {"add": [], "remove": []},
                "cook_method_override": item.get("cook_method_override"),
                "equipment": item.get("equipment"),
                "caution_text_override": item.get("caution_text_override"),
            }
        )

    url = (raw.get("source_url") or "").strip() or None
    profile = raw.get("time_profile") if isinstance(raw.get("time_profile"), dict) else {}
    return {
        "slug": slug,
        "title": raw["title"],
        "protein_base": raw["protein_base"],
        "cook_method": raw["cook_method"],
        "dish_type": raw["dish_type"],
        "scale_mode": raw.get("scale_mode") or "linear",
        "scalable": raw.get("scalable", True),
        "servings": raw.get("servings"),
        "yield_weight_g": _dec(raw.get("yield_weight_g")),
        "yield_kind": (raw.get("yield_kind") or None)
        or ("estimated" if raw.get("yield_weight_g") not in (None, "") else None),
        "summary": raw.get("summary"),
        "source_name": raw.get("source_name"),
        "source_url": url,
        "source_type": raw.get("source_type"),
        "high_risk_flags": raw.get("high_risk_flags") or [],
        "caution_text": raw.get("caution_text"),
        "energy_profile": raw.get("energy_profile") or "standard",
        "equipment": raw.get("equipment") or None,
        "allowed_cuts": raw.get("allowed_cuts") or [],
        "notes": raw.get("notes") or [],
        "prep": raw.get("prep") or [],
        "time_total_minutes": profile.get("total_minutes", raw.get("time_minutes")),
        "time_active_minutes": profile.get("active_minutes", raw.get("active_minutes")),
        "effort_level": raw.get("effort_level", raw.get("effort")),
        "washing_level": raw.get("washing_level", raw.get("washing")),
        "use_cases": raw.get("use_cases") or [],
        "adaptations": raw.get("adaptations") or [],
        "new_canons": new_canons,
        "ingredient_titles": " ".join(titles),
        "lines": lines,
        "steps": steps,
        "variants": variants,
        "origin": "draft",
        "status": "published",
        "raw": raw,
    }


def known_from_v1_map(ingredient_map: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in ingredient_map.values():
        cid = row["canonical_id"]
        current = out.get(cid)
        aliases = list(row.get("aliases") or [])
        if current:
            aliases = list(dict.fromkeys([*(current.get("aliases") or []), *aliases]))
        out[cid] = {
            "canonical_id": cid,
            "title": row.get("title") or cid,
            "aliases": aliases,
            "contains": row.get("contains") or [],
            "may_contain": row.get("may_contain") or [],
            "unknown": row.get("unknown") or [],
        }
    return out


def load_review(path: Path) -> dict:
    if not path.is_file():
        raise DraftError(f"Нет вердикта {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DraftError(f"{path.name}: вердикт не объект")
    return payload


def review_allows_import(review: dict) -> bool:
    return (
        review.get("verdict") == "accept"
        and review.get("cookable") is True
        and review.get("real") is not False
    )
