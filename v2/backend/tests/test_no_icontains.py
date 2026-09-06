from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_i11_catalog_search_has_no_icontains():
    search_py = (ROOT / "apps" / "recipes" / "services" / "search.py").read_text(
        encoding="utf-8"
    )
    views_py = (ROOT / "apps" / "recipes" / "views.py").read_text(encoding="utf-8")
    assert "__icontains" not in search_py
    assert "__icontains" not in views_py
    assert "to_tsvector" in (ROOT / "apps" / "recipes" / "models.py").read_text(
        encoding="utf-8"
    )
    assert "normalize_ru" in search_py
