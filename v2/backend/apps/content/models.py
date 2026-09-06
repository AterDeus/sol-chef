from django.db import models


class ContentDocument(models.Model):
    TYPE_GUIDE = "guide"
    TYPE_MEAT = "meat"
    TYPE_CHOICES = (
        (TYPE_GUIDE, TYPE_GUIDE),
        (TYPE_MEAT, TYPE_MEAT),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    slug = models.SlugField(max_length=80)
    title = models.TextField()
    payload_json = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["type", "slug"],
                name="content_document_type_slug_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.type}/{self.slug}"
