from abc import ABC, abstractmethod

from app.providers.schemas import SimulatedProviderRecord
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalTransactionInput,
)

CanonicalRecord = (
    CanonicalTransactionInput | CanonicalProviderBalanceInput | CanonicalFeedStatusInput
)


class ProviderAdapter(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def map_record(self, record: SimulatedProviderRecord) -> CanonicalRecord:
        raise NotImplementedError
