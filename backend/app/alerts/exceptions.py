class AlertError(Exception):
    """Base error for advisory alert operations."""


class AlertNotFoundError(AlertError):
    """Raised when an alert or source signal is not visible."""


class AlertConflictError(AlertError):
    """Raised for an invalid alert lifecycle transition."""


class AlertAuthorizationError(AlertError):
    """Raised when an actor lacks the required role or scope."""


class AlertSourceError(AlertError):
    """Raised when a source signal is not eligible for an alert."""
