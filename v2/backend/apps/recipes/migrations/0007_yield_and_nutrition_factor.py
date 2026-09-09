from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0006_ingredient_nutrition"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="yield_weight_g",
            field=models.DecimalField(
                blank=True, decimal_places=1, max_digits=8, null=True
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="yield_kind",
            field=models.CharField(
                blank=True,
                choices=[("estimated", "estimated"), ("exact", "exact")],
                max_length=16,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="recipeingredient",
            name="nutrition_factor",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=4, null=True
            ),
        ),
    ]
