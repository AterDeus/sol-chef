from django.urls import path

from apps.recipes.views import (
    IngredientListView,
    RecipeDetailView,
    RecipeListView,
    RecommendationListView,
)

urlpatterns = [
    path("recipes/", RecipeListView.as_view(), name="recipe-list"),
    path("recipes/<slug:slug>/", RecipeDetailView.as_view(), name="recipe-detail"),
    path("recommendations/", RecommendationListView.as_view(), name="recommendations"),
    path("ingredients/", IngredientListView.as_view(), name="ingredient-list"),
]
