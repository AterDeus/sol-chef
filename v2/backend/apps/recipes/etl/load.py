"""Load V1 recipe JSON (no DB). Used by import_v1 and tests."""

from __future__ import annotations

import json
from pathlib import Path

from apps.recipes.constants import EXPECTED_RECIPE_COUNT, EXPECTED_RECIPE_FILES


class V1ImportError(Exception):
    pass


def read_index(data_root: Path) -> list[str]:
    index_path = data_root / "data" / "recipes" / "index.json"
    if not index_path.is_file():
        raise V1ImportError(f"Нет файла {index_path}")
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    files = payload.get("files") or []
    if len(files) != EXPECTED_RECIPE_FILES:
        raise V1ImportError(
            f"Ожидалось {EXPECTED_RECIPE_FILES} файлов в index.json, получено {len(files)}"
        )
    return files


def load_recipe_objects(data_root: Path) -> list[tuple[str, dict]]:
    """Return list of (relative_file, recipe_dict). Fails if count ≠ 43."""
    files = read_index(data_root)
    found: list[tuple[str, dict]] = []
    for rel in files:
        path = data_root / rel
        if not path.is_file():
            raise V1ImportError(f"Нет файла рецептов {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise V1ImportError(f"{rel} должен быть массивом рецептов")
        for recipe in data:
            found.append((rel, recipe))
    if len(found) != EXPECTED_RECIPE_COUNT:
        raise V1ImportError(
            f"Ожидалось {EXPECTED_RECIPE_COUNT} рецептов, получено {len(found)}"
        )
    return found


def folder_from_rel(rel: str) -> str:
    # data/recipes/duhovka/ptitsa.json → duhovka
    parts = Path(rel).parts
    return parts[2]
