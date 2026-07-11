from datetime import UTC, datetime

from app.providers.base import CanonicalRecord, ProviderAdapter
from app.providers.exceptions import ProviderAdapterError
from app.providers.schemas import SimulatedProviderRecord
from app.validation.normalizer import normalize_provider_code
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalTransactionInput,
)


class SimulatedProviderAdapter(ProviderAdapter):
    def __init__(self, provider_code: str) -> None:
        self._provider_code = normalize_provider_code(provider_code)

    @property
    def provider_code(self) -> str:
        return self._provider_code

    def map_record(self, record: SimulatedProviderRecord) -> CanonicalRecord:
        if normalize_provider_code(record.provider_code) != self.provider_code:
            raise ProviderAdapterError("record provider does not match adapter scope")
        received = record.received_timestamp or datetime.now(UTC)
        event = record.event_timestamp or received
        if record.record_type == "transaction":
            if record.amount is None or record.transaction_type is None:
                raise ProviderAdapterError(
                    "transaction records require amount and transaction_type"
                )
            return CanonicalTransactionInput(
                provider_code=self.provider_code,
                agent_ref=record.agent_ref,
                account_ref=record.account_ref,
                synthetic_transaction_ref=record.record_ref,
                synthetic_account_ref=record.account_ref,
                synthetic_customer_ref=record.synthetic_customer_ref or "SIM-CUST-0001",
                transaction_type=record.transaction_type,
                amount=record.amount,
                currency=record.currency,
                event_timestamp=event,
                received_timestamp=received,
                source_sequence=record.source_sequence,
                source_status=record.source_status,
                scenario_run_ref=record.scenario_run_ref,
                source_metadata=record.metadata,
            )
        if record.record_type == "provider_balance":
            return CanonicalProviderBalanceInput(
                provider_code=self.provider_code,
                agent_ref=record.agent_ref,
                account_ref=record.account_ref,
                reported_balance=record.amount,
                balance_timestamp=event,
                received_timestamp=received,
                source_sequence=record.source_sequence,
                availability_state=record.availability_state,
                scenario_run_ref=record.scenario_run_ref,
                source_metadata=record.metadata,
            )
        if record.record_type == "feed_status":
            return CanonicalFeedStatusInput(
                provider_code=self.provider_code,
                agent_ref=record.agent_ref,
                expected_timestamp=event,
                received_timestamp=record.received_timestamp,
                last_successful_timestamp=record.event_timestamp,
                source_status=record.source_status,
                source_sequence=record.source_sequence,
                error_code=None,
                scenario_run_ref=record.scenario_run_ref,
                source_metadata=record.metadata,
            )
        raise ProviderAdapterError(f"unsupported simulated record type: {record.record_type}")
