from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.prep.models import PrepKit
from apps.prep.serializers import serialize_kit_detail, serialize_kit_list_item
from apps.prep.services.leftover import parse_no_leftover
from apps.recipes.query import parse_optional_decimal


def _published():
    return PrepKit.objects.filter(status="published")


class PrepKitListView(APIView):
    def get(self, request):
        kits = _published().order_by("position", "slug")
        return Response({"results": [serialize_kit_list_item(kit) for kit in kits]})


class PrepKitDetailView(APIView):
    def get(self, request, slug: str):
        kit = (
            _published()
            .prefetch_related("components", "containers__component", "slots__recipe")
            .filter(slug=slug)
            .first()
        )
        if kit is None:
            raise NotFound("Набор не найден.")
        servings = parse_optional_decimal(request, "servings")
        no_leftover = parse_no_leftover(request)
        return Response(serialize_kit_detail(kit, servings, no_leftover=no_leftover))
