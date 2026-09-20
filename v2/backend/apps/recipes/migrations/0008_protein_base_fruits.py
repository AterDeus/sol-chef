from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0007_yield_and_nutrition_factor"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="protein_base",
            field=models.CharField(
                choices=[
                    ("beef", "beef"),
                    ("eggs_dairy", "eggs_dairy"),
                    ("fish_canned", "fish_canned"),
                    ("fish_red_sea", "fish_red_sea"),
                    ("fish_river", "fish_river"),
                    ("fish_white_sea", "fish_white_sea"),
                    ("fruits", "fruits"),
                    ("lamb", "lamb"),
                    ("legumes", "legumes"),
                    ("mushrooms", "mushrooms"),
                    ("offal", "offal"),
                    ("pork", "pork"),
                    ("poultry", "poultry"),
                    ("seafood", "seafood"),
                    ("vegetables", "vegetables"),
                    ("vegetarian", "vegetarian"),
                ],
                max_length=32,
            ),
        ),
    ]
