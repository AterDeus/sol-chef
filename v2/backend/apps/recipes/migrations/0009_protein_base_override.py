from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


_PROTEIN = [
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
]


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0008_protein_base_fruits"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="protein_bases_extra",
            field=ArrayField(
                models.CharField(choices=_PROTEIN, max_length=32),
                blank=True,
                default=list,
            ),
        ),
        migrations.AddField(
            model_name="recipevariant",
            name="protein_base_override",
            field=models.CharField(
                blank=True,
                choices=_PROTEIN,
                max_length=32,
                null=True,
            ),
        ),
    ]
