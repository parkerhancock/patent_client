class InvalidFieldError(ValueError):
    """Raised when an invalid field is provided in a search query."""

    pass


class PtabApiError(Exception):
    """Custom exception for PTAB API errors."""

    pass
