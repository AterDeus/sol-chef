"""Write a live Recipe from Postgres as author draft JSON."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.recipes.etl.serialize import recipe_to_draft
from apps.recipes.models import Recipe


class Command(BaseCommand):
    help = "Выгрузить рецепт из БД в JSON черновика (для правки и import_draft --path)."

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True, help="slug рецепта")
        parser.add_argument(
            "--path",
            type=str,
            help="Куда писать. По умолчанию stdout.",
        )

    def handle(self, *args, **options):
        slug = options["slug"].strip()
        try:
            recipe = Recipe.objects.prefetch_related(
                "ingredients__ingredient", "steps", "variants"
            ).get(slug=slug)
        except Recipe.DoesNotExist as exc:
            raise CommandError(f"Нет рецепта {slug}") from exc
        payload = recipe_to_draft(recipe)
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        dest = options.get("path")
        if dest:
            path = Path(dest)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            self.stdout.write(f"записан {path}")
            return
        self.stdout.write(text)
