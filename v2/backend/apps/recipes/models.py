"""Recipe catalog models — live card on Recipe, not joined to revisions (DATA-MODEL)."""

from __future__ import annotations

from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, GeneratedField, Value
from django.db.models.functions import Coalesce, Concat

from apps.recipes.constants import (
    COOK_METHOD,
    CUT,
    DISH_TYPE,
    ENERGY_PROFILE,
    EQUIPMENT,
    HIGH_RISK,
    NUTRITION_BASIS,
    NUTRITION_SOURCE,
    PROTEIN_BASE,
    RECIPE_STATUS,
    SCALE_MODE,
    UNIT,
    USE_CASE,
    VARIANT_AXIS,
    YIELD_KIND,
)


def _choice(codes: frozenset[str]) -> list[tuple[str, str]]:
    return [(code, code) for code in sorted(codes)]


class NormalizeRu(models.Func):
    """Postgres normalize_ru(text) — ё→е, lower. Not unaccent."""

    function = "normalize_ru"
    output_field = models.TextField()
    arity = 1


class ToTsVector(models.Func):
    function = "to_tsvector"
    output_field = SearchVectorField()

    def __init__(self, config: str, expression):
        super().__init__(Value(config), expression)


class Recipe(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.TextField()
    protein_base = models.CharField(max_length=32, choices=_choice(PROTEIN_BASE))
    cook_method = models.CharField(max_length=32, choices=_choice(COOK_METHOD))
    dish_type = models.CharField(max_length=32, choices=_choice(DISH_TYPE))
    scale_mode = models.CharField(
        max_length=16, choices=_choice(SCALE_MODE), default="linear"
    )
    scalable = models.BooleanField(default=True)
    servings = models.PositiveIntegerField(null=True, blank=True)
    yield_weight_g = models.DecimalField(
        max_digits=8, decimal_places=1, null=True, blank=True
    )
    yield_kind = models.CharField(
        max_length=16, choices=_choice(YIELD_KIND), null=True, blank=True
    )
    summary = models.TextField(null=True, blank=True)
    source_name = models.TextField(null=True, blank=True)
    source_url = models.URLField(max_length=500, null=True, blank=True)
    source_type = models.TextField(null=True, blank=True)
    editorial_tested = models.BooleanField(default=False)
    high_risk_flags = ArrayField(
        models.CharField(max_length=32, choices=_choice(HIGH_RISK)),
        default=list,
        blank=True,
    )
    caution_text = models.TextField(null=True, blank=True)
    energy_profile = models.CharField(
        max_length=16, choices=_choice(ENERGY_PROFILE), default="standard"
    )
    equipment = models.CharField(
        max_length=32, choices=_choice(EQUIPMENT), null=True, blank=True
    )
    allowed_cuts = ArrayField(
        models.CharField(max_length=32, choices=_choice(CUT)),
        default=list,
        blank=True,
    )
    protein_bases_extra = ArrayField(
        models.CharField(max_length=32, choices=_choice(PROTEIN_BASE)),
        default=list,
        blank=True,
    )
    notes = models.JSONField(default=list, blank=True)
    prep = models.JSONField(default=list, blank=True)
    time_total_minutes = models.PositiveIntegerField(null=True, blank=True)
    time_active_minutes = models.PositiveIntegerField(null=True, blank=True)
    effort_level = models.PositiveSmallIntegerField(null=True, blank=True)
    washing_level = models.PositiveSmallIntegerField(null=True, blank=True)
    use_cases = ArrayField(
        models.CharField(max_length=32, choices=_choice(USE_CASE)),
        default=list,
        blank=True,
    )
    adaptations = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=_choice(RECIPE_STATUS), default="published"
    )
    # Denormalized for generated FTS: title + ingredient_titles + summary.
    ingredient_titles = models.TextField(default="", blank=True)
    search_vector = GeneratedField(
        expression=ToTsVector(
            "russian",
            NormalizeRu(
                Concat(
                    F("title"),
                    Value(" ", output_field=models.TextField()),
                    F("ingredient_titles"),
                    Value(" ", output_field=models.TextField()),
                    Coalesce(
                        F("summary"),
                        Value("", output_field=models.TextField()),
                    ),
                    output_field=models.TextField(),
                )
            ),
        ),
        output_field=SearchVectorField(),
        db_persist=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(
                OpClass(NormalizeRu("title"), name="gin_trgm_ops"),
                name="recipe_title_trgm",
            ),
        ]

    def __str__(self) -> str:
        return self.slug

    def clean(self) -> None:
        flags = list(self.high_risk_flags or [])
        if self.status == "published" and flags and not (self.caution_text or "").strip():
            raise ValidationError(
                "Нельзя публиковать high-risk рецепт без текста «Осторожно»."
            )
        unknown_flags = set(flags) - HIGH_RISK
        if unknown_flags:
            raise ValidationError(f"Неизвестный high-risk флаг: {sorted(unknown_flags)}")
        unknown_cases = set(self.use_cases or []) - USE_CASE
        if unknown_cases:
            raise ValidationError(f"Неизвестный use_case: {sorted(unknown_cases)}")
        for field in ("effort_level", "washing_level"):
            value = getattr(self, field)
            if value is not None and not 1 <= value <= 5:
                raise ValidationError(f"{field} должен быть 1–5.")
        total = self.time_total_minutes
        active = self.time_active_minutes
        if total is not None and active is not None and active > total:
            raise ValidationError("active_minutes не больше total_minutes.")
        if self.yield_weight_g is not None and self.yield_weight_g <= 0:
            raise ValidationError("yield_weight_g должен быть > 0.")
        if self.yield_kind and self.yield_kind not in YIELD_KIND:
            raise ValidationError(f"Неизвестный yield_kind: {self.yield_kind}")
        if self.yield_kind and self.yield_weight_g is None:
            raise ValidationError("yield_kind без yield_weight_g.")
        extra = list(self.protein_bases_extra or [])
        unknown_extra = set(extra) - PROTEIN_BASE
        if unknown_extra:
            raise ValidationError(f"Неизвестная extra-основа: {sorted(unknown_extra)}")
        if self.protein_base in extra:
            raise ValidationError("protein_bases_extra не дублирует protein_base.")

    def anchor_row(self) -> RecipeIngredient | None:
        return self.ingredients.filter(is_anchor=True).select_related("ingredient").first()


class RecipeVariant(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="variants")
    axis = models.CharField(max_length=16, choices=_choice(VARIANT_AXIS))
    code = models.SlugField(max_length=80)
    title = models.TextField()
    has_delta = models.BooleanField(default=False)
    legacy_text = models.TextField(null=True, blank=True)
    ingredient_delta = models.JSONField(null=True, blank=True)
    step_delta = models.JSONField(null=True, blank=True)
    allergen_delta = models.JSONField(null=True, blank=True)
    high_risk_delta = models.JSONField(default=dict, blank=True)
    cook_method_override = models.CharField(
        max_length=32, choices=_choice(COOK_METHOD), null=True, blank=True
    )
    protein_base_override = models.CharField(
        max_length=32, choices=_choice(PROTEIN_BASE), null=True, blank=True
    )
    equipment = models.CharField(
        max_length=32, choices=_choice(EQUIPMENT), null=True, blank=True
    )
    caution_text_override = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["axis", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "axis", "code"],
                name="recipes_variant_unique_axis_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.recipe.slug}:{self.axis}:{self.code}"


class RecipeRevision(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="revisions"
    )
    payload_json = models.JSONField()
    status = models.CharField(max_length=16, choices=_choice(RECIPE_STATUS))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Ingredient(models.Model):
    canonical_id = models.SlugField(max_length=80, unique=True)
    title = models.TextField()
    aliases = ArrayField(models.TextField(), default=list, blank=True)
    density_g_per_ml = models.DecimalField(
        max_digits=8, decimal_places=3, null=True, blank=True
    )
    kcal_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    protein_g_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    fat_g_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    carbs_g_per_100g = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    nutrition_basis = models.CharField(
        max_length=16, choices=_choice(NUTRITION_BASIS), null=True, blank=True
    )
    nutrition_source = models.CharField(
        max_length=32, choices=_choice(NUTRITION_SOURCE), null=True, blank=True
    )
    nutrition_source_id = models.TextField(null=True, blank=True)
    g_per_tsp = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_tbsp = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_pcs = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_clove = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_bunch = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    g_per_slice = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    allergens_contains = ArrayField(models.CharField(max_length=32), default=list, blank=True)
    allergens_may_contain = ArrayField(
        models.CharField(max_length=32), default=list, blank=True
    )
    allergens_unknown = ArrayField(models.CharField(max_length=32), default=list, blank=True)

    def __str__(self) -> str:
        return self.canonical_id


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, related_name="recipe_lines"
    )
    position = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    amount_max = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=16, choices=_choice(UNIT))
    detail = models.TextField(null=True, blank=True)
    scale_mode = models.CharField(
        max_length=16, choices=_choice(SCALE_MODE), default="linear"
    )
    scalable = models.BooleanField(default=True)
    is_anchor = models.BooleanField(default=False)
    optional = models.BooleanField(default=False)
    nutrition_exclude = models.BooleanField(default=False)
    nutrition_factor = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    choice_group = models.TextField(null=True, blank=True)
    display_name = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe"],
                condition=models.Q(is_anchor=True),
                name="recipes_one_anchor_per_recipe",
            ),
        ]

    def clean(self) -> None:
        if self.unit in {"to_taste", "pinch"}:
            if self.amount is not None:
                raise ValidationError("Для «по вкусу»/щепотки amount должен быть пустым.")
            if self.scalable:
                raise ValidationError("to_taste/pinch не масштабируются.")
        if self.nutrition_exclude and self.nutrition_factor is not None:
            raise ValidationError("nutrition_factor не вместе с nutrition_exclude.")
        if self.nutrition_factor is not None and not (
            Decimal("0.01") <= self.nutrition_factor <= Decimal("1")
        ):
            raise ValidationError("nutrition_factor должен быть 0.01–1.")


class SubstitutionRule(models.Model):
    from_ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="substitutions_from"
    )
    to_ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="substitutions_to"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="substitution_rules",
        null=True,
        blank=True,
    )
    quality = models.DecimalField(max_digits=3, decimal_places=2)
    forbidden = models.BooleanField(default=False)
    note = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_ingredient", "to_ingredient"],
                condition=models.Q(recipe__isnull=True),
                name="recipes_sub_unique_global",
            ),
            models.UniqueConstraint(
                fields=["from_ingredient", "to_ingredient", "recipe"],
                condition=models.Q(recipe__isnull=False),
                name="recipes_sub_unique_recipe",
            ),
        ]

    def __str__(self) -> str:
        scope = self.recipe.slug if self.recipe_id else "global"
        return f"{self.from_ingredient_id}->{self.to_ingredient_id}@{scope}"


class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    position = models.PositiveIntegerField()
    text = models.TextField()
    timer_seconds = models.PositiveIntegerField(null=True, blank=True)
    timer_label = models.TextField(null=True, blank=True)
    timer_note = models.TextField(null=True, blank=True)
    pull_internal_temperature_c = models.PositiveIntegerField(null=True, blank=True)
    target_internal_temperature_c = models.PositiveIntegerField(null=True, blank=True)
    hold_seconds = models.PositiveIntegerField(null=True, blank=True)
    equipment_note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["position"]

    def clean(self) -> None:
        if (
            self.pull_internal_temperature_c is not None
            and self.target_internal_temperature_c is None
        ):
            raise ValidationError("Заполнен pull без target — ошибка SAFETY.")
