from enum import StrEnum


class ValidationCategory(StrEnum):
    VALID = "valid"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_IDENTIFIER = "invalid_identifier"
    UNKNOWN_PROVIDER = "unknown_provider"
    INVALID_AMOUNT = "invalid_amount"
    INVALID_CURRENCY = "invalid_currency"
    INVALID_TRANSACTION_TYPE = "invalid_transaction_type"
    DUPLICATE_TRANSACTION = "duplicate_transaction"
    DUPLICATE_SNAPSHOT = "duplicate_snapshot"
    DELAYED_FEED = "delayed_feed"
    STALE_FEED = "stale_feed"
    MISSING_FEED = "missing_feed"
    CONFLICTING_BALANCE = "conflicting_balance"
    OUT_OF_ORDER_EVENT = "out_of_order_event"
    SEQUENCE_GAP = "sequence_gap"
    FUTURE_TIMESTAMP = "future_timestamp"
    TIMESTAMP_SKEW = "timestamp_skew"
    NEGATIVE_BALANCE = "negative_balance"
    IMPOSSIBLE_BALANCE_CHANGE = "impossible_balance_change"
    PROVIDER_SCOPE_MISMATCH = "provider_scope_mismatch"
    AGENT_ACCOUNT_MISMATCH = "agent_account_mismatch"
    MALFORMED_METADATA = "malformed_metadata"
    UNSUPPORTED_RECORD = "unsupported_record"


class ValidationSeverity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecordDisposition(StrEnum):
    ACCEPTED = "accepted"
    ACCEPTED_WITH_WARNING = "accepted_with_warning"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"
    DUPLICATE_IGNORED = "duplicate_ignored"


class RecordUsability(StrEnum):
    USABLE = "usable"
    USABLE_WITH_WARNING = "usable_with_warning"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"


class QualityLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNUSABLE = "unusable"
