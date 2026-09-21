from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.prep.services.validate import KitImportError, upsert_kit
from apps.recipes.etl.draft import DraftError, load_json


class Command(BaseCommand):
    help = "Validate and upsert a weekly-prep kit JSON. --dry-run не пишет."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, required=True, help="Файл kit JSON")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только валидатор, без записи",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Опубликовать набор после успешного импорта",
        )
        parser.add_argument(
            "--draft",
            action="store_true",
            help="Сохранить набор как черновик (даже если он уже published)",
        )

    def handle(self, *args, **options):
        if options["publish"] and options["draft"]:
            raise CommandError("Укажите только один флаг: --publish или --draft.")
        if options["publish"]:
            publish: bool | None = True
        elif options["draft"]:
            publish = False
        else:
            publish = None
        path = Path(options["path"])
        try:
            payload = load_json(path)
        except DraftError as exc:
            raise CommandError(str(exc)) from exc
        try:
            kit = upsert_kit(
                payload, dry_run=bool(options["dry_run"]), publish=publish
            )
        except KitImportError as exc:
            for line in exc.errors:
                self.stderr.write(line)
            raise CommandError(f"Набор не принят ({len(exc.errors)} ошибок).") from exc
        if options["dry_run"]:
            self.stdout.write("dry-run ok")
            return
        self.stdout.write(f"imported {kit.slug} status={kit.status}")
