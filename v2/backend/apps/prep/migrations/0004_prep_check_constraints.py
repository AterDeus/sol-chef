from django.db import migrations, models
from django.db.models import Q


def _null_out_invalid_counters(apps, schema_editor):
    PrepSlot = apps.get_model("prep", "PrepSlot")
    PrepContainer = apps.get_model("prep", "PrepContainer")
    PrepSlot.objects.filter(servings_cooked=0).update(servings_cooked=None)
    PrepSlot.objects.filter(feeds_slots=0).update(feeds_slots=None)
    PrepContainer.objects.filter(thaw_before_day=0).update(thaw_before_day=None)


class Migration(migrations.Migration):
    dependencies = [
        ("prep", "0003_prepslot_no_leftover"),
    ]

    operations = [
        migrations.RunPython(_null_out_invalid_counters, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="prepkit",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                default="draft",
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="prepcontainer",
            name="place",
            field=models.CharField(
                choices=[
                    ("fridge", "Fridge"),
                    ("freezer", "Freezer"),
                    ("pantry", "Pantry"),
                ],
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="prepslot",
            name="meal",
            field=models.CharField(
                choices=[("lunch", "Lunch"), ("dinner", "Dinner")],
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="prepslot",
            name="mode",
            field=models.CharField(
                choices=[
                    ("assemble", "Assemble"),
                    ("finish", "Finish"),
                    ("reheat", "Reheat"),
                ],
                max_length=16,
            ),
        ),
        migrations.AddConstraint(
            model_name="prepcontainer",
            constraint=models.CheckConstraint(
                condition=Q(thaw_before_day__isnull=True)
                | Q(thaw_before_day__gte=1, thaw_before_day__lte=7),
                name="prep_container_thaw_day_1_7",
            ),
        ),
        migrations.AddConstraint(
            model_name="prepslot",
            constraint=models.CheckConstraint(
                condition=Q(day__gte=1, day__lte=7),
                name="prep_slot_day_1_7",
            ),
        ),
        migrations.AddConstraint(
            model_name="prepslot",
            constraint=models.CheckConstraint(
                condition=Q(servings_cooked__isnull=True) | Q(servings_cooked__gte=1),
                name="prep_slot_servings_cooked_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="prepslot",
            constraint=models.CheckConstraint(
                condition=Q(feeds_slots__isnull=True) | Q(feeds_slots__gte=1),
                name="prep_slot_feeds_slots_positive",
            ),
        ),
    ]
