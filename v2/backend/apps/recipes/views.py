from django.db.models import Exists, OuterRef, Prefetch, Q
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeVariant
from apps.recipes.query import (
    parse_codes,
    parse_have,
    parse_have_groups,
    parse_intent,
    parse_optional_decimal,
    parse_without_allergens,
)
from apps.recipes.serializers import serialize_recipe_detail, serialize_recipe_list_item
from apps.recipes.services.assemble import assemble_recipe, catalog_allergens, pick_anchor
from apps.recipes.services.scale import resolve_scale
from apps.recipes.services.search import apply_catalog_search
from apps.recipes.pantry_vocab import CANONICAL_INGREDIENT_LABEL_RU, groups_to_expand
from apps.recipes.services.pantry import (
    expand_have_group,
    resolve_pantry_text,
)
from apps.recipes.services.solve import (
    assign_buckets,
    build_board,
    is_standalone_dish,
    serialize_solution,
    solve_recipe,
)
from apps.recipes.services.substitutions import stored_rules_from_db


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


def _apply_filters(qs, request, *, with_search: bool):
    protein = parse_codes(request, "protein_base")
    method = parse_codes(request, "cook_method")
    dish = parse_codes(request, "dish_type")
    equipment = parse_codes(request, "equipment")
    cuts = parse_codes(request, "cuts")
    if protein:
        qs = qs.filter(protein_base__in=protein)
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
                    equipment__in=equipment,
                )
            )
        )
    if cuts:
        qs = qs.filter(allowed_cuts__overlap=cuts)
    if with_search:
        q = request.query_params.get("q", "").strip()
        if q:
            qs = apply_catalog_search(qs, q)
    return qs.distinct(), protein, method, dish, equipment, cuts


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
        qs, _, _, _, _, _ = _apply_filters(_published(), request, with_search=True)
        qs = qs.order_by("title")
        without = parse_without_allergens(request)
        recipes = _exclude_allergens(list(qs), without)
        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        paginator.page_size = 20
        page = paginator.paginate_queryset(recipes, request, view=self)
        data = [serialize_recipe_list_item(recipe) for recipe in page]
        return paginator.get_paginated_response(data)


class RecipeDetailView(APIView):
    def get(self, request, slug: str):
        recipe = _published().filter(slug=slug).first()
        if recipe is None:
            raise NotFound("Рецепт не найден.")
        from apps.prep.services.context import resolve_prep_for_recipe

        prep_pack = resolve_prep_for_recipe(recipe, request)
        variant = (request.query_params.get("variant") or "").strip() or None
        equipment = (request.query_params.get("equipment") or "").strip() or None
        assembled = assemble_recipe(recipe, variant_code=variant, equipment_code=equipment)
        servings = None if prep_pack else parse_optional_decimal(request, "servings")
        anchor_weight = None if prep_pack else parse_optional_decimal(request, "anchor_weight")
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
        data = serialize_recipe_detail(recipe, assembled, scale)
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
            items_for_have_group,
            shopping_label,
        )

        text = (request.query_params.get("text") or "").strip()
        titles = {
            **CANONICAL_INGREDIENT_LABEL_RU,
            **dict(Ingredient.objects.values_list("canonical_id", "title")),
        }
        known = set(titles)
        if text:
            found, unknown = resolve_pantry_text(text, titles=titles, known=known)
            items = [{"canonical_id": cid, "title": shopping_label(cid, titles)} for cid in found]
            return Response({"items": items, "unknown": unknown})

        def group_payload(code: str) -> dict:
            children = HAVE_GROUP_CHILDREN.get(code, ())
            payload: dict = {
                "id": code,
                "title": HAVE_GROUP_LABEL_RU[code],
                "items": [
                    {"canonical_id": cid, "title": shopping_label(cid, {**titles, **CANONICAL_INGREDIENT_LABEL_RU})}
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
        qs, protein, method, dish, equipment, cuts = _apply_filters(
            _published(), request, with_search=False
        )
        without = parse_without_allergens(request)
        have = parse_have(request)
        explicit_have = list(have)
        have_groups = parse_have_groups(request)
        chosen = set(have)
        for group in groups_to_expand(have_groups):
            group_ids = expand_have_group(group)
            if chosen & set(group_ids):
                continue
            for cid in group_ids:
                if cid not in have:
                    have.append(cid)
        intents = parse_intent(request)
        recipes = _exclude_allergens(list(qs), without)
        rules = stored_rules_from_db() if have else []
        titles = {
            **CANONICAL_INGREDIENT_LABEL_RU,
            **dict(Ingredient.objects.values_list("canonical_id", "title")),
        }
        have = list(dict.fromkeys(have))
        solutions = []
        for recipe in recipes:
            item = serialize_recipe_list_item(recipe)
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
        visible = (
            buckets["now"] + buckets["almost"] + buckets["best"]
            if have
            else solutions
        )
        return Response(
            {
                "filters": {
                    "protein_base": protein,
                    "cook_method": method,
                    "dish_type": dish,
                    "equipment": equipment,
                    "cuts": cuts,
                    "have": have,
                    "have_group": have_groups,
                    "intent": intents,
                },
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
        )
