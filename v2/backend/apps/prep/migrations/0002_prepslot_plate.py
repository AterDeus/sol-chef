from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("prep", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="prepslot",
            name="plate",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
