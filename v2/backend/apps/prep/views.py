from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.prep.constants import PrepStatus
from apps.prep.models import PrepKit
from apps.prep.serializers import serialize_kit_detail, serialize_kit_list_item
from apps.prep.services.leftover import parse_no_leftover
from apps.prep.services.read_model import load_kit_data
from apps.recipes.query import parse_optional_decimal


def _published():
    return PrepKit.objects.filter(status=PrepStatus.PUBLISHED)


class PrepKitListView(APIView):
    def get(self, request):
        kits = _published().order_by("position", "slug")
        return Response({"results": [serialize_kit_list_item(kit) for kit in kits]})


class PrepKitDetailView(APIView):
    def get(self, request, slug: str):
        kit = (
            _published()
            .prefetch_related(
                "components",
                "containers__component",
                "slots__recipe",
            )
            .filter(slug=slug)
            .first()
        )
        if kit is None:
            raise NotFound("Набор не найден.")

        return Response(
            serialize_kit_detail(
                load_kit_data(kit),
                parse_optional_decimal(request, "servings"),
                no_leftover=parse_no_leftover(request),
            )
        )
