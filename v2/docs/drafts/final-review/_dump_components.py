"""One-shot dump of frontend components for an external auditor."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMPONENTS = ROOT / "frontend" / "components"
OUT = Path(__file__).with_name("FRONTEND-COMPONENTS.md")

EXPORT_RE = re.compile(
    r"^export\s+(?:default\s+)?(?:async\s+)?(?:function|const|class)\s+([A-Za-z0-9_]+)",
    re.MULTILINE,
)


def exports(text: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for name in EXPORT_RE.findall(text):
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def main() -> None:
    files = sorted(COMPONENTS.glob("*.tsx"))
    rows: list[tuple[Path, str, list[str], int]] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        names = exports(text)
        lines = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
        rows.append((path, text, names, lines))

    parts: list[str] = []
    parts.append("# Компоненты фронтенда sol-chef 2.0 — дамп для аудита")
    parts.append("")
    parts.append("Снимок кода на 2026-09-20. Источник: `v2/frontend/components/`.")
    parts.append("Страницы `app/` и стили сюда не входят — только React-компоненты.")
    parts.append("")
    parts.append("Правило раскладки: **один файл = содержимое одного исходного `.tsx`**.")
    parts.append("Заголовок блока — путь относительно `v2/`. Ниже — экспорты и полный исходник.")
    parts.append("Вспомогательные функции без `export` живут в том же файле, что и публичный компонент.")
    parts.append("")
    parts.append("## Оглавление")
    parts.append("")
    parts.append("| # | Файл | Экспорты | Строк |")
    parts.append("|---|------|----------|------:|")
    for i, (path, _text, names, lines) in enumerate(rows, start=1):
        rel = f"frontend/components/{path.name}"
        exp = ", ".join(f"`{n}`" for n in names) if names else "—"
        parts.append(f"| {i} | `{rel}` | {exp} | {lines} |")
    parts.append("")
    parts.append(f"Всего файлов: **{len(rows)}**. Строк исходников: **{sum(r[3] for r in rows)}**.")
    parts.append("")
    parts.append("---")
    parts.append("")

    for i, (path, text, names, lines) in enumerate(rows, start=1):
        rel = f"frontend/components/{path.name}"
        exp = ", ".join(names) if names else "нет именованных export function/const/class"
        parts.append(f"## {i}. `{rel}`")
        parts.append("")
        parts.append(f"- Путь: `v2/{rel}`")
        parts.append(f"- Экспорты: {exp}")
        parts.append(f"- Строк: {lines}")
        parts.append("")
        parts.append(f"```tsx")
        parts.append(text.rstrip("\n"))
        parts.append("```")
        parts.append("")
        parts.append("---")
        parts.append("")

    OUT.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(rows)} files)")


if __name__ == "__main__":
    main()
