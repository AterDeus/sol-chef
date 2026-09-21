"""List published recipes with required assembled lines missing canonical_id."""

from django.core.management.base import BaseCommand

from apps.recipes.models import Recipe
from apps.recipes.services.assemble import VariantError, assemble_recipe


class Command(BaseCommand):
    help = "Сироты canonical_id в обязательных строках опубликованных рецептов."

    def handle(self, *args, **options):
        found = 0
        qs = Recipe.objects.filter(status="published").prefetch_related(
            "ingredients__ingredient", "variants", "steps"
        )
        for recipe in qs:
            try:
                assembled = assemble_recipe(recipe, enrich=False)
            except VariantError as exc:
                self.stderr.write(f"{recipe.slug}: {exc}")
                continue
            orphans = [
                (line.get("name") or "?").strip() or "?"
                for line in assembled.ingredients
                if not (line.get("canonical_id") or "").strip() and not line.get("optional")
            ]
            if not orphans:
                continue
            found += 1
            self.stdout.write(f"{recipe.slug}: {', '.join(orphans)}")
        if found == 0:
            self.stdout.write("сирот canonical_id нет")
            return
        self.stdout.write(f"итого {found}")
