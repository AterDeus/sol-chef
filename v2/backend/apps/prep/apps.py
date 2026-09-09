from django.apps import AppConfig


class PrepConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prep"
    label = "prep"
    verbose_name = "Weekly prep"
