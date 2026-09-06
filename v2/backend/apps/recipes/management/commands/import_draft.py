"""Import accepted V2 recipe drafts into Postgres (overlay after import_v1)."""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.recipes.etl.draft import (
    DraftError,
    known_from_v1_map,
    load_json,
    load_review,
    parse_draft,
    review_allows_import,
    validate_draft,
)
from apps.recipes.etl.upsert import upsert_recipe


def drafts_root() -> Path:
    mounted = Path(settings.V1_DATA_ROOT) / "v2" / "docs" / "drafts"
    if (mounted / "recipes").is_dir():
        return mounted
    return Path(__file__).resolve().parents[5] / "docs" / "drafts"


def v1_map_path() -> Path:
    return Path(__file__).resolve().parents[2] / "fixtures" / "v1_ingredient_map.json"


class Command(BaseCommand):
    help = "Validate and upsert V2 draft recipes. --accepted loads only Luna-approved overlays."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Один файл черновика")
        parser.add_argument(
            "--accepted",
            action="store_true",
            help="Все slug с reviews/<slug>.json verdict=accept и cookable=true",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Только валидатор, без записи и без вердикта Luna",
        )

    def handle(self, *args, **options):
        root = drafts_root()
        recipes_dir = root / "recipes"
        reviews_dir = root / "reviews"
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
        for path in paths:
            if path.name.startswith("_"):
                continue
            try:
                raw = load_json(path)
            except DraftError as exc:
                raise CommandError(str(exc)) from exc
            errors = validate_draft(raw, overlay=True, known_ingredients=known)
            slug = (raw.get("id") or raw.get("slug") or path.stem).strip()
            if errors:
                for item in errors:
                    self.stderr.write(item)
                raise CommandError(f"{path.name}: валидатор {len(errors)} ошибок")
            if options.get("check") and not options.get("accepted"):
                self.stdout.write(f"OK {slug}")
                continue
            if options.get("accepted") or not options.get("check"):
                review_path = reviews_dir / f"{slug}.json"
                try:
                    review = load_review(review_path)
                except DraftError as exc:
                    if options.get("path") and not options.get("accepted"):
                        raise CommandError(
                            f"{slug}: нет вердикта Luna ({review_path}). "
                            "Сначала независимая проверка."
                        ) from exc
                    self.stdout.write(f"пропуск {slug}: нет accept-вердикта")
                    continue
                if not review_allows_import(review):
                    self.stdout.write(
                        f"пропуск {slug}: verdict={review.get('verdict')} "
                        f"cookable={review.get('cookable')}"
                    )
                    continue
            try:
                item = parse_draft(raw, known_ingredients=known)
            except DraftError as exc:
                raise CommandError(str(exc)) from exc
            with transaction.atomic():
                upsert_recipe(item)
            imported += 1
            self.stdout.write(f"записан {slug}")
        self.stdout.write(f"готово imported={imported}")
