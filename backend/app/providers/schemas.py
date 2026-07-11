from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class SimulatedProviderRecord:
    provider_code: str
    agent_ref: str
    account_ref: str
    record_type: str
    record_ref: str
    amount: Decimal | None
    currency: str = "BDT"
    event_timestamp: datetime | None = None
    received_timestamp: datetime | None = None
    transaction_type: str | None = None
    source_status: str = "completed"
    source_sequence: int | None = None
    availability_state: str = "available"
    scenario_run_ref: str | None = None
    synthetic_customer_ref: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
