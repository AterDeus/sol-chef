from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.prep.models import PrepKit
from apps.prep.services.metrics import refresh_kit_metrics


class Command(BaseCommand):
    help = "Пересчитать metrics.kcal_avg_per_serving для наборов (не вызывается из GET)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug",
            type=str,
            help="Только этот набор; без флага — все наборы",
        )

    def handle(self, *args, **options):
        qs = PrepKit.objects.all().order_by("position", "slug")
        slug = options.get("slug")
        if slug:
            qs = qs.filter(slug=slug)
            if not qs.exists():
                raise CommandError(f"Набор {slug} не найден.")
        count = 0
        for kit in qs:
            refresh_kit_metrics(kit)
            count += 1
            self.stdout.write(f"metrics {kit.slug}")
        self.stdout.write(f"updated {count}")
