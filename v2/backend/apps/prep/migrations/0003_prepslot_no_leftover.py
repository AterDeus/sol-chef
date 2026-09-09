from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("prep", "0002_prepslot_plate"),
    ]

    operations = [
        migrations.AddField(
            model_name="prepslot",
            name="no_leftover",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
