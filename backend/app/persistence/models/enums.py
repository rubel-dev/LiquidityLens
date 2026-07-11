from enum import StrEnum
from typing import TypeVar

EnumType = TypeVar("EnumType", bound=StrEnum)


def enum_values(enum_cls: type[EnumType]) -> list[str]:
    return [member.value for member in enum_cls]


class AgentStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TransactionType(StrEnum):
    CASH_IN = "cash_in"
    CASH_OUT = "cash_out"
    BILL_PAY = "bill_pay"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class TransactionStatus(StrEnum):
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    REVERSED_SIMULATED = "reversed_simulated"


class FeedQualityStatus(StrEnum):
    COMPLETE = "complete"
    DELAYED = "delayed"
    STALE = "stale"
    MISSING = "missing"
    CONFLICTING = "conflicting"
    INVALID = "invalid"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScenarioRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AlertStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    ACKNOWLEDGED = "acknowledged"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CaseStatus(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    ACKNOWLEDGED = "acknowledged"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ExplanationLanguage(StrEnum):
    EN = "en"
    BN = "bn"
    BANGLISH = "banglish"


class ReviewStatus(StrEnum):
    NEW = "new"
    NEEDS_REVIEW = "needs_review"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"
