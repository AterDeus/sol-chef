"""Rebuild calculator axis snapshots for published recipes."""

from django.core.management.base import BaseCommand

from apps.recipes.models import Recipe
from apps.recipes.services.snapshots import refresh_axis_snapshots


class Command(BaseCommand):
    help = "Собрать axis_snapshots для солвера калькулятора."

    def handle(self, *args, **options):
        qs = Recipe.objects.filter(status="published").prefetch_related(
            "ingredients__ingredient", "variants", "steps"
        )
        written = 0
        for recipe in qs:
            refresh_axis_snapshots(recipe)
            written += 1
        self.stdout.write(f"снимки: {written}")
