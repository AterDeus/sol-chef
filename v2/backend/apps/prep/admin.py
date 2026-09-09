from django.contrib import admin

from apps.prep.models import PrepComponent, PrepContainer, PrepKit, PrepSlot


class PrepComponentInline(admin.TabularInline):
    model = PrepComponent
    extra = 0


class PrepContainerInline(admin.TabularInline):
    model = PrepContainer
    extra = 0


class PrepSlotInline(admin.TabularInline):
    model = PrepSlot
    extra = 0


@admin.register(PrepKit)
class PrepKitAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "status", "position", "servings_base")
    list_filter = ("status",)
    search_fields = ("slug", "title")
    inlines = [PrepComponentInline, PrepContainerInline, PrepSlotInline]


@admin.register(PrepComponent)
class PrepComponentAdmin(admin.ModelAdmin):
    list_display = ("kit", "code", "title")
    search_fields = ("code", "title")


@admin.register(PrepContainer)
class PrepContainerAdmin(admin.ModelAdmin):
    list_display = ("kit", "code", "label", "place")


@admin.register(PrepSlot)
class PrepSlotAdmin(admin.ModelAdmin):
    list_display = ("kit", "day", "meal", "recipe", "mode")
    list_filter = ("mode", "meal")
