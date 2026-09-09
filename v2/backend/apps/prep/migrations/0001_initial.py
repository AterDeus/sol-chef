import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("recipes", "0007_yield_and_nutrition_factor"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrepKit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.SlugField(max_length=200, unique=True)),
                ("title", models.TextField()),
                ("summary", models.TextField(blank=True, null=True)),
                ("servings_base", models.PositiveIntegerField(blank=True, null=True)),
                ("caution_text", models.TextField(blank=True, null=True)),
                ("rhythm", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "draft"), ("published", "published")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("position", models.IntegerField(default=0)),
                ("metrics", models.JSONField(blank=True, default=dict)),
                ("weekend_timeline", models.JSONField(blank=True, default=list)),
                ("shopping", models.JSONField(blank=True, default=list)),
                ("allergens", models.JSONField(blank=True, default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["position", "slug"],
            },
        ),
        migrations.CreateModel(
            name="PrepComponent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.SlugField(max_length=80)),
                ("title", models.TextField()),
                ("canonical_ids", models.JSONField(blank=True, default=list)),
                ("qty", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "unit",
                    models.CharField(
                        choices=[
                            ("bunch", "bunch"),
                            ("clove", "clove"),
                            ("g", "g"),
                            ("kg", "kg"),
                            ("l", "l"),
                            ("ml", "ml"),
                            ("pcs", "pcs"),
                            ("pinch", "pinch"),
                            ("slice", "slice"),
                            ("tbsp", "tbsp"),
                            ("to_taste", "to_taste"),
                            ("tsp", "tsp"),
                        ],
                        max_length=16,
                    ),
                ),
                ("weekend_steps", models.JSONField(blank=True, default=list)),
                ("parcook", models.JSONField(blank=True, default=dict)),
                ("storage", models.JSONField(blank=True, default=dict)),
                (
                    "kit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="components",
                        to="prep.prepkit",
                    ),
                ),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="PrepContainer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.SlugField(max_length=80)),
                ("label", models.TextField()),
                ("qty", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "unit",
                    models.CharField(
                        choices=[
                            ("bunch", "bunch"),
                            ("clove", "clove"),
                            ("g", "g"),
                            ("kg", "kg"),
                            ("l", "l"),
                            ("ml", "ml"),
                            ("pcs", "pcs"),
                            ("pinch", "pinch"),
                            ("slice", "slice"),
                            ("tbsp", "tbsp"),
                            ("to_taste", "to_taste"),
                            ("tsp", "tsp"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "place",
                    models.CharField(
                        choices=[("freezer", "freezer"), ("fridge", "fridge")],
                        max_length=16,
                    ),
                ),
                (
                    "thaw_before_day",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "component",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="boxes",
                        to="prep.prepcomponent",
                    ),
                ),
                (
                    "kit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="containers",
                        to="prep.prepkit",
                    ),
                ),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="PrepSlot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("day", models.PositiveSmallIntegerField()),
                (
                    "meal",
                    models.CharField(
                        choices=[("dinner", "dinner"), ("lunch", "lunch")],
                        max_length=16,
                    ),
                ),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("assemble", "assemble"),
                            ("finish", "finish"),
                            ("reheat", "reheat"),
                        ],
                        max_length=16,
                    ),
                ),
                ("flavor", models.TextField(blank=True, null=True)),
                ("source", models.JSONField(default=dict)),
                ("container_ids", models.JSONField(blank=True, default=list)),
                ("alternatives", models.JSONField(blank=True, default=list)),
                (
                    "servings_cooked",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("feeds_slots", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "time_active_from_prep_min",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "time_active_scratch_min",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("steps", models.JSONField(default=list)),
                (
                    "kit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="slots",
                        to="prep.prepkit",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="prep_slots",
                        to="recipes.recipe",
                    ),
                ),
            ],
            options={"ordering": ["day", "meal"]},
        ),
        migrations.AddIndex(
            model_name="prepkit",
            index=models.Index(
                fields=["status", "position", "slug"],
                name="prep_prepki_status_2f1c1a_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="prepcomponent",
            constraint=models.UniqueConstraint(
                fields=("kit", "code"),
                name="prep_component_unique_kit_code",
            ),
        ),
        migrations.AddConstraint(
            model_name="prepcontainer",
            constraint=models.UniqueConstraint(
                fields=("kit", "code"),
                name="prep_container_unique_kit_code",
            ),
        ),
        migrations.AddConstraint(
            model_name="prepslot",
            constraint=models.UniqueConstraint(
                fields=("kit", "day", "meal"),
                name="prep_slot_unique_kit_day_meal",
            ),
        ),
    ]
