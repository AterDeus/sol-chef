"""Compatibility re-export. New code should import from apps.core.exceptions."""

from apps.core.exceptions import DomainValidationError, api_exception_handler

__all__ = ["DomainValidationError", "api_exception_handler"]
