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
