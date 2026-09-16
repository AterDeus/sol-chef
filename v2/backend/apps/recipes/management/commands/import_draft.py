"""Import V2 recipe drafts into Postgres (overlay after import_v1)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.recipes.etl.draft import (
    DraftError,
    known_from_v1_map,
    load_json,
    parse_draft,
    validate_draft,
)
from apps.recipes.etl.nutrition import load_ingredient_nutrition
from apps.recipes.etl.upsert import upsert_recipe


def drafts_root() -> Path:
    candidates: list[Path] = []
    docs_root = os.environ.get("DOCS_ROOT")
    if docs_root:
        candidates.append(Path(docs_root) / "drafts")
    candidates.append(Path(settings.V1_DATA_ROOT) / "v2" / "docs" / "drafts")
    candidates.append(Path(__file__).resolve().parents[5] / "docs" / "drafts")
    for candidate in candidates:
        if (candidate / "recipes").is_dir():
            return candidate
    return candidates[0]


def v1_map_path() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "v1_ingredient_map.json"


class Command(BaseCommand):
    help = (
        "Validate and upsert V2 draft recipes. "
        "--path один файл; --accepted все *.json в drafts/recipes/; "
        "пустая папка — успех, не ошибка. Вердикт Terra для импорта не нужен."
    )

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Один файл черновика")
        parser.add_argument(
            "--accepted",
            action="store_true",
            help="Все JSON в drafts/recipes/ (без reviews)",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Только валидатор, без записи",
        )

    def handle(self, *args, **options):
        root = drafts_root()
        recipes_dir = root / "recipes"
        try:
            known = known_from_v1_map(json.loads(v1_map_path().read_text(encoding="utf-8")))
        except OSError as exc:
            raise CommandError(f"Нет сида ингредиентов: {exc}") from exc

        paths: list[Path] = []
        if options.get("path"):
            paths = [Path(options["path"])]
        elif options.get("accepted") or options.get("check"):
            if recipes_dir.is_dir():
                paths = sorted(recipes_dir.glob("*.json"))
        else:
            raise CommandError("Укажите --path FILE или --accepted или --check")

        if not paths:
            self.stdout.write("Черновиков нет.")
            return

        imported = 0
        skipped = 0
        fail_fast = bool(options.get("path"))
        for path in paths:
            if path.name.startswith("_"):
                continue
            try:
                raw = load_json(path)
            except DraftError as exc:
                if fail_fast:
                    raise CommandError(str(exc)) from exc
                skipped += 1
                self.stdout.write(f"пропуск {path.name}: {exc}")
                continue
            errors = validate_draft(raw, overlay=True, known_ingredients=known)
            slug = (raw.get("id") or raw.get("slug") or path.stem).strip()
            if errors:
                for item in errors:
                    self.stderr.write(item)
                msg = f"{path.name}: валидатор {len(errors)} ошибок"
                if fail_fast:
                    raise CommandError(msg)
                skipped += 1
                self.stdout.write(f"пропуск {slug}: {msg}")
                continue
            if options.get("check") and not options.get("accepted"):
                self.stdout.write(f"OK {slug}")
                continue
            try:
                item = parse_draft(raw, known_ingredients=known)
            except DraftError as exc:
                if fail_fast:
                    raise CommandError(str(exc)) from exc
                skipped += 1
                self.stdout.write(f"пропуск {slug}: {exc}")
                continue
            with transaction.atomic():
                upsert_recipe(item)
                load_ingredient_nutrition()
            imported += 1
            self.stdout.write(f"записан {slug}")
        self.stdout.write(f"готово imported={imported} skipped={skipped}")
