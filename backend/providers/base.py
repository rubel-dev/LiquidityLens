from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProviderBalanceResult:
    provider: str
    balance: float | None
    fetched_at: datetime
    data_quality: str          # ok | delayed | missing | conflict
    latency_ms: int


@dataclass
class ProviderTransaction:
    id: str
    provider: str
    type: str
    amount: float
    account_id: str
    timestamp: datetime
    status: str


class BaseProvider(ABC):
    name: str

    @abstractmethod
    async def get_balance(self, agent_id: str) -> ProviderBalanceResult:
        pass

    @abstractmethod
    async def get_recent_transactions(
        self, agent_id: str, minutes: int = 60
    ) -> list[ProviderTransaction]:
        pass
