"""VOCAB TextChoices. Codes must match docs/VOCAB.md; do not invent new ones."""

from django.db import models


class RecipeStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_REVIEW = "in_review", "In review"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"


class CookMethod(models.TextChoices):
    OVEN = "oven", "Oven"
    PAN_FRY = "pan_fry", "Pan fry"
    STEW = "stew", "Stew"
    BOIL = "boil", "Boil"
    GRILL = "grill", "Grill"
    STEAM = "steam", "Steam"
    NO_COOK = "no_cook", "No cook"
    AIR_FRYER = "air_fryer", "Air fryer"
    DEEP_FRY = "deep_fry", "Deep fry"


class ProteinBase(models.TextChoices):
    BEEF = "beef", "Beef"
    PORK = "pork", "Pork"
    POULTRY = "poultry", "Poultry"
    LAMB = "lamb", "Lamb"
    FISH_WHITE_SEA = "fish_white_sea", "White sea fish"
    FISH_RED_SEA = "fish_red_sea", "Red sea fish"
    FISH_RIVER = "fish_river", "River fish"
    FISH_CANNED = "fish_canned", "Canned fish"
    SEAFOOD = "seafood", "Seafood"
    OFFAL = "offal", "Offal"
    EGGS_DAIRY = "eggs_dairy", "Eggs and dairy"
    VEGETARIAN = "vegetarian", "Vegetarian"
    VEGETABLES = "vegetables", "Vegetables"
    MUSHROOMS = "mushrooms", "Mushrooms"
    LEGUMES = "legumes", "Legumes"
    FRUITS = "fruits", "Fruits"


class DishType(models.TextChoices):
    MAIN = "main", "Main"
    SOUP = "soup", "Soup"
    SALAD = "salad", "Salad"
    APPETIZER = "appetizer", "Appetizer"
    BREAKFAST = "breakfast", "Breakfast"
    SIDE = "side", "Side"
    PASTA_GRAINS = "pasta_grains", "Pasta and grains"
    BAKERY = "bakery", "Bakery"
    DESSERT = "dessert", "Dessert"
    SAUCE = "sauce", "Sauce"
    DRINK = "drink", "Drink"
    PRESERVE = "preserve", "Preserve"


class ScaleMode(models.TextChoices):
    LINEAR = "linear", "Linear"
    GENTLE = "gentle", "Gentle"
    WHOLE = "whole", "Whole"
    MANUAL = "manual", "Manual"


class Unit(models.TextChoices):
    G = "g", "g"
    KG = "kg", "kg"
    ML = "ml", "ml"
    L = "l", "l"
    PCS = "pcs", "pcs"
    TSP = "tsp", "tsp"
    TBSP = "tbsp", "tbsp"
    PINCH = "pinch", "pinch"
    CLOVE = "clove", "clove"
    BUNCH = "bunch", "bunch"
    SLICE = "slice", "slice"
    TO_TASTE = "to_taste", "to_taste"


class Allergen(models.TextChoices):
    GLUTEN = "gluten", "Gluten"
    MILK = "milk", "Milk"
    EGG = "egg", "Egg"
    FISH = "fish", "Fish"
    CRUSTACEAN = "crustacean", "Crustacean"
    MOLLUSC = "mollusc", "Mollusc"
    PEANUT = "peanut", "Peanut"
    TREE_NUT = "tree_nut", "Tree nut"
    SOY = "soy", "Soy"
    SESAME = "sesame", "Sesame"
    MUSTARD = "mustard", "Mustard"
    CELERY = "celery", "Celery"
    SULFITE = "sulfite", "Sulfite"
    LUPIN = "lupin", "Lupin"


class HighRisk(models.TextChoices):
    RAW_EGG = "raw_egg", "Raw egg"
    RAW_MEAT = "raw_meat", "Raw meat"
    RAW_FISH = "raw_fish", "Raw fish"
    RAW_MILK = "raw_milk", "Raw milk"
    WILD_MUSHROOMS = "wild_mushrooms", "Wild mushrooms"
    GROUND_MEAT = "ground_meat", "Ground meat"
    PRESERVATION = "preservation", "Preservation"
    FERMENTATION = "fermentation", "Fermentation"
    CHILD_FOOD = "child_food", "Child food"
    FIRE_HAZARD = "fire_hazard", "Fire hazard"
    POULTRY_TEMP = "poultry_temp", "Poultry temperature"


class EnergyProfile(models.TextChoices):
    STANDARD = "standard", "Standard"
    LIGHT = "light", "Light"
    RICH = "rich", "Rich"


class NutritionBasis(models.TextChoices):
    RAW_100G = "raw_100g", "Raw 100g"


class YieldKind(models.TextChoices):
    ESTIMATED = "estimated", "Estimated"
    EXACT = "exact", "Exact"


class NutritionSource(models.TextChoices):
    FOODDATA_CENTRAL = "fooddata_central", "FoodData Central"
    RU_TABLE = "ru_table", "RU table"
    PACKAGING_TYPICAL = "packaging_typical", "Packaging typical"
    EDITORIAL = "editorial", "Editorial"


class Equipment(models.TextChoices):
    POT = "pot", "Pot"
    OVEN = "oven", "Oven"
    KAZAN = "kazan", "Kazan"
    SKILLET = "skillet", "Skillet"
    SAUCEPAN = "saucepan", "Saucepan"
    BAKING_DISH = "baking_dish", "Baking dish"
    GRILL = "grill", "Grill"


class Cut(models.TextChoices):
    SHANK = "shank", "Shank"
    SHOULDER = "shoulder", "Shoulder"
    NECK = "neck", "Neck"
    RUMP = "rump", "Rump"
    BRISKET = "brisket", "Brisket"
    THICK_RIB = "thick_rib", "Thick rib"
    TENDERLOIN = "tenderloin", "Tenderloin"
    LOIN = "loin", "Loin"
    BELLY = "belly", "Belly"
    RIBS = "ribs", "Ribs"
    MINCE = "mince", "Mince"
    BREAST = "breast", "Breast"
    THIGH = "thigh", "Thigh"
    DRUMSTICK = "drumstick", "Drumstick"
    WING = "wing", "Wing"
    WHOLE_BIRD = "whole_bird", "Whole bird"


class VariantAxis(models.TextChoices):
    ADDON = "addon", "Addon"
    EQUIPMENT = "equipment", "Equipment"
    ENERGY = "energy", "Energy"


class UseCase(models.TextChoices):
    FAST = "fast", "Fast"
    EASY = "easy", "Easy"
    PANTRY = "pantry", "Pantry"
    ONE_PAN = "one_pan", "One pan"
    BATCH = "batch", "Batch"
    BUDGET = "budget", "Budget"
    LIGHT = "light", "Light"


class AdaptationType(models.TextChoices):
    SUBSTITUTION = "substitution", "Substitution"
    OMISSION = "omission", "Omission"
    EQUIPMENT = "equipment", "Equipment"
    METHOD = "method", "Method"
