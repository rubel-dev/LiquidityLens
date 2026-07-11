from abc import ABC, abstractmethod

from app.providers.schemas import SimulatedProviderRecord
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalSharedCashInput,
    CanonicalTransactionInput,
)

CanonicalRecord = (
    CanonicalTransactionInput
    | CanonicalProviderBalanceInput
    | CanonicalSharedCashInput
    | CanonicalFeedStatusInput
)


class ProviderAdapter(ABC):
    @property
    @abstractmethod
    def provider_code(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def map_record(self, record: SimulatedProviderRecord) -> CanonicalRecord:
        raise NotImplementedError
