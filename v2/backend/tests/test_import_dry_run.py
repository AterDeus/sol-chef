from pathlib import Path

from django.conf import settings

from apps.recipes.etl.load import V1ImportError, resolve_v1_root
from apps.recipes.management.commands.import_v1 import run_import


def _v1_root() -> Path:
    env = Path(settings.V1_DATA_ROOT)
    try:
        return resolve_v1_root(env)
    except V1ImportError:
        return resolve_v1_root(Path(__file__).resolve().parents[3])


def test_import_v1_dry_run_parses_43():
    report = run_import(_v1_root(), dry_run=True)
    text = "\n".join(report)
    assert "recipes=43" in text
    assert "dry_run=True" in text
    assert "Запись в БД пропущена." in text
