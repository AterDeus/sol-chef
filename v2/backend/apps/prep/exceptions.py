from apps.core.exceptions import DomainValidationError


class PrepError(DomainValidationError):
    """Bad prep query or payload — API 400."""
