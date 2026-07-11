from app.persistence.models.enums import FeedQualityStatus, TransactionStatus, TransactionType
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalSharedCashInput,
    CanonicalTransactionInput,
)


def normalize_provider_code(value: str) -> str:
    if value.startswith("SIM-PROVIDER-"):
        return value
    return f"SIM-PROVIDER-{value}"


def normalize_transaction_type(value: TransactionType | str) -> TransactionType:
    return value if isinstance(value, TransactionType) else TransactionType(str(value))


def normalize_transaction_status(value: TransactionStatus | str) -> TransactionStatus:
    return value if isinstance(value, TransactionStatus) else TransactionStatus(str(value))


def normalize_feed_status(value: FeedQualityStatus | str) -> FeedQualityStatus:
    return value if isinstance(value, FeedQualityStatus) else FeedQualityStatus(str(value))


def canonical_transaction(record: CanonicalTransactionInput) -> CanonicalTransactionInput:
    return CanonicalTransactionInput(
        provider_code=normalize_provider_code(record.provider_code),
        agent_ref=record.agent_ref,
        account_ref=record.account_ref,
        synthetic_transaction_ref=record.synthetic_transaction_ref,
        synthetic_account_ref=record.synthetic_account_ref,
        synthetic_customer_ref=record.synthetic_customer_ref,
        transaction_type=normalize_transaction_type(record.transaction_type),
        amount=record.amount,
        currency=record.currency.upper(),
        event_timestamp=record.event_timestamp,
        received_timestamp=record.received_timestamp,
        source_sequence=record.source_sequence,
        source_status=normalize_transaction_status(record.source_status),
        scenario_run_ref=record.scenario_run_ref,
        source_metadata=record.source_metadata,
    )


def canonical_provider_balance(
    record: CanonicalProviderBalanceInput,
) -> CanonicalProviderBalanceInput:
    return CanonicalProviderBalanceInput(
        provider_code=normalize_provider_code(record.provider_code),
        agent_ref=record.agent_ref,
        account_ref=record.account_ref,
        reported_balance=record.reported_balance,
        balance_timestamp=record.balance_timestamp,
        received_timestamp=record.received_timestamp,
        source_sequence=record.source_sequence,
        availability_state=record.availability_state,
        scenario_run_ref=record.scenario_run_ref,
        source_metadata=record.source_metadata,
    )


def canonical_shared_cash(record: CanonicalSharedCashInput) -> CanonicalSharedCashInput:
    return record


def canonical_feed_status(record: CanonicalFeedStatusInput) -> CanonicalFeedStatusInput:
    return CanonicalFeedStatusInput(
        provider_code=normalize_provider_code(record.provider_code),
        agent_ref=record.agent_ref,
        expected_timestamp=record.expected_timestamp,
        received_timestamp=record.received_timestamp,
        last_successful_timestamp=record.last_successful_timestamp,
        source_status=normalize_feed_status(record.source_status),
        source_sequence=record.source_sequence,
        error_code=record.error_code,
        scenario_run_ref=record.scenario_run_ref,
        source_metadata=record.source_metadata,
    )
