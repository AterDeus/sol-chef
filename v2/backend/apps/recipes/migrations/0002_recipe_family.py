# Generated manually for sprint 2 family fields.

import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models


def forwards_notes_and_variants(apps, schema_editor):
    Recipe = apps.get_model("recipes", "Recipe")
    RecipeVariant = apps.get_model("recipes", "RecipeVariant")

    def split_notes(blob):
        if blob is None:
            return []
        text = str(blob).strip()
        if not text:
            return []
        parts = [part.strip() for part in text.split("\n\n") if part.strip()]
        return [{"title": None, "text": part} for part in parts]

    translit = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "kh",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }

    def slugify_code(title, used):
        import re

        mapped = "".join(translit.get(ch.lower(), ch) for ch in title or "")
        code = re.sub(r"[^a-z0-9]+", "-", mapped.lower()).strip("-")[:80] or "variant"
        base = code
        n = 2
        while code in used:
            suffix = f"-{n}"
            code = f"{base[: 80 - len(suffix)]}{suffix}"
            n += 1
        used.add(code)
        return code

    for recipe in Recipe.objects.all():
        recipe.notes_items = split_notes(recipe.notes)
        recipe.save(update_fields=["notes_items"])
        used: set[str] = set()
        for item in recipe.variations or []:
            if not isinstance(item, dict):
                continue
            title = item.get("title") or "Вариация"
            RecipeVariant.objects.create(
                recipe=recipe,
                axis="addon",
                code=slugify_code(title, used),
                title=title,
                has_delta=False,
                legacy_text=item.get("text") or "",
                high_risk_delta={},
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="equipment",
            field=models.CharField(
                blank=True,
                choices=[
                    ("baking_dish", "baking_dish"),
                    ("grill", "grill"),
                    ("kazan", "kazan"),
                    ("oven", "oven"),
                    ("pot", "pot"),
                    ("saucepan", "saucepan"),
                    ("skillet", "skillet"),
                ],
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="allowed_cuts",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("belly", "belly"),
                        ("breast", "breast"),
                        ("brisket", "brisket"),
                        ("drumstick", "drumstick"),
                        ("loin", "loin"),
                        ("mince", "mince"),
                        ("neck", "neck"),
                        ("ribs", "ribs"),
                        ("rump", "rump"),
                        ("shank", "shank"),
                        ("shoulder", "shoulder"),
                        ("tenderloin", "tenderloin"),
                        ("thick_rib", "thick_rib"),
                        ("thigh", "thigh"),
                        ("whole_bird", "whole_bird"),
                        ("wing", "wing"),
                    ],
                    max_length=32,
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="prep",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="recipe",
            name="notes_items",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.CreateModel(
            name="RecipeVariant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "axis",
                    models.CharField(
                        choices=[
                            ("addon", "addon"),
                            ("energy", "energy"),
                            ("equipment", "equipment"),
                        ],
                        max_length=16,
                    ),
                ),
                ("code", models.SlugField(max_length=80)),
                ("title", models.TextField()),
                ("has_delta", models.BooleanField(default=False)),
                ("legacy_text", models.TextField(blank=True, null=True)),
                ("ingredient_delta", models.JSONField(blank=True, null=True)),
                ("step_delta", models.JSONField(blank=True, null=True)),
                ("allergen_delta", models.JSONField(blank=True, null=True)),
                ("high_risk_delta", models.JSONField(blank=True, default=dict)),
                (
                    "cook_method_override",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("air_fryer", "air_fryer"),
                            ("boil", "boil"),
                            ("deep_fry", "deep_fry"),
                            ("grill", "grill"),
                            ("no_cook", "no_cook"),
                            ("oven", "oven"),
                            ("pan_fry", "pan_fry"),
                            ("steam", "steam"),
                            ("stew", "stew"),
                        ],
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "equipment",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("baking_dish", "baking_dish"),
                            ("grill", "grill"),
                            ("kazan", "kazan"),
                            ("oven", "oven"),
                            ("pot", "pot"),
                            ("saucepan", "saucepan"),
                            ("skillet", "skillet"),
                        ],
                        max_length=32,
                        null=True,
                    ),
                ),
                ("caution_text_override", models.TextField(blank=True, null=True)),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variants",
                        to="recipes.recipe",
                    ),
                ),
            ],
            options={
                "ordering": ["axis", "code"],
            },
        ),
        migrations.AddConstraint(
            model_name="recipevariant",
            constraint=models.UniqueConstraint(
                fields=("recipe", "axis", "code"),
                name="recipes_variant_unique_axis_code",
            ),
        ),
        migrations.RunPython(forwards_notes_and_variants, noop_reverse),
        migrations.RemoveField(
            model_name="recipe",
            name="variations",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="notes",
        ),
        migrations.RenameField(
            model_name="recipe",
            old_name="notes_items",
            new_name="notes",
        ),
    ]
