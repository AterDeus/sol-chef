from pathlib import Path

from django.conf import settings

from apps.recipes.constants import EXPECTED_RECIPE_COUNT, EXPECTED_RECIPE_FILES
from apps.recipes.etl.load import V1ImportError, load_recipe_objects, read_index, resolve_v1_root


def _v1_root() -> Path:
    env = Path(settings.V1_DATA_ROOT)
    try:
        return resolve_v1_root(env)
    except V1ImportError:
        return resolve_v1_root(Path(__file__).resolve().parents[3])


def test_i1_v1_catalog_has_43_recipes():
    root = _v1_root()
    files = read_index(root)
    assert len(files) == EXPECTED_RECIPE_FILES
    recipes = load_recipe_objects(root)
    assert len(recipes) == EXPECTED_RECIPE_COUNT
    slugs = [raw["id"] for _rel, raw in recipes]
    assert len(slugs) == len(set(slugs))
