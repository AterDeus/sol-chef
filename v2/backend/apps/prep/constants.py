"""Shared prep domain codes. Use these instead of string literals."""

from django.db import models


class PrepStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class PrepMode(models.TextChoices):
    ASSEMBLE = "assemble", "Assemble"
    FINISH = "finish", "Finish"
    REHEAT = "reheat", "Reheat"


class PrepMeal(models.TextChoices):
    LUNCH = "lunch", "Lunch"
    DINNER = "dinner", "Dinner"


class PrepPlace(models.TextChoices):
    FRIDGE = "fridge", "Fridge"
    FREEZER = "freezer", "Freezer"
    PANTRY = "pantry", "Pantry"


MEAL_RANK = {PrepMeal.LUNCH: 0, PrepMeal.DINNER: 1}

PREP_STATUS = frozenset(PrepStatus.values)
PREP_MODE = frozenset(PrepMode.values)
PREP_MEAL = frozenset(PrepMeal.values)
PREP_PLACE = frozenset(PrepPlace.values)

NO_LEFTOVER_TRUE = frozenset({"1", "true", "yes", "on"})
NO_LEFTOVER_FALSE = frozenset({"0", "false", "no", "off", ""})
