"""Split V1 notes blob into the JSON list DATA-MODEL expects."""

from __future__ import annotations


def split_notes_blob(blob: str | None) -> list[dict]:
    """NULL → []; no blank line → one item; else split on \\n\\n. Titles stay null."""
    if blob is None:
        return []
    text = str(blob).strip()
    if not text:
        return []
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    return [{"title": None, "text": part} for part in parts]


def normalize_notes(value) -> list[dict]:
    if value is None:
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict) and (item.get("text") or "").strip():
                title = item.get("title")
                out.append(
                    {
                        "title": title if isinstance(title, str) and title.strip() else None,
                        "text": str(item["text"]).strip(),
                    }
                )
            elif isinstance(item, str) and item.strip():
                out.append({"title": None, "text": item.strip()})
        return out
    if isinstance(value, str):
        return split_notes_blob(value)
    return []
