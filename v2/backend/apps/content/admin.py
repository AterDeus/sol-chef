from django.contrib import admin

from apps.content.models import ContentDocument


@admin.register(ContentDocument)
class ContentDocumentAdmin(admin.ModelAdmin):
    list_display = ("type", "slug", "title", "updated_at")
    list_filter = ("type",)
