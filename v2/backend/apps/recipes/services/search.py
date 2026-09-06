"""Catalog FTS: russian config + normalize_ru. Do not use icontains lookups."""

from __future__ import annotations

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, FloatField, Func, Q, TextField, Value

from apps.recipes.services.allergens import normalize_ru


class PgNormalizeRu(Func):
    function = "normalize_ru"
    output_field = TextField()
    arity = 1


class Similarity(Func):
    function = "similarity"
    output_field = FloatField()
    arity = 2


def apply_catalog_search(queryset, raw_q: str):
    qn = normalize_ru(raw_q).strip()
    if not qn:
        return queryset
    query = SearchQuery(qn, config="russian", search_type="plain")
    return (
        queryset.annotate(
            search_rank=SearchRank(F("search_vector"), query),
            title_trgm=Similarity(PgNormalizeRu(F("title")), Value(qn)),
        )
        .filter(Q(search_vector=query) | Q(title_trgm__gt=0.2))
        .order_by("-search_rank", "-title_trgm", "title")
    )
