class ProviderAdapterError(Exception):
    """Base provider adapter error."""


class UnsupportedProviderError(ProviderAdapterError):
    pass
