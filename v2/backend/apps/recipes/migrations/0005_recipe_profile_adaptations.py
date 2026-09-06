from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0004_substitutionrule"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="time_total_minutes",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="time_active_minutes",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="effort_level",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="washing_level",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="use_cases",
            field=ArrayField(
                base_field=models.CharField(max_length=32),
                blank=True,
                default=list,
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="adaptations",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
