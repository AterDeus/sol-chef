from __future__ import annotations

import os

import pytest
from rest_framework.test import APIClient

from apps.prep.models import PrepKit
from apps.prep.services.validate import KitImportError, upsert_kit
from apps.recipes.models import Recipe, RecipeStep

pytestmark = [
    pytest.mark.skipif(
        not (os.environ.get("POSTGRES_HOST") or os.environ.get("DATABASE_URL")),
        reason="нет POSTGRES_HOST/DATABASE_URL",
    ),
    pytest.mark.django_db,
]


def _recipe(slug: str, *, status: str = "published") -> Recipe:
    recipe = Recipe.objects.create(
        slug=slug,
        title=slug,
        protein_base="poultry",
        cook_method="pan_fry",
        dish_type="main",
        scale_mode="linear",
        scalable=True,
        energy_profile="standard",
        status=status,
    )
    RecipeStep.objects.create(recipe=recipe, position=0, text="Шаг с нуля")
    return recipe


def _trio(tag: str) -> tuple[Recipe, Recipe, Recipe]:
    return (
        _recipe(f"{tag}-soup"),
        _recipe(f"{tag}-wrap"),
        _recipe(f"{tag}-extra"),
    )


def _slots(soup: str, wrap: str, extra: str, alt: str | None = None) -> list[dict]:
    rows: list[dict] = []
    for day in range(1, 8):
        if day % 2 == 1:
            rows.append(
                {
                    "day": day,
                    "meal": "lunch",
                    "slug": soup,
                    "mode": "finish",
                    "source": {"kind": "weekend"},
                    "container_ids": ["c1"],
                    "steps": [{"text": f"Довести суп {day}"}],
                    "alternatives": [],
                }
            )
        else:
            rows.append(
                {
                    "day": day,
                    "meal": "lunch",
                    "slug": soup,
                    "mode": "reheat",
                    "source": {"kind": "slot", "day": day - 1, "meal": "lunch"},
                    "container_ids": [],
                    "steps": [{"text": f"Разогреть суп {day}"}],
                    "alternatives": [],
                    "no_leftover": {
                        "slug": extra,
                        "mode": "assemble",
                        "container_ids": ["c2"],
                        "steps": [{"text": f"Собрать без остатка {day}"}],
                        "plate": {
                            "title": "Лаваш без вчерашнего",
                            "composition": "Лаваш",
                        },
                    },
                }
            )
        dinner_alts = []
        if alt and day == 1:
            dinner_alts = [
                {
                    "slug": alt,
                    "label": "Другой лаваш",
                    "mode": "assemble",
                    "container_ids": ["c2"],
                    "steps": [{"text": "Собрать замену"}],
                }
            ]
        rows.append(
            {
                "day": day,
                "meal": "dinner",
                "slug": wrap,
                "mode": "assemble",
                "source": {"kind": "weekend"},
                "container_ids": ["c2"],
                "steps": [{"text": f"Собрать лаваш {day}"}],
                "alternatives": dinner_alts,
            }
        )
    return rows


def _payload(
    *,
    soup: str,
    wrap: str,
    extra: str,
    alt: str | None = None,
    kit_id: str = "nedelya-test",
    **overrides,
) -> dict:
    data = {
        "id": kit_id,
        "title": "Тестовая неделя",
        "servings_base": 2,
        "position": 1,
        "metrics": {"slots_assemble": 7, "slots_finish": 4, "slots_reheat": 3},
        "components": [
            {
                "id": "soup_base",
                "title": "Суп",
                "canonical_ids": ["chicken_thigh"],
                "qty": 700,
                "unit": "g",
                "container_ids": ["c1"],
                "weekend_steps": ["Сварить основу."],
                "parcook": {},
                "storage": {"fridge_days": 3, "notes": "оценка редакции, не ГОСТ"},
            },
            {
                "id": "chicken",
                "title": "Курица",
                "canonical_ids": ["chicken_thigh"],
                "qty": 1400,
                "unit": "g",
                "container_ids": ["c2"],
                "weekend_steps": ["Разобрать."],
                "parcook": {},
                "storage": {},
            },
        ],
        "containers": [
            {
                "id": "c1",
                "label": "№1",
                "component_id": "soup_base",
                "qty": 700,
                "unit": "g",
                "place": "fridge",
                "thaw_before_day": None,
            },
            {
                "id": "c2",
                "label": "№2",
                "component_id": "chicken",
                "qty": 1400,
                "unit": "g",
                "place": "freezer",
                "thaw_before_day": 3,
            },
        ],
        "weekend_timeline": [{"t_min": 0, "hands": "Начать", "heat": ""}],
        "slots": _slots(soup, wrap, extra, alt),
        "shopping": [
            {"canonical_id": "chicken_thigh", "qty": 2100, "unit": "g", "title_ru": "Бедро"}
        ],
        "allergens": {"contains": [], "unknown": [], "may_contain": []},
    }
    data.update(overrides)
    return data


def test_u51_empty_prep_list():
    client = APIClient()
    res = client.get("/api/prep-kits/")
    assert res.status_code == 200
    assert res.json() == {"results": []}


def test_u52_list_published_order():
    soup, wrap, extra = _trio("a")
    upsert_kit(
        _payload(
            soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-b", position=2
        ),
        publish=True,
    )
    upsert_kit(
        _payload(
            soup=soup.slug,
            wrap=wrap.slug,
            extra=extra.slug,
            kit_id="kit-a",
            position=2,
            title="A",
        ),
        publish=True,
    )
    draft = PrepKit.objects.create(slug="hidden", title="no", status="draft", position=0)
    client = APIClient()
    res = client.get("/api/prep-kits/")
    slugs = [row["slug"] for row in res.json()["results"]]
    assert "hidden" not in slugs
    assert slugs == ["kit-a", "kit-b"]
    assert draft.status == "draft"


def test_prep_list_keeps_stored_kcal():
    soup, wrap, extra = _trio("kcal")
    kit = upsert_kit(
        _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-kcal"),
        publish=True,
    )
    assert kit is not None
    stored = dict(kit.metrics or {})
    stored["kcal_avg_per_serving"] = 432
    kit.metrics = stored
    kit.save(update_fields=["metrics"])
    client = APIClient()
    res = client.get("/api/prep-kits/")
    row = next(item for item in res.json()["results"] if item["slug"] == kit.slug)
    assert row["metrics"]["kcal_avg_per_serving"] == 432


def test_u53_import_fourteen_slots():
    soup, wrap, extra = _trio("b")
    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug)
    kit = upsert_kit(payload)
    assert kit is not None
    assert kit.status == "draft"
    assert kit.slots.count() == 14
    published = upsert_kit(payload, publish=True)
    assert published is not None
    assert published.status == "published"
    assert published.pk == kit.pk
    assert published.slots.count() == 14


def test_u54_import_rejects_bad_refs():
    soup, wrap, extra = _trio("c")
    unpublished = _recipe("draft-dish", status="draft")
    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug)
    payload["slots"][0]["container_ids"] = ["nope"]
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=unpublished.slug, wrap=wrap.slug, extra=extra.slug)
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug)
    for row in payload["slots"]:
        if row["day"] == 1 and row["meal"] == "lunch":
            row["mode"] = "reheat"
            row["source"] = {"kind": "slot", "day": 2, "meal": "lunch"}
            row["container_ids"] = []
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug)
    for row in payload["slots"]:
        if row["day"] == 3 and row["meal"] == "lunch":
            row["mode"] = "reheat"
            row["source"] = {"kind": "slot", "day": 1, "meal": "lunch"}
            row["container_ids"] = []
    with pytest.raises(KitImportError):
        upsert_kit(payload)
    assert not PrepKit.objects.filter(slug="nedelya-test").exists()


def test_u55_recipe_without_prep_keeps_book_steps():
    soup, wrap, extra = _trio("d")
    upsert_kit(_payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug), publish=True)
    client = APIClient()
    res = client.get(f"/api/recipes/{soup.slug}/")
    assert res.status_code == 200
    assert res.json()["steps"][0]["text"] == "Шаг с нуля"
    assert "prep_context" not in res.json()


def test_u56_ambiguous_prep_without_day_meal():
    soup, wrap, extra = _trio("e")
    upsert_kit(_payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug), publish=True)
    client = APIClient()
    res = client.get(f"/api/recipes/{wrap.slug}/", {"prep": "nedelya-test"})
    assert res.status_code == 400


def test_u57_prep_slot_steps_and_mode():
    soup, wrap, extra = _trio("f")
    upsert_kit(_payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug), publish=True)
    client = APIClient()
    res = client.get(
        f"/api/recipes/{soup.slug}/",
        {"prep": "nedelya-test", "day": "1", "meal": "lunch"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["steps"][0]["text"] == "Довести суп 1"
    assert body["prep_context"]["mode"] == "finish"
    assert body["prep_context"]["day"] == 1


def test_u58_servings_scales_qty_not_box_count():
    soup, wrap, extra = _trio("g")
    upsert_kit(_payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug), publish=True)
    client = APIClient()
    base = client.get("/api/prep-kits/nedelya-test/").json()
    scaled = client.get("/api/prep-kits/nedelya-test/", {"servings": "4"}).json()
    assert len(base["containers"]) == len(scaled["containers"]) == 2
    box = next(row for row in scaled["containers"] if row["label"] == "№2")
    base_box = next(row for row in base["containers"] if row["label"] == "№2")
    assert box["code"] == base_box["code"]
    assert box["qty"] == base_box["qty"] * 2
    half = client.get("/api/prep-kits/nedelya-test/", {"servings": "1"}).json()
    half_box = next(row for row in half["containers"] if row["label"] == "№2")
    assert half_box["qty"] == base_box["qty"] / 2


def test_u59_alternative_uses_own_steps():
    soup, wrap, extra = _trio("h")
    alt = _recipe("wrap-alt")
    upsert_kit(
        _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, alt=alt.slug),
        publish=True,
    )
    client = APIClient()
    res = client.get(
        f"/api/recipes/{alt.slug}/",
        {"prep": "nedelya-test", "day": "1", "meal": "dinner"},
    )
    assert res.status_code == 200
    assert res.json()["steps"][0]["text"] == "Собрать замену"
    assert res.json()["prep_context"]["mode"] == "assemble"


def test_u60_anchor_weight_with_prep_rejected():
    soup, wrap, extra = _trio("i")
    upsert_kit(_payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug), publish=True)
    client = APIClient()
    res = client.get(
        f"/api/recipes/{soup.slug}/",
        {"prep": "nedelya-test", "day": "1", "meal": "lunch", "anchor_weight": "400"},
    )
    assert res.status_code == 400


def test_u61_no_leftover_replaces_reheat():
    soup, wrap, extra = _trio("j")
    upsert_kit(_payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug), publish=True)
    client = APIClient()
    base = client.get("/api/prep-kits/nedelya-test/").json()
    reheat = next(row for row in base["slots"] if row["mode"] == "reheat")
    assert reheat["day"] == 2
    assert reheat["slug"] == soup.slug
    assert base["no_leftover"] is False
    assert base["has_leftovers"] is True

    fresh = client.get("/api/prep-kits/nedelya-test/", {"no_leftover": "1"}).json()
    assert fresh["no_leftover"] is True
    slot = next(
        row
        for row in fresh["slots"]
        if row["day"] == reheat["day"] and row["meal"] == reheat["meal"]
    )
    assert slot["mode"] == "assemble"
    assert slot["slug"] == extra.slug
    assert slot["feeds_slots"] == 1

    res = client.get(
        f"/api/recipes/{extra.slug}/",
        {
            "prep": "nedelya-test",
            "day": "2",
            "meal": "lunch",
            "no_leftover": "1",
        },
    )
    assert res.status_code == 200
    assert res.json()["steps"][0]["text"] == "Собрать без остатка 2"
    assert res.json()["prep_context"]["mode"] == "assemble"
    assert res.json()["prep_context"]["no_leftover"] is True

    res = client.get(
        f"/api/recipes/{extra.slug}/",
        {"prep": "nedelya-test", "day": "2", "meal": "lunch"},
    )
    assert res.status_code == 400

    payload = _payload(
        soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="nedelya-no-nl"
    )
    for row in payload["slots"]:
        if row.get("mode") == "reheat":
            row.pop("no_leftover", None)
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    dup = _payload(soup=soup.slug, wrap=wrap.slug, extra=wrap.slug, kit_id="nedelya-dup")
    with pytest.raises(KitImportError):
        upsert_kit(dup)
