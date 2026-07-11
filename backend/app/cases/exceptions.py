class CaseError(Exception):
    """Base error for case operations."""


class CaseNotFoundError(CaseError):
    """Raised when a case is not visible in the actor scope."""


class CaseConflictError(CaseError):
    """Raised for an invalid or concurrent lifecycle transition."""


class CaseAuthorizationError(CaseError):
    """Raised when an actor lacks the required role."""
