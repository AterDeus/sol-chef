from __future__ import annotations

import os
from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.prep.models import PrepComponent, PrepContainer, PrepKit
from apps.prep.services.graph import kit_graph
from apps.prep.services.leftover import merge_shopping
from apps.prep.services.read_model import KitData
from apps.prep.services.validate import KitImportError, upsert_kit
from tests.test_prep import _payload, _trio

pytestmark = [
    pytest.mark.skipif(
        not (os.environ.get("POSTGRES_HOST") or os.environ.get("DATABASE_URL")),
        reason="нет POSTGRES_HOST/DATABASE_URL",
    ),
    pytest.mark.django_db,
]


def test_list_get_does_not_write():
    soup, wrap, extra = _trio("list-ro")
    upsert_kit(
        _payload(
            soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-list-ro"
        ),
        publish=True,
    )
    client = APIClient()
    with CaptureQueriesContext(connection) as queries:
        response = client.get("/api/prep-kits/")
    assert response.status_code == 200
    sql = " ".join(query["sql"].upper() for query in queries)
    assert " UPDATE " not in sql
    assert " INSERT " not in sql
    assert " DELETE " not in sql


def test_detail_get_does_not_write_and_stays_bounded():
    soup, wrap, extra = _trio("detail-ro")
    upsert_kit(
        _payload(
            soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-detail-ro"
        ),
        publish=True,
    )
    client = APIClient()
    with CaptureQueriesContext(connection) as queries:
        response = client.get("/api/prep-kits/kit-detail-ro/")
    assert response.status_code == 200
    sql = " ".join(query["sql"].upper() for query in queries)
    assert " UPDATE " not in sql
    assert " INSERT " not in sql
    assert " DELETE " not in sql
    assert len(queries) <= 8


def test_draft_import_is_not_public():
    soup, wrap, extra = _trio("draft-pub")
    payload = _payload(
        soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-hidden-draft"
    )
    kit = upsert_kit(payload)
    assert kit is not None
    assert kit.status == "draft"
    client = APIClient()
    listed = client.get("/api/prep-kits/")
    assert "kit-hidden-draft" not in [row["slug"] for row in listed.json()["results"]]
    detail = client.get("/api/prep-kits/kit-hidden-draft/")
    assert detail.status_code == 404
    published = upsert_kit(payload, publish=True)
    assert published.status == "published"
    again = upsert_kit(payload)
    assert again.status == "published"
    hidden = upsert_kit(payload, publish=False)
    assert hidden.status == "draft"
    assert client.get("/api/prep-kits/kit-hidden-draft/").status_code == 404


def test_merge_shopping_keeps_units_separate():
    merged = merge_shopping(
        [{"canonical_id": "milk", "qty": 200, "unit": "g", "title_ru": "Молоко"}],
        [{"canonical_id": "milk", "qty": 300, "unit": "ml", "title_ru": "Молоко"}],
    )
    assert len(merged) == 2
    by_unit = {row["unit"]: row["qty"] for row in merged}
    assert by_unit["g"] == 200
    assert by_unit["ml"] == 300
    same = merge_shopping(
        [{"canonical_id": "milk", "qty": 200, "unit": "g"}],
        [{"canonical_id": "milk", "qty": 50, "unit": "g"}],
    )
    assert len(same) == 1
    assert same[0]["qty"] == 250


def test_graph_broken_source_and_long_chain():
    recipe = SimpleNamespace(slug="r", title="R")
    component = SimpleNamespace(pk=1, code="c", title="C")
    box = SimpleNamespace(code="b1", component_id=1)
    start = SimpleNamespace(
        day=1,
        meal="lunch",
        mode="finish",
        container_ids=["b1"],
        source={"kind": "weekend"},
        recipe=recipe,
    )
    broken = SimpleNamespace(
        day=2,
        meal="lunch",
        mode="reheat",
        container_ids=[],
        source={"kind": "slot"},
        recipe=recipe,
    )
    data = KitData(
        kit=SimpleNamespace(),
        components=(component,),
        containers=(box,),
        slots=(start, broken),
    )
    graph = kit_graph(data)
    assert graph[0]["slots"] == [
        {
            "day": 1,
            "meal": "lunch",
            "slug": "r",
            "title": "R",
            "mode": "finish",
        }
    ]

    chain = [
        start,
        SimpleNamespace(
            day=2,
            meal="lunch",
            mode="reheat",
            container_ids=[],
            source={"kind": "slot", "day": 1, "meal": "lunch"},
            recipe=recipe,
        ),
        SimpleNamespace(
            day=3,
            meal="lunch",
            mode="reheat",
            container_ids=[],
            source={"kind": "slot", "day": 2, "meal": "lunch"},
            recipe=recipe,
        ),
        SimpleNamespace(
            day=4,
            meal="lunch",
            mode="reheat",
            container_ids=[],
            source={"kind": "slot", "day": 3, "meal": "lunch"},
            recipe=recipe,
        ),
    ]
    chained = kit_graph(
        KitData(
            kit=SimpleNamespace(),
            components=(component,),
            containers=(box,),
            slots=tuple(chain),
        )
    )
    assert [row["day"] for row in chained[0]["slots"]] == [1, 2, 3, 4]


def test_import_rejects_nan_infinity_and_fractional_ints():
    soup, wrap, extra = _trio("nan")
    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-nan")
    payload["components"][0]["qty"] = "NaN"
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-inf")
    payload["containers"][0]["qty"] = "Infinity"
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-bool")
    payload["servings_base"] = True
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-frac")
    payload["position"] = 1.5
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-sb")
    payload["servings_base"] = 0
    with pytest.raises(KitImportError):
        upsert_kit(payload)

    payload = _payload(soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-feeds")
    payload["slots"][0]["feeds_slots"] = 0
    with pytest.raises(KitImportError):
        upsert_kit(payload)


def test_container_rejects_component_from_other_kit():
    a = PrepKit.objects.create(slug="kit-a-own", title="A", status="published")
    b = PrepKit.objects.create(slug="kit-b-own", title="B", status="published")
    other = PrepComponent.objects.create(
        kit=b, code="foreign", title="Чужой", qty=1, unit="g"
    )
    box = PrepContainer(
        kit=a,
        code="box-x",
        label="X",
        component=other,
        qty=1,
        unit="g",
        place="fridge",
    )
    with pytest.raises(ValidationError):
        box.full_clean()


def test_used_earlier_no_leftover_thaw_text():
    soup, wrap, extra = _trio("thaw-nl")
    payload = _payload(
        soup=soup.slug, wrap=wrap.slug, extra=extra.slug, kit_id="kit-thaw-nl"
    )
    payload["containers"][1]["thaw_before_day"] = 2
    upsert_kit(payload, publish=True)
    client = APIClient()
    res = client.get(
        f"/api/recipes/{wrap.slug}/",
        {
            "prep": "kit-thaw-nl",
            "day": "2",
            "meal": "dinner",
            "no_leftover": "1",
        },
    )
    assert res.status_code == 200
    texts = [item["text"] for item in res.json()["prep"]]
    assert any("уже в холодильнике" in text and "утром" in text for text in texts)

    lunch = client.get(
        f"/api/recipes/{extra.slug}/",
        {
            "prep": "kit-thaw-nl",
            "day": "2",
            "meal": "lunch",
            "no_leftover": "1",
        },
    )
    assert lunch.status_code == 200
    lunch_texts = [item["text"] for item in lunch.json()["prep"]]
    assert any("достаньте" in text for text in lunch_texts)
    assert not any("уже в холодильнике — вы достали его утром" in text for text in lunch_texts)
