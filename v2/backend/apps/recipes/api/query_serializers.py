"""DRF query serializers for catalog, detail, and recommendations."""

from __future__ import annotations

from rest_framework import serializers

from apps.recipes.query import (
    parse_codes,
    parse_have,
    parse_have_groups,
    parse_intent,
    parse_optional_decimal,
    parse_sample,
    parse_without_allergens,
)


class RecipeListQuerySerializer(serializers.Serializer):
    protein_base = serializers.CharField(required=False)
    cook_method = serializers.CharField(required=False)
    dish_type = serializers.CharField(required=False)
    equipment = serializers.CharField(required=False)
    cuts = serializers.CharField(required=False)
    q = serializers.CharField(required=False, allow_blank=True)
    without = serializers.CharField(required=False)
    exclude_allergen = serializers.CharField(required=False)
    sample = serializers.IntegerField(required=False, min_value=1, max_value=24)

    def to_internal_value(self, data):
        request = self.context["request"]
        return {
            "protein_base": parse_codes(request, "protein_base"),
            "cook_method": parse_codes(request, "cook_method"),
            "dish_type": parse_codes(request, "dish_type"),
            "equipment": parse_codes(request, "equipment"),
            "cuts": parse_codes(request, "cuts"),
            "q": (request.query_params.get("q") or "").strip(),
            "without": parse_without_allergens(request),
            "sample": parse_sample(request),
        }


class RecipeDetailQuerySerializer(serializers.Serializer):
    variant = serializers.CharField(required=False, allow_blank=True)
    equipment = serializers.CharField(required=False, allow_blank=True)
    servings = serializers.DecimalField(
        required=False, max_digits=8, decimal_places=2, min_value=1
    )
    anchor_weight = serializers.DecimalField(
        required=False, max_digits=8, decimal_places=2, min_value=1
    )

    def to_internal_value(self, data):
        request = self.context["request"]
        variant = (request.query_params.get("variant") or "").strip() or None
        equipment = (request.query_params.get("equipment") or "").strip() or None
        return {
            "variant": variant,
            "equipment": equipment,
            "servings": parse_optional_decimal(request, "servings"),
            "anchor_weight": parse_optional_decimal(request, "anchor_weight"),
        }


class RecommendationQuerySerializer(serializers.Serializer):
    protein_base = serializers.CharField(required=False)
    cook_method = serializers.CharField(required=False)
    dish_type = serializers.CharField(required=False)
    equipment = serializers.CharField(required=False)
    cuts = serializers.CharField(required=False)
    have = serializers.CharField(required=False)
    have_group = serializers.CharField(required=False)
    intent = serializers.CharField(required=False)
    without = serializers.CharField(required=False)
    exclude_allergen = serializers.CharField(required=False)

    def to_internal_value(self, data):
        request = self.context["request"]
        return {
            "protein_base": parse_codes(request, "protein_base"),
            "cook_method": parse_codes(request, "cook_method"),
            "dish_type": parse_codes(request, "dish_type"),
            "equipment": parse_codes(request, "equipment"),
            "cuts": parse_codes(request, "cuts"),
            "have": parse_have(request),
            "have_group": parse_have_groups(request),
            "intent": parse_intent(request),
            "without": parse_without_allergens(request),
        }
