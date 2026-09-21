"""Recipe catalog models — live card on Recipe, not joined to revisions (DATA-MODEL)."""

from __future__ import annotations

from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex, OpClass
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, GeneratedField, Q, Value
from django.db.models.functions import Coalesce, Concat

from apps.recipes.domain.enums import (
    CookMethod,
    Cut,
    DishType,
    EnergyProfile,
    Equipment,
    HighRisk,
    NutritionBasis,
    NutritionSource,
    ProteinBase,
    RecipeStatus,
    ScaleMode,
    Unit,
    UseCase,
    VariantAxis,
    YieldKind,
)


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
    protein_base = models.CharField(max_length=32, choices=ProteinBase.choices)
    cook_method = models.CharField(max_length=32, choices=CookMethod.choices)
    dish_type = models.CharField(max_length=32, choices=DishType.choices)
    scale_mode = models.CharField(
        max_length=16, choices=ScaleMode.choices, default=ScaleMode.LINEAR
    )
    scalable = models.BooleanField(default=True)
    servings = models.PositiveIntegerField(null=True, blank=True)
    yield_weight_g = models.DecimalField(
        max_digits=8, decimal_places=1, null=True, blank=True
    )
    yield_kind = models.CharField(
        max_length=16, choices=YieldKind.choices, null=True, blank=True
    )
    summary = models.TextField(null=True, blank=True)
    source_name = models.TextField(null=True, blank=True)
    source_url = models.URLField(max_length=500, null=True, blank=True)
    source_type = models.TextField(null=True, blank=True)
    editorial_tested = models.BooleanField(default=False)
    high_risk_flags = ArrayField(
        models.CharField(max_length=32, choices=HighRisk.choices),
        default=list,
        blank=True,
    )
    caution_text = models.TextField(null=True, blank=True)
    energy_profile = models.CharField(
        max_length=16, choices=EnergyProfile.choices, default=EnergyProfile.STANDARD
    )
    equipment = models.CharField(
        max_length=32, choices=Equipment.choices, null=True, blank=True
    )
    allowed_cuts = ArrayField(
        models.CharField(max_length=32, choices=Cut.choices),
        default=list,
        blank=True,
    )
    protein_bases_extra = ArrayField(
        models.CharField(max_length=32, choices=ProteinBase.choices),
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
        models.CharField(max_length=32, choices=UseCase.choices),
        default=list,
        blank=True,
    )
    adaptations = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=16, choices=RecipeStatus.choices, default=RecipeStatus.DRAFT
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
    axis_snapshots = models.JSONField(default=list, blank=True)
    content_version = models.PositiveIntegerField(default=1)
    snapshot_version = models.PositiveIntegerField(default=0)
    snapshots_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            GinIndex(fields=["search_vector"]),
            GinIndex(
                OpClass(NormalizeRu("title"), name="gin_trgm_ops"),
                name="recipe_title_trgm",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(servings__isnull=True) | Q(servings__gte=1),
                name="recipe_servings_positive",
            ),
            models.CheckConstraint(
                condition=Q(yield_weight_g__isnull=True) | Q(yield_weight_g__gt=0),
                name="recipe_yield_weight_positive",
            ),
            models.CheckConstraint(
                condition=Q(time_total_minutes__isnull=True) | Q(time_total_minutes__gte=1),
                name="recipe_total_time_positive",
            ),
            models.CheckConstraint(
                condition=Q(time_active_minutes__isnull=True)
                | Q(time_active_minutes__gte=0),
                name="recipe_active_time_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(time_total_minutes__isnull=True)
                | Q(time_active_minutes__isnull=True)
                | Q(time_active_minutes__lte=F("time_total_minutes")),
                name="recipe_active_time_not_greater_total",
            ),
        ]

    def __str__(self) -> str:
        return self.slug

    def clean(self) -> None:
        flags = list(self.high_risk_flags or [])
        if self.status == RecipeStatus.PUBLISHED and flags and not (
            self.caution_text or ""
        ).strip():
            raise ValidationError(
                "Нельзя публиковать high-risk рецепт без текста «Осторожно»."
            )
        unknown_flags = set(flags) - set(HighRisk.values)
        if unknown_flags:
            raise ValidationError(f"Неизвестный high-risk флаг: {sorted(unknown_flags)}")
        unknown_cases = set(self.use_cases or []) - set(UseCase.values)
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
        if self.yield_kind and self.yield_kind not in YieldKind.values:
            raise ValidationError(f"Неизвестный yield_kind: {self.yield_kind}")
        if self.yield_kind and self.yield_weight_g is None:
            raise ValidationError("yield_kind без yield_weight_g.")
        extra = list(self.protein_bases_extra or [])
        unknown_extra = set(extra) - set(ProteinBase.values)
        if unknown_extra:
            raise ValidationError(f"Неизвестная extra-основа: {sorted(unknown_extra)}")
        if self.protein_base in extra:
            raise ValidationError("protein_bases_extra не дублирует protein_base.")

    def anchor_row(self) -> RecipeIngredient | None:
        return self.ingredients.filter(is_anchor=True).select_related("ingredient").first()


class RecipeVariant(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="variants")
    axis = models.CharField(max_length=16, choices=VariantAxis.choices)
    code = models.SlugField(max_length=80)
    title = models.TextField()
    has_delta = models.BooleanField(default=False)
    legacy_text = models.TextField(null=True, blank=True)
    ingredient_delta = models.JSONField(null=True, blank=True)
    step_delta = models.JSONField(null=True, blank=True)
    allergen_delta = models.JSONField(null=True, blank=True)
    high_risk_delta = models.JSONField(default=dict, blank=True)
    cook_method_override = models.CharField(
        max_length=32, choices=CookMethod.choices, null=True, blank=True
    )
    protein_base_override = models.CharField(
        max_length=32, choices=ProteinBase.choices, null=True, blank=True
    )
    equipment = models.CharField(
        max_length=32, choices=Equipment.choices, null=True, blank=True
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
    number = models.PositiveIntegerField()
    payload_json = models.JSONField()
    payload_hash = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(max_length=16, choices=RecipeStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-number", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "number"],
                name="recipe_revision_number_unique",
            ),
        ]


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
        max_length=16, choices=NutritionBasis.choices, null=True, blank=True
    )
    nutrition_source = models.CharField(
        max_length=32, choices=NutritionSource.choices, null=True, blank=True
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
    unit = models.CharField(max_length=16, choices=Unit.choices)
    detail = models.TextField(null=True, blank=True)
    scale_mode = models.CharField(
        max_length=16, choices=ScaleMode.choices, default=ScaleMode.LINEAR
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
            models.UniqueConstraint(
                fields=["recipe", "position"],
                name="recipe_ingredient_position_unique",
            ),
            models.CheckConstraint(
                condition=Q(amount__isnull=True) | Q(amount__gte=0),
                name="recipe_ingredient_amount_nonnegative",
            ),
            models.CheckConstraint(
                condition=Q(amount_max__isnull=True) | Q(amount_max__gte=0),
                name="recipe_ingredient_amount_max_nonnegative",
            ),
        ]

    def clean(self) -> None:
        if self.unit in {Unit.TO_TASTE, Unit.PINCH}:
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
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "position"],
                name="recipe_step_position_unique",
            ),
        ]

    def clean(self) -> None:
        if (
            self.pull_internal_temperature_c is not None
            and self.target_internal_temperature_c is None
        ):
            raise ValidationError("Заполнен pull без target — ошибка SAFETY.")
