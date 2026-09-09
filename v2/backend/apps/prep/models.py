"""Weekly-prep kits — slot bodies, not a second Recipe body (DATA-MODEL)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.recipes.constants import UNIT
from apps.recipes.models import Recipe


def _choice(codes: frozenset[str] | tuple[str, ...]) -> list[tuple[str, str]]:
    return [(code, code) for code in sorted(codes)]


PREP_STATUS = frozenset({"draft", "published"})
PREP_MODE = frozenset({"assemble", "finish", "reheat"})
PREP_MEAL = frozenset({"lunch", "dinner"})
PREP_PLACE = frozenset({"fridge", "freezer"})


class PrepKit(models.Model):
    slug = models.SlugField(max_length=200, unique=True)
    title = models.TextField()
    summary = models.TextField(null=True, blank=True)
    servings_base = models.PositiveIntegerField(null=True, blank=True)
    caution_text = models.TextField(null=True, blank=True)
    rhythm = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=_choice(PREP_STATUS), default="draft"
    )
    position = models.IntegerField(default=0)
    metrics = models.JSONField(default=dict, blank=True)
    weekend_timeline = models.JSONField(default=list, blank=True)
    shopping = models.JSONField(default=list, blank=True)
    allergens = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "slug"]
        indexes = [
            models.Index(fields=["status", "position", "slug"]),
        ]

    def __str__(self) -> str:
        return self.slug


class PrepComponent(models.Model):
    kit = models.ForeignKey(PrepKit, on_delete=models.CASCADE, related_name="components")
    code = models.SlugField(max_length=80)
    title = models.TextField()
    canonical_ids = models.JSONField(default=list, blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=16, choices=_choice(UNIT))
    weekend_steps = models.JSONField(default=list, blank=True)
    parcook = models.JSONField(default=dict, blank=True)
    storage = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "code"],
                name="prep_component_unique_kit_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.kit.slug}:{self.code}"


class PrepContainer(models.Model):
    kit = models.ForeignKey(PrepKit, on_delete=models.CASCADE, related_name="containers")
    code = models.SlugField(max_length=80)
    label = models.TextField()
    component = models.ForeignKey(
        PrepComponent, on_delete=models.CASCADE, related_name="boxes"
    )
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=16, choices=_choice(UNIT))
    place = models.CharField(max_length=16, choices=_choice(PREP_PLACE))
    thaw_before_day = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "code"],
                name="prep_container_unique_kit_code",
            )
        ]

    def __str__(self) -> str:
        return f"{self.kit.slug}:{self.code}"

    def clean(self) -> None:
        if self.thaw_before_day is not None and not 1 <= self.thaw_before_day <= 7:
            raise ValidationError("thaw_before_day должен быть 1–7.")


class PrepSlot(models.Model):
    kit = models.ForeignKey(PrepKit, on_delete=models.CASCADE, related_name="slots")
    day = models.PositiveSmallIntegerField()
    meal = models.CharField(max_length=16, choices=_choice(PREP_MEAL))
    recipe = models.ForeignKey(
        Recipe, on_delete=models.PROTECT, related_name="prep_slots"
    )
    mode = models.CharField(max_length=16, choices=_choice(PREP_MODE))
    flavor = models.TextField(null=True, blank=True)
    plate = models.JSONField(default=dict, blank=True)
    source = models.JSONField(default=dict)
    container_ids = models.JSONField(default=list, blank=True)
    alternatives = models.JSONField(default=list, blank=True)
    servings_cooked = models.PositiveIntegerField(null=True, blank=True)
    feeds_slots = models.PositiveIntegerField(null=True, blank=True)
    time_active_from_prep_min = models.PositiveIntegerField(null=True, blank=True)
    time_active_scratch_min = models.PositiveIntegerField(null=True, blank=True)
    steps = models.JSONField(default=list)
    no_leftover = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["day", "meal"]
        constraints = [
            models.UniqueConstraint(
                fields=["kit", "day", "meal"],
                name="prep_slot_unique_kit_day_meal",
            )
        ]

    def __str__(self) -> str:
        return f"{self.kit.slug}:{self.day}:{self.meal}"

    def clean(self) -> None:
        if self.day < 1 or self.day > 7:
            raise ValidationError("day должен быть 1–7.")
