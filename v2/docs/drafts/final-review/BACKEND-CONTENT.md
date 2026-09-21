# Бэкенд sol-chef 2.0 — приложение content — дамп для аудита

Снимок кода на 2026-09-20.
Источник: `v2/backend/apps/content/`.
Справочный контент: советы, зёрна, мясо. Не каталог рецептов и не калькулятор.

Правило раскладки: **один файл = содержимое одного исходного `.py`**.
Заголовок блока — путь относительно `v2/`. Ниже — классы и функции верхнего уровня и полный исходник.
Не входят: `migrations/`, `__pycache__/`, пустые `__init__.py`.

## Оглавление

| # | Файл | Классы и функции | Строк |
|---|------|------------------|------:|
| 1 | `backend/apps/content/admin.py` | `ContentDocumentAdmin` | 9 |
| 2 | `backend/apps/content/apps.py` | `ContentConfig` | 8 |
| 3 | `backend/apps/content/models.py` | `ContentDocument` | 27 |
| 4 | `backend/apps/content/urls.py` | — | 9 |
| 5 | `backend/apps/content/views.py` | `GuideView`, `GrainsGuideView`, `TipsGuideView`, `MeatGuideView` | 44 |

Всего файлов: **5**. Строк исходников: **97**.

---

## 1. `backend/apps/content/admin.py`

- Путь: `v2/backend/apps/content/admin.py`
- Классы и функции: ContentDocumentAdmin
- Строк: 9

```python
from django.contrib import admin

from apps.content.models import ContentDocument


@admin.register(ContentDocument)
class ContentDocumentAdmin(admin.ModelAdmin):
    list_display = ("type", "slug", "title", "updated_at")
    list_filter = ("type",)
```

---

## 2. `backend/apps/content/apps.py`

- Путь: `v2/backend/apps/content/apps.py`
- Классы и функции: ContentConfig
- Строк: 8

```python
from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.content"
    label = "content"
    verbose_name = "Content"
```

---

## 3. `backend/apps/content/models.py`

- Путь: `v2/backend/apps/content/models.py`
- Классы и функции: ContentDocument
- Строк: 27

```python
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
```

---

## 4. `backend/apps/content/urls.py`

- Путь: `v2/backend/apps/content/urls.py`
- Классы и функции: нет классов/функций верхнего уровня
- Строк: 9

```python
from django.urls import path

from apps.content.views import GrainsGuideView, MeatGuideView, TipsGuideView

urlpatterns = [
    path("guides/grains/", GrainsGuideView.as_view(), name="guide-grains"),
    path("guides/tips/", TipsGuideView.as_view(), name="guide-tips"),
    path("guides/meat/<slug:cut>/", MeatGuideView.as_view(), name="guide-meat"),
]
```

---

## 5. `backend/apps/content/views.py`

- Путь: `v2/backend/apps/content/views.py`
- Классы и функции: GuideView, GrainsGuideView, TipsGuideView, MeatGuideView
- Строк: 44

```python
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import ContentDocument
from apps.recipes.constants import MEAT_CUTS


def _serialize(doc: ContentDocument) -> dict:
    return {
        "type": doc.type,
        "slug": doc.slug,
        "title": doc.title,
        "payload": doc.payload_json,
    }


class GuideView(APIView):
    type_name = "guide"
    slug = ""

    def get(self, request):
        doc = ContentDocument.objects.filter(type=self.type_name, slug=self.slug).first()
        if doc is None:
            raise NotFound("Справочник не найден.")
        return Response(_serialize(doc))


class GrainsGuideView(GuideView):
    slug = "grains"


class TipsGuideView(GuideView):
    slug = "tips"


class MeatGuideView(APIView):
    def get(self, request, cut: str):
        if cut not in MEAT_CUTS:
            raise NotFound("Нет такого раздела мяса.")
        doc = ContentDocument.objects.filter(type="meat", slug=cut).first()
        if doc is None:
            raise NotFound("Справочник не найден.")
        return Response(_serialize(doc))
```

---
