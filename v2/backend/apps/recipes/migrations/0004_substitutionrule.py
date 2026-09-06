# Substitution graph for the calculator (sprint 3).

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_recipeingredient_optional"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubstitutionRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quality", models.DecimalField(decimal_places=2, max_digits=3)),
                ("forbidden", models.BooleanField(default=False)),
                ("note", models.TextField(blank=True, default="")),
                (
                    "from_ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="substitutions_from",
                        to="recipes.ingredient",
                    ),
                ),
                (
                    "to_ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="substitutions_to",
                        to="recipes.ingredient",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="substitution_rules",
                        to="recipes.recipe",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="substitutionrule",
            constraint=models.UniqueConstraint(
                condition=models.Q(recipe__isnull=True),
                fields=("from_ingredient", "to_ingredient"),
                name="recipes_sub_unique_global",
            ),
        ),
        migrations.AddConstraint(
            model_name="substitutionrule",
            constraint=models.UniqueConstraint(
                condition=models.Q(recipe__isnull=False),
                fields=("from_ingredient", "to_ingredient", "recipe"),
                name="recipes_sub_unique_recipe",
            ),
        ),
    ]
