class ValidationError(Exception):
    """Base validation module error."""


class ProviderMappingError(ValidationError):
    pass


class ValidationPersistenceError(ValidationError):
    pass
