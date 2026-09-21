"""Dump backend Django apps (content, prep, recipes) for an external auditor."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APPS = ROOT / "backend" / "apps"

SKIP_DIRS = {"__pycache__", "migrations"}

CLASS_RE = re.compile(r"^class\s+([A-Za-z0-9_]+)\s*[:(]", re.MULTILINE)
FUNC_RE = re.compile(r"^def\s+([A-Za-z0-9_]+)\s*\(", re.MULTILINE)

APPS_META = (
    {
        "name": "content",
        "title": "Бэкенд sol-chef 2.0 — приложение content",
        "out": "BACKEND-CONTENT.md",
        "note": "Справочный контент: советы, зёрна, мясо. Не каталог рецептов и не калькулятор.",
    },
    {
        "name": "prep",
        "title": "Бэкенд sol-chef 2.0 — приложение prep",
        "out": "BACKEND-PREP.md",
        "note": "Наборы «На неделю»: слоты, масштабирование, разморозка, остатки, валидация.",
    },
    {
        "name": "recipes",
        "title": "Бэкенд sol-chef 2.0 — приложение recipes",
        "out": "BACKEND-RECIPES.md",
        "note": "Каталог, карточка, поиск, солвер калькулятора, ETL, масштабирование порций, аллергены, КБЖУ.",
    },
)


def iter_py(app_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in app_dir.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def symbols(text: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for name in CLASS_RE.findall(text) + FUNC_RE.findall(text):
        if name.startswith("_") and not name.startswith("__"):
            continue
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def dump_app(meta: dict) -> None:
    app_dir = APPS / meta["name"]
    rows: list[tuple[Path, str, list[str], int]] = []
    for path in iter_py(app_dir):
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            continue
        rows.append((path, text, symbols(text), line_count(text)))

    parts: list[str] = []
    parts.append(f"# {meta['title']} — дамп для аудита")
    parts.append("")
    parts.append("Снимок кода на 2026-09-20.")
    parts.append(f"Источник: `v2/backend/apps/{meta['name']}/`.")
    parts.append(meta["note"])
    parts.append("")
    parts.append("Правило раскладки: **один файл = содержимое одного исходного `.py`**.")
    parts.append("Заголовок блока — путь относительно `v2/`. Ниже — классы и функции верхнего уровня и полный исходник.")
    parts.append("Не входят: `migrations/`, `__pycache__/`, пустые `__init__.py`.")
    parts.append("")
    parts.append("## Оглавление")
    parts.append("")
    parts.append("| # | Файл | Классы и функции | Строк |")
    parts.append("|---|------|------------------|------:|")
    for i, (path, _text, names, lines) in enumerate(rows, start=1):
        rel = path.relative_to(ROOT).as_posix()
        exp = ", ".join(f"`{n}`" for n in names) if names else "—"
        parts.append(f"| {i} | `{rel}` | {exp} | {lines} |")
    parts.append("")
    parts.append(f"Всего файлов: **{len(rows)}**. Строк исходников: **{sum(r[3] for r in rows)}**.")
    parts.append("")
    parts.append("---")
    parts.append("")

    for i, (path, text, names, lines) in enumerate(rows, start=1):
        rel = path.relative_to(ROOT).as_posix()
        exp = ", ".join(names) if names else "нет классов/функций верхнего уровня"
        parts.append(f"## {i}. `{rel}`")
        parts.append("")
        parts.append(f"- Путь: `v2/{rel}`")
        parts.append(f"- Классы и функции: {exp}")
        parts.append(f"- Строк: {lines}")
        parts.append("")
        parts.append("```python")
        parts.append(text.rstrip("\n"))
        parts.append("```")
        parts.append("")
        parts.append("---")
        parts.append("")

    out = Path(__file__).with_name(meta["out"])
    out.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {out.name} ({out.stat().st_size} bytes, {len(rows)} files, {sum(r[3] for r in rows)} lines)")


def main() -> None:
    for meta in APPS_META:
        dump_app(meta)


if __name__ == "__main__":
    main()
