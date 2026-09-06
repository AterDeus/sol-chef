# Generated manually: optional garnish lines.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0002_recipe_family"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipeingredient",
            name="optional",
            field=models.BooleanField(default=False),
        ),
    ]
