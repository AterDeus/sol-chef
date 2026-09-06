"""Resolve pantry text and coarse groups. No runtime LLM."""

from __future__ import annotations

from apps.recipes.pantry_vocab import (
    CANONICAL_INGREDIENT_LABEL_RU,
    HAVE_GROUPS,
    HAVE_TEXT_ALIASES,
    shopping_ids,
)


def norm_ru(text: str) -> str:
    return (text or "").strip().lower().replace("ё", "е")


def split_pantry_text(text: str) -> list[str]:
    raw = (text or "").replace(";", ",")
    return [part.strip() for part in raw.split(",") if part.strip()]


def expand_have_group(code: str) -> list[str]:
    return list(HAVE_GROUPS.get(code, ()))


def pantry_universe(known: set[str] | None = None, titles: dict[str, str] | None = None):
    ids = shopping_ids() | (known or set())
    labels = {**CANONICAL_INGREDIENT_LABEL_RU, **(titles or {})}
    return ids, labels


def resolve_token(token: str, *, titles: dict[str, str], known: set[str]) -> list[str]:
    """Return canonical_ids. Empty = unknown. Ambiguous words like «масло» stay unknown."""
    raw = token.strip()
    if not raw:
        return []
    universe, labels = pantry_universe(known, titles)
    if raw in universe:
        return [raw]
    key = norm_ru(raw)
    alias = HAVE_TEXT_ALIASES.get(key)
    if alias:
        if alias in HAVE_GROUPS:
            return list(HAVE_GROUPS[alias])
        if alias in universe:
            return [alias]
    for cid, title in labels.items():
        if norm_ru(title) == key:
            return [cid]
    return []


def resolve_pantry_text(text: str, *, titles: dict[str, str], known: set[str]) -> tuple[list[str], list[str]]:
    found: list[str] = []
    unknown: list[str] = []
    seen: set[str] = set()

    def add_ids(ids: list[str]) -> None:
        for cid in ids:
            if cid not in seen:
                seen.add(cid)
                found.append(cid)

    for phrase in split_pantry_text(text):
        ids = resolve_token(phrase, titles=titles, known=known)
        if ids:
            add_ids(ids)
            continue
        words = [word.strip(" .") for word in phrase.split() if word.strip(" .")]
        if len(words) <= 1:
            unknown.append(phrase)
            continue
        i = 0
        leftover: list[str] = []
        while i < len(words):
            matched: list[str] | None = None
            taken = 1
            for length in range(len(words) - i, 0, -1):
                chunk = " ".join(words[i : i + length])
                chunk_ids = resolve_token(chunk, titles=titles, known=known)
                if chunk_ids:
                    matched = chunk_ids
                    taken = length
                    break
            if matched:
                add_ids(matched)
                i += taken
            else:
                leftover.append(words[i])
                i += 1
        unknown.extend(leftover)
    return found, unknown
