import random
from hashlib import sha1

from django.core.cache import cache
from django.db.models import Exists, OuterRef, Prefetch, Q
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recipes.api.query_serializers import (
    RecipeDetailQuerySerializer,
    RecipeListQuerySerializer,
    RecommendationQuerySerializer,
)
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeVariant
from apps.recipes.pantry_vocab import CANONICAL_INGREDIENT_LABEL_RU, groups_to_expand
from apps.recipes.serializers import serialize_recipe_detail, serialize_recipe_list_item
from apps.recipes.services.assemble import (
    assemble_recipe,
    catalog_allergens,
    catalog_protein_bases,
    catalog_protein_variants,
    pick_anchor,
)
from apps.recipes.services.pantry import (
    fill_have_from_groups,
    resolve_pantry_text,
)
from apps.recipes.services.scale import resolve_scale
from apps.recipes.services.search import apply_catalog_search
from apps.recipes.services.solve import (
    MAX_CANDIDATES,
    assign_buckets,
    build_board,
    is_standalone_dish,
    serialize_solution,
    solve_recipe,
)
from apps.recipes.services.substitutions import stored_rules_from_db

REC_CACHE_TTL = 45
DETAIL_CACHE_TTL = 10 * 60


def _solver_card(recipe) -> dict:
    return {
        "has_delta_variants": any(
            item.axis == "addon" and item.has_delta for item in recipe.variants.all()
        ),
        "allowed_cuts": list(recipe.allowed_cuts or []),
        "protein_bases": catalog_protein_bases(recipe),
        "protein_variants": catalog_protein_variants(recipe),
    }


def _rec_cache_key(
    *,
    protein: list[str],
    method: list[str],
    dish: list[str],
    equipment: list[str],
    cuts: list[str],
    without: list[str],
    have: list[str],
    have_groups: list[str],
    intents: list[str],
) -> str:
    raw = "|".join(
        [
            ",".join(protein),
            ",".join(method),
            ",".join(dish),
            ",".join(equipment),
            ",".join(cuts),
            ",".join(without),
            ",".join(sorted(have)),
            ",".join(have_groups),
            ",".join(intents),
        ]
    )
    return "rec:v4:" + sha1(raw.encode("utf-8")).hexdigest()


def _detail_cache_key(
    recipe,
    *,
    variant: str | None,
    equipment: str | None,
    servings,
    anchor_weight,
) -> str:
    serv = "" if servings is None else str(servings)
    anc = "" if anchor_weight is None else str(anchor_weight)
    version = getattr(recipe, "content_version", 0)
    return (
        f"recipe-detail:{recipe.slug}:v{version}"
        f":variant={variant or ''}:equipment={equipment or ''}"
        f":servings={serv}:anchor={anc}"
    )


def _idle_recommendations(filters: dict) -> dict:
    return {
        "filters": filters,
        "featured": None,
        "alternatives": [],
        "buckets": {"now": [], "almost": [], "best": []},
        "results": [],
    }


class CatalogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 500


def _published():
    return Recipe.objects.filter(status="published").prefetch_related(
        Prefetch(
            "ingredients",
            queryset=RecipeIngredient.objects.select_related("ingredient").order_by(
                "position"
            ),
        ),
        "steps",
        "variants",
    )


def _list_cards():
    return Recipe.objects.filter(status="published").prefetch_related(
        Prefetch(
            "ingredients",
            queryset=RecipeIngredient.objects.select_related("ingredient").order_by(
                "position"
            ),
        ),
        "variants",
    )


def _solver_qs(*, with_ingredients: bool = False):
    """Published families for ranking. Snapshots live on the row; steps are unused."""
    qs = Recipe.objects.filter(status="published").prefetch_related("variants")
    if with_ingredients:
        qs = qs.prefetch_related(
            Prefetch(
                "ingredients",
                queryset=RecipeIngredient.objects.select_related("ingredient").order_by(
                    "position"
                ),
            )
        )
    return qs


def _apply_filters(qs, filters: dict, *, with_search: bool):
    protein = filters.get("protein_base") or []
    method = filters.get("cook_method") or []
    dish = filters.get("dish_type") or []
    equipment = filters.get("equipment") or []
    cuts = filters.get("cuts") or []
    if protein:
        qs = qs.filter(
            Q(protein_base__in=protein)
            | Q(protein_bases_extra__overlap=protein)
            | Exists(
                RecipeVariant.objects.filter(
                    recipe_id=OuterRef("pk"),
                    axis="addon",
                    has_delta=True,
                    protein_base_override__in=protein,
                )
            )
        )
    if method:
        qs = qs.filter(
            Q(cook_method__in=method)
            | Exists(
                RecipeVariant.objects.filter(
                    recipe_id=OuterRef("pk"),
                    axis="equipment",
                    has_delta=True,
                    cook_method_override__in=method,
                )
            )
        )
    if dish:
        qs = qs.filter(dish_type__in=dish)
    if equipment:
        qs = qs.filter(
            Q(equipment__in=equipment)
            | Exists(
                RecipeVariant.objects.filter(
                    recipe_id=OuterRef("pk"),
                    axis="equipment",
                    has_delta=True,
                ).filter(
                    Q(equipment__in=equipment)
                    | (Q(equipment__isnull=True) & Q(code__in=equipment))
                )
            )
        )
    if cuts:
        qs = qs.filter(allowed_cuts__overlap=cuts)
    if with_search:
        q = (filters.get("q") or "").strip()
        if q:
            qs = apply_catalog_search(qs, q)
    return qs.distinct()


def _exclude_allergens(recipes: list[Recipe], codes: list[str]) -> list[Recipe]:
    if not codes:
        return recipes
    kept = []
    for recipe in recipes:
        allergens = catalog_allergens(recipe)
        hit = False
        for code in codes:
            if code in allergens.get("contains", []) or code in allergens.get("unknown", []):
                hit = True
                break
        if not hit:
            kept.append(recipe)
    return kept


class RecipeListView(APIView):
    def get(self, request):
        query = RecipeListQuerySerializer(
            data=request.query_params, context={"request": request}
        )
        query.is_valid(raise_exception=True)
        filters = query.validated_data
        qs = _apply_filters(_list_cards(), filters, with_search=True)
        without = filters["without"]
        sample_n = filters["sample"]
        if sample_n is not None:
            if without:
                recipes = _exclude_allergens(list(qs), without)
                recipes = random.sample(recipes, min(sample_n, len(recipes)))
            else:
                pks = list(qs.order_by("?").values_list("pk", flat=True)[:sample_n])
                by_id = {recipe.pk: recipe for recipe in _list_cards().filter(pk__in=pks)}
                recipes = [by_id[pk] for pk in pks if pk in by_id]
            data = [serialize_recipe_list_item(recipe) for recipe in recipes]
            return Response({"count": len(data), "next": None, "previous": None, "results": data})
        qs = qs.order_by("title")
        paginator = CatalogPagination()
        if without:
            recipes = _exclude_allergens(list(qs), without)
            page = paginator.paginate_queryset(recipes, request, view=self)
        else:
            page = paginator.paginate_queryset(qs, request, view=self)
        data = [serialize_recipe_list_item(recipe) for recipe in page]
        return paginator.get_paginated_response(data)


class RecipeDetailView(APIView):
    def get(self, request, slug: str):
        query = RecipeDetailQuerySerializer(
            data=request.query_params, context={"request": request}
        )
        query.is_valid(raise_exception=True)
        params = query.validated_data
        recipe = _published().filter(slug=slug).first()
        if recipe is None:
            raise NotFound("Рецепт не найден.")
        from apps.prep.services.context import resolve_prep_for_recipe

        prep_pack = resolve_prep_for_recipe(recipe, request)
        variant = params["variant"]
        equipment = params["equipment"]
        servings = None if prep_pack else params["servings"]
        anchor_weight = None if prep_pack else params["anchor_weight"]
        cache_key = _detail_cache_key(
            recipe,
            variant=variant,
            equipment=equipment,
            servings=servings,
            anchor_weight=anchor_weight,
        )
        cached = cache.get(cache_key)
        if cached is None:
            assembled = assemble_recipe(recipe, variant_code=variant, equipment_code=equipment)
            anchor = pick_anchor(assembled.ingredients)
            scale = resolve_scale(
                recipe_scalable=recipe.scalable,
                recipe_servings=recipe.servings,
                anchor_amount=anchor["amount"] if anchor else None,
                anchor_unit=anchor["unit"] if anchor else None,
                servings=servings,
                anchor_weight=anchor_weight,
                anchor_name=(anchor.get("name") if anchor else None),
            )
            cached = serialize_recipe_detail(recipe, assembled, scale)
            cache.set(cache_key, cached, DETAIL_CACHE_TTL)
        data = dict(cached)
        if prep_pack:
            data["steps"] = prep_pack["steps"]
            data["prep"] = prep_pack["prep"]
            data["prep_context"] = prep_pack["prep_context"]
            data["scaling"] = prep_pack["scaling"]
        return Response(data)


class IngredientListView(APIView):
    def get(self, request):
        from apps.recipes.models import Ingredient
        from apps.recipes.pantry_vocab import (
            CANONICAL_INGREDIENT_LABEL_RU,
            HAVE_GROUP_CHILDREN,
            HAVE_GROUP_LABEL_RU,
            HAVE_UI_GROUPS,
            chip_title,
            items_for_have_group,
        )

        text = (request.query_params.get("text") or "").strip()
        titles = {
            **CANONICAL_INGREDIENT_LABEL_RU,
            **dict(Ingredient.objects.values_list("canonical_id", "title")),
        }
        known = set(titles)
        if text:
            found, unknown = resolve_pantry_text(text, titles=titles, known=known)
            items = [{"canonical_id": cid, "title": chip_title(cid, titles)} for cid in found]
            return Response({"items": items, "unknown": unknown})

        def group_payload(code: str) -> dict:
            children = HAVE_GROUP_CHILDREN.get(code, ())
            payload: dict = {
                "id": code,
                "title": HAVE_GROUP_LABEL_RU[code],
                "items": [
                    {
                        "canonical_id": cid,
                        "title": chip_title(
                            cid, {**titles, **CANONICAL_INGREDIENT_LABEL_RU}
                        ),
                    }
                    for cid in items_for_have_group(code)
                ],
            }
            if children:
                payload["items"] = []
                payload["children"] = [group_payload(child) for child in children]
            return payload

        return Response({"groups": [group_payload(code) for code in HAVE_UI_GROUPS]})


class RecommendationListView(APIView):
    def get(self, request):
        query = RecommendationQuerySerializer(
            data=request.query_params, context={"request": request}
        )
        query.is_valid(raise_exception=True)
        params = query.validated_data
        protein = params["protein_base"]
        method = params["cook_method"]
        dish = params["dish_type"]
        equipment = params["equipment"]
        cuts = params["cuts"]
        without = params["without"]
        have = list(params["have"])
        explicit_have = list(have)
        have_groups = params["have_group"]
        have = fill_have_from_groups(have, have_groups)
        intents = params["intent"]
        have = list(dict.fromkeys(have))
        filters = {
            "protein_base": protein,
            "cook_method": method,
            "dish_type": dish,
            "equipment": equipment,
            "cuts": cuts,
            "have": have,
            "have_group": have_groups,
            "intent": intents,
        }
        asked = bool(
            protein
            or method
            or dish
            or equipment
            or cuts
            or without
            or have
            or groups_to_expand(have_groups)
            or intents
        )
        if not asked:
            return Response(_idle_recommendations(filters))
        cache_key = _rec_cache_key(
            protein=protein,
            method=method,
            dish=dish,
            equipment=equipment,
            cuts=cuts,
            without=without,
            have=have,
            have_groups=have_groups,
            intents=intents,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        qs = _apply_filters(
            _solver_qs(with_ingredients=bool(without)),
            params,
            with_search=False,
        )
        recipes = _exclude_allergens(list(qs), without)[:MAX_CANDIDATES]
        rules = stored_rules_from_db() if have else []
        titles = {
            **CANONICAL_INGREDIENT_LABEL_RU,
            **dict(Ingredient.objects.values_list("canonical_id", "title")),
        }
        solutions = []
        for recipe in recipes:
            item = _solver_card(recipe)
            solved = solve_recipe(
                recipe,
                filter_protein=protein,
                filter_method=method,
                filter_dish=dish,
                filter_equipment=equipment,
                have=have,
                catalog_item=item,
                rules=rules,
                titles=titles,
                intents=intents,
                explicit_have=explicit_have,
            )
            if solved is not None:
                solutions.append(solved)
        solutions.sort(
            key=lambda row: (
                (
                    int(not is_standalone_dish(row.dish_type)),
                    -int(row.have_all),
                    -row.have_used,
                    -row.pantry_hits,
                    -row.score,
                    row.title,
                )
                if have
                else (
                    int(not is_standalone_dish(row.dish_type)),
                    -row.score,
                    row.title,
                )
            )
        )
        buckets = assign_buckets(solutions, has_have=bool(have))
        featured, alternatives = build_board(solutions, buckets, has_have=bool(have))
        if have:
            visible = buckets["now"] + buckets["almost"] + buckets["best"]
        else:
            visible = [featured] if featured else []
            visible.extend(item for _, item in alternatives)
        payload = {
            "filters": filters,
            "featured": serialize_solution(featured) if featured else None,
            "alternatives": [
                {**serialize_solution(item), "label": label}
                for label, item in alternatives
            ],
            "buckets": {
                "now": [serialize_solution(item) for item in buckets["now"]],
                "almost": [serialize_solution(item) for item in buckets["almost"]],
                "best": [serialize_solution(item) for item in buckets["best"]],
            },
            "results": [serialize_solution(item) for item in visible],
        }
        cache.set(cache_key, payload, REC_CACHE_TTL)
        return Response(payload)
