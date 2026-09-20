from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.content.models import ContentDocument
from apps.recipes.constants import (
    EXPECTED_CONTENT_DOCUMENTS,
    V1_FOLDER_TO_COOK_METHOD,
    V1_FOLDER_TO_EQUIPMENT,
    slugify_ru,
)
from apps.recipes.etl.ingredients import (
    infer_scale_mode,
    is_anchor_candidate,
    is_optional_line,
    map_unit_and_amount,
    parse_amount,
)
from apps.recipes.etl.load import (
    V1ImportError,
    folder_from_rel,
    load_recipe_objects,
    resolve_v1_root,
)
from apps.recipes.etl.nutrition import load_ingredient_nutrition
from apps.recipes.etl.taxonomy import (
    CAUTION_TEXT,
    POULTRY_TEMP_SLUGS,
    RECIPE_TAXONOMY,
    TEMP_REQUIRED_SLUGS,
)
from apps.recipes.etl.upsert import upsert_recipe
from apps.recipes.models import Recipe
from apps.recipes.services.notes import split_notes_blob
from apps.recipes.services.substitutions import upsert_substitution_rules

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"

CONTENT_SOURCES = [
    ("guide", "grains", "Крупы", "data/grains.json"),
    ("guide", "tips", "Советы", "data/tips.json"),
    ("meat", "beef", "Говядина", "data/meat-beef.json"),
    ("meat", "pork", "Свинина", "data/meat-pork.json"),
    ("meat", "poultry", "Птица", "data/meat-poultry.json"),
]


class Command(BaseCommand):
    help = "Import V1 catalog JSON into Postgres (upsert, one transaction)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print a report and write nothing.",
        )

    def handle(self, *args, **options):
        data_root = resolve_v1_root(Path(settings.V1_DATA_ROOT))
        dry_run = options["dry_run"]
        try:
            report = run_import(data_root, dry_run=dry_run)
        except V1ImportError as exc:
            raise CommandError(str(exc)) from exc
        for line in report:
            self.stdout.write(line)


def run_import(data_root: Path, *, dry_run: bool) -> list[str]:
    recipes = load_recipe_objects(data_root)
    ingredient_map = _load_json(FIXTURES / "v1_ingredient_map.json")
    temp_seed = _load_json(FIXTURES / "v1_step_temperatures.json")
    _validate_seed_coverage(recipes, ingredient_map, temp_seed)

    parsed = [_parse_recipe(rel, raw, ingredient_map, temp_seed) for rel, raw in recipes]
    unique_names = {name for _rel, raw in recipes for name in _ingredient_names(raw)}
    report = [
        f"V1_DATA_ROOT={data_root}",
        f"files={len({rel for rel, _ in recipes})}",
        f"recipes={len(parsed)}",
        f"unique_ingredient_names={len(unique_names)}",
        f"content_documents={EXPECTED_CONTENT_DOCUMENTS}",
        f"dry_run={dry_run}",
    ]
    if dry_run:
        report.append("Запись в БД пропущена.")
        return report

    skipped_overlay = 0
    with transaction.atomic():
        _upsert_content(data_root)
        for item in parsed:
            if _is_v2_overlay(item["slug"]):
                skipped_overlay += 1
                continue
            _upsert_recipe(item)
        docs = ContentDocument.objects.count()
        if docs != EXPECTED_CONTENT_DOCUMENTS:
            raise V1ImportError(
                f"ContentDocument.count={docs}, expected {EXPECTED_CONTENT_DOCUMENTS}"
            )
        load_ingredient_nutrition()
        subs = upsert_substitution_rules()
    report.append(
        f"записано recipes={Recipe.objects.count()} "
        f"skipped_overlay={skipped_overlay} "
        f"content={ContentDocument.objects.count()} substitutions={subs}"
    )
    return report


def _load_json(path: Path):
    if not path.is_file():
        raise V1ImportError(f"Нет сида {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _ingredient_names(raw: dict) -> list[str]:
    names = []
    for item in raw.get("ingredients") or []:
        if isinstance(item, dict) and item.get("name"):
            names.append(item["name"])
    return names


def _validate_seed_coverage(recipes, ingredient_map, temp_seed) -> None:
    missing_ing = []
    for _rel, raw in recipes:
        for name in _ingredient_names(raw):
            if name not in ingredient_map:
                missing_ing.append(name)
    if missing_ing:
        uniq = sorted(set(missing_ing))
        raise V1ImportError(
            "Нет ключа в v1_ingredient_map.json: " + ", ".join(uniq[:20])
            + (f" (+{len(uniq) - 20})" if len(uniq) > 20 else "")
        )
    missing_temp = sorted(TEMP_REQUIRED_SLUGS - set(temp_seed))
    if missing_temp:
        raise V1ImportError(
            "Нет сида температур для: " + ", ".join(missing_temp)
        )


def _parse_recipe(rel: str, raw: dict, ingredient_map: dict, temp_seed: dict) -> dict:
    slug = raw["id"]
    if slug not in RECIPE_TAXONOMY:
        raise V1ImportError(f"Нет taxonomy для {slug}")
    protein_base, dish_type = RECIPE_TAXONOMY[slug]
    folder = folder_from_rel(rel)
    cook_method = V1_FOLDER_TO_COOK_METHOD.get(folder)
    if not cook_method:
        raise V1ImportError(f"Неизвестная папка V1 {folder} ({rel})")
    equipment = V1_FOLDER_TO_EQUIPMENT.get(folder)

    lines = []
    anchor_index = None
    titles = []
    for position, item in enumerate(raw.get("ingredients") or []):
        if not isinstance(item, dict):
            raise V1ImportError(f"{slug}: ингредиент не объект")
        name = item.get("name") or ""
        mapped = ingredient_map[name]
        amount = parse_amount(item.get("amount"))
        amount_max = parse_amount(item.get("amount_max"))
        v1_unit = item.get("unit")
        unit, amount = map_unit_and_amount(v1_unit, amount)
        if v1_unit == "стакана" and amount_max is not None:
            amount_max = amount_max * Decimal("250")
        scalable = item.get("scalable", True)
        if unit in {"to_taste", "pinch"}:
            amount = None
            amount_max = None
            scalable = False
        if amount is None and unit not in {"to_taste", "pinch"}:
            detail = (item.get("detail") or "").lower()
            if "щепот" in detail:
                unit = "pinch"
            else:
                unit = "to_taste"
            scalable = False
        scale_mode = infer_scale_mode(name, unit, item.get("scale_mode"))
        if is_anchor_candidate(scalable, amount, unit) and anchor_index is None:
            anchor_index = position
        titles.append(mapped.get("title") or name)
        lines.append(
            {
                "canonical_id": mapped["canonical_id"],
                "ingredient_title": mapped["title"],
                "contains": mapped.get("contains") or [],
                "may_contain": mapped.get("may_contain") or [],
                "unknown": mapped.get("unknown") or [],
                "position": position,
                "amount": amount,
                "amount_max": amount_max if unit not in {"to_taste", "pinch"} else None,
                "unit": unit,
                "detail": item.get("detail"),
                "scale_mode": scale_mode,
                "scalable": bool(scalable),
                "is_anchor": False,
                "optional": is_optional_line(item.get("detail")),
                "display_name": name,
            }
        )
    if anchor_index is not None:
        lines[anchor_index]["is_anchor"] = True

    steps = _parse_steps(slug, raw.get("steps") or [], temp_seed)
    if slug in TEMP_REQUIRED_SLUGS:
        targets = {
            step["target_internal_temperature_c"]
            for step in steps
            if step["target_internal_temperature_c"] is not None
        }
        if not targets:
            raise V1ImportError(f"{slug}: нет target в сиде температур")
        if slug in {
            "classic-roast-chicken",
            "kuritsa-maslo-limon-zapechennaya",
            "kuritsa-s-yablokami-zapechennaya",
            "kuritsa-tselikom-limonnoe-maslo-bazovyy",
        } and not ({72, 82} <= targets):
            raise V1ImportError(f"{slug}: целая птица требует target 72 и 82")

    flags = []
    caution = None
    if slug in POULTRY_TEMP_SLUGS:
        flags = ["poultry_temp"]
        caution = CAUTION_TEXT.get(slug)
        if not caution:
            raise V1ImportError(f"{slug}: poultry_temp без caution_text")

    source_url = (raw.get("source_url") or "").strip() or None
    return {
        "slug": slug,
        "title": raw["title"],
        "protein_base": protein_base,
        "cook_method": cook_method,
        "dish_type": dish_type,
        "summary": raw.get("summary"),
        "source_name": raw.get("source_name") or None,
        "source_url": source_url,
        "source_type": raw.get("source_type") or None,
        "ingredient_titles": " ".join(titles),
        "equipment": equipment,
        "allowed_cuts": [],
        "notes": split_notes_blob(raw.get("notes")),
        "prep": raw.get("prep") or [],
        "variants": _parse_legacy_variants(raw.get("variations") or []),
        "high_risk_flags": flags,
        "caution_text": caution,
        "lines": lines,
        "steps": steps,
        "origin": "v1",
        "raw": raw,
    }


def _parse_steps(slug: str, raw_steps: list, temp_seed: dict) -> list[dict]:
    rules = temp_seed.get(slug) or []
    used = [False] * len(rules)
    out = []
    for position, step in enumerate(raw_steps):
        if isinstance(step, str):
            text = step
            timer_min = None
            timer_label = None
            timer_note = None
        elif isinstance(step, dict):
            text = step.get("text") or ""
            timer_min = step.get("timer_min")
            timer_label = step.get("timer_label")
            timer_note = step.get("timer_note")
        else:
            raise V1ImportError(f"{slug}: шаг {position} неизвестного типа")
        pull = target = hold = None
        for i, rule in enumerate(rules):
            if used[i]:
                continue
            needle = rule["match"]
            if needle.lower() in text.lower():
                used[i] = True
                pull = rule.get("pull_internal_temperature_c")
                target = rule.get("target_internal_temperature_c")
                hold = rule.get("hold_seconds")
                break
        out.append(
            {
                "position": position,
                "text": text,
                "timer_seconds": int(timer_min * 60) if timer_min is not None else None,
                "timer_label": timer_label,
                "timer_note": timer_note,
                "pull_internal_temperature_c": pull,
                "target_internal_temperature_c": target,
                "hold_seconds": hold,
            }
        )
    unused = [rules[i]["match"] for i, flag in enumerate(used) if not flag]
    if unused:
        raise V1ImportError(f"{slug}: сид температур не совпал со шагами: {unused}")
    return out


def _parse_legacy_variants(raw_variations: list) -> list[dict]:
    used: set[str] = set()
    out = []
    for item in raw_variations:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip() or "Вариация"
        out.append(
            {
                "axis": "addon",
                "code": slugify_ru(title, used=used),
                "title": title,
                "has_delta": False,
                "legacy_text": item.get("text") or "",
                "ingredient_delta": None,
                "step_delta": None,
                "allergen_delta": None,
                "high_risk_delta": {},
                "cook_method_override": None,
                "protein_base_override": None,
                "equipment": None,
                "caution_text_override": None,
            }
        )
    return out


def _upsert_content(data_root: Path) -> None:
    for type_name, slug, title, rel in CONTENT_SOURCES:
        path = data_root / rel
        if not path.is_file():
            raise V1ImportError(f"Нет справочника {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        ContentDocument.objects.update_or_create(
            type=type_name,
            slug=slug,
            defaults={"title": title, "payload_json": payload},
        )


def _is_v2_overlay(slug: str) -> bool:
    """Overlay/wave rows have time_profile; do not roll them back to V1 JSON."""
    return Recipe.objects.filter(slug=slug, time_total_minutes__isnull=False).exists()


def _upsert_recipe(item: dict) -> None:
    upsert_recipe(item)


