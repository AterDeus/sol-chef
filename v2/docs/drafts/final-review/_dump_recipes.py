# Temporary dump helper for editorial review. Not a product command.
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

BASE = "http://localhost:8080"
OUT_DIR = Path(__file__).resolve().parent / "recipes"
OUT_FILE = OUT_DIR / "all.md"
README = OUT_DIR / "README.md"


def get_json(url: str):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_catalog() -> list[dict]:
    items: list[dict] = []
    url = f"{BASE}/api/recipes/?page=1"
    while url:
        payload = get_json(url)
        items.extend(payload.get("results") or [])
        url = payload.get("next")
        if url and url.startswith("/"):
            url = BASE + url
    return items


def format_ingredient(line: dict) -> str:
    amount = (line.get("display_amount") or "").strip()
    name = (line.get("name") or "").strip()
    detail = (line.get("detail") or "").strip()
    bits = [part for part in (amount, name) if part]
    text = " ".join(bits) if bits else name
    if line.get("optional"):
        extra = "по желанию"
        detail = f"{detail}; {extra}" if detail else extra
    if detail:
        return f"- {text} — {detail}"
    return f"- {text}"


def format_timer(step: dict) -> str | None:
    seconds = step.get("timer_seconds")
    label = step.get("timer_label")
    note = step.get("timer_note")
    pull = step.get("pull_internal_temperature_c")
    target = step.get("target_internal_temperature_c")
    if seconds is None and not label and not note and pull is None and target is None:
        return None
    parts: list[str] = []
    if seconds is not None:
        if seconds >= 120 and seconds % 60 == 0:
            mins = seconds // 60
            head = f"таймер {mins} мин"
        else:
            head = f"таймер {seconds} с"
        if label:
            head = f"{head} ({label})"
        parts.append(head)
    elif label:
        parts.append(label)
    if note:
        parts.append(note)
    if pull is not None:
        parts.append(f"снятие {pull} °C")
    if target is not None:
        parts.append(f"цель {target} °C")
    if not parts:
        return None
    return "_" + "; ".join(parts) + "_"


def format_note(item: dict) -> str:
    title = (item.get("title") or "").strip()
    text = (item.get("text") or "").strip()
    if title:
        return f"**{title}.** {text}"
    return text


def render(recipe: dict) -> str:
    parts = [f"## {recipe['title']}", ""]
    summary = (recipe.get("summary") or "").strip()
    if summary:
        parts.append(summary)
        parts.append("")
    ings = recipe.get("ingredients") or []
    if ings:
        parts.append("### Ингредиенты")
        parts.append("")
        parts.extend(format_ingredient(line) for line in ings)
        parts.append("")
    steps = recipe.get("steps") or []
    if steps:
        parts.append("### Шаги")
        parts.append("")
        for i, step in enumerate(steps, start=1):
            parts.append(f"{i}. {(step.get('text') or '').strip()}")
            timer = format_timer(step)
            if timer:
                parts.append(f"   {timer}")
        parts.append("")
    notes = recipe.get("notes") or []
    note_texts = [format_note(item) for item in notes if (item.get("text") or "").strip()]
    if note_texts:
        parts.append("### Заметки")
        parts.append("")
        parts.append("\n\n".join(note_texts))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    catalog = fetch_catalog()
    catalog.sort(key=lambda item: item["title"])
    recipes = []
    for item in catalog:
        slug = item["slug"]
        recipes.append(get_json(f"{BASE}/api/recipes/{slug}/"))
    titles = [r["title"] for r in recipes]
    toc = "\n".join(f"- {title}" for title in titles)
    blocks = "\n---\n\n".join(render(r) for r in recipes)
    text = f"# Рецепты V2\n\n{toc}\n\n---\n\n{blocks}"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(text, encoding="utf-8")
    readme = README.read_text(encoding="utf-8") if README.exists() else ""
    readme = readme.replace("Карточек: **135**.", f"Карточек: **{len(recipes)}**.")
    if "Карточек:" not in readme:
        pass
    README.write_text(readme, encoding="utf-8") if readme else None
    print("wrote", OUT_FILE, "recipes", len(recipes), "chars", len(text))


if __name__ == "__main__":
    main()
