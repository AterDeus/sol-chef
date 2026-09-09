from rest_framework.views import exception_handler

from apps.prep.exceptions import PrepError
from apps.recipes.services.assemble import VariantError
from apps.recipes.services.scale import ScaleConflict


def api_exception_handler(exc, context):
    if isinstance(exc, (ScaleConflict, VariantError, PrepError)):
        from rest_framework.response import Response

        return Response({"detail": str(exc)}, status=400)
    return exception_handler(exc, context)
