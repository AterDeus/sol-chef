"""Shared domain errors. API boundary maps them to HTTP 400."""

from rest_framework.response import Response
from rest_framework.views import exception_handler


class DomainValidationError(Exception):
    """Use-case error converted to HTTP 400 at the API boundary."""


def api_exception_handler(exc, context):
    if isinstance(exc, DomainValidationError):
        return Response({"detail": str(exc)}, status=400)
    return exception_handler(exc, context)
