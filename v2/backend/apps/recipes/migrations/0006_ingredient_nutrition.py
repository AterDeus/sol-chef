from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0005_recipe_profile_adaptations"),
    ]

    operations = [
        migrations.AddField(
            model_name="ingredient",
            name="kcal_per_100g",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="protein_g_per_100g",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="fat_g_per_100g",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="carbs_g_per_100g",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="nutrition_basis",
            field=models.CharField(
                blank=True,
                choices=[("raw_100g", "raw_100g")],
                max_length=16,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="nutrition_source",
            field=models.CharField(
                blank=True,
                choices=[
                    ("editorial", "editorial"),
                    ("fooddata_central", "fooddata_central"),
                    ("packaging_typical", "packaging_typical"),
                    ("ru_table", "ru_table"),
                ],
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="nutrition_source_id",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="g_per_tsp",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="g_per_tbsp",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="g_per_pcs",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="g_per_clove",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="g_per_bunch",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="ingredient",
            name="g_per_slice",
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="recipeingredient",
            name="nutrition_exclude",
            field=models.BooleanField(default=False),
        ),
    ]
