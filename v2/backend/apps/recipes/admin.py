from django.contrib import admin

from apps.recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeRevision,
    RecipeStep,
    RecipeVariant,
    SubstitutionRule,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 0


class RecipeVariantInline(admin.TabularInline):
    model = RecipeVariant
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title",
        "protein_base",
        "cook_method",
        "dish_type",
        "equipment",
        "status",
        "editorial_tested",
    )
    list_filter = ("protein_base", "cook_method", "dish_type", "equipment", "status")
    search_fields = ("slug", "title")
    inlines = [RecipeIngredientInline, RecipeStepInline, RecipeVariantInline]
    readonly_fields = ("search_vector", "updated_at")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("canonical_id", "title")
    search_fields = ("canonical_id", "title")


@admin.register(RecipeVariant)
class RecipeVariantAdmin(admin.ModelAdmin):
    list_display = ("recipe", "axis", "code", "has_delta")
    list_filter = ("axis", "has_delta")


@admin.register(SubstitutionRule)
class SubstitutionRuleAdmin(admin.ModelAdmin):
    list_display = ("from_ingredient", "to_ingredient", "quality", "forbidden", "recipe")
    list_filter = ("forbidden",)
    search_fields = (
        "from_ingredient__canonical_id",
        "to_ingredient__canonical_id",
    )


@admin.register(RecipeRevision)
class RecipeRevisionAdmin(admin.ModelAdmin):
    list_display = ("recipe", "status", "created_at")
