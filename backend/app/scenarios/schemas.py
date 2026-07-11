from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Literal

from app.persistence.models.enums import FeedQualityStatus, TransactionType

GENERATOR_VERSION = "scenario-generator-v1"
CATALOG_VERSION = "scenario-catalog-v1"
SCENARIO_DEFINITION_VERSION = "v1"

ProfileName = Literal["small", "medium", "demo"]


@dataclass(frozen=True)
class ProviderContext:
    code: str
    display_name: str
    synthetic_ref: str


@dataclass(frozen=True)
class ScenarioDefinition:
    code: str
    name: str
    purpose: str
    expected_ground_truth: tuple[str, ...]
    review_required: bool
    anomaly_positive: bool
    false_positive_case: bool
    version: str = SCENARIO_DEFINITION_VERSION


@dataclass(frozen=True)
class ScenarioConfig:
    profile: ProfileName = "small"
    start_timestamp: datetime | None = None
    requested_run_ref: str | None = None


@dataclass(frozen=True)
class GeneratedTransaction:
    synthetic_transaction_ref: str
    provider_code: str
    synthetic_account_ref: str
    synthetic_customer_ref: str
    transaction_type: TransactionType
    amount: Decimal
    occurred_at: datetime
    currency: str = "BDT"


@dataclass(frozen=True)
class GeneratedBalanceSnapshot:
    provider_code: str | None
    amount: Decimal | None
    observed_at: datetime
    quality_status: str
    currency: str = "BDT"


@dataclass(frozen=True)
class GeneratedFeedStatus:
    provider_code: str
    status: FeedQualityStatus
    observed_at: datetime
    ingested_at: datetime | None
    event_type: str | None = None


@dataclass(frozen=True)
class GroundTruthEvent:
    category: str
    start_time: datetime
    end_time: datetime
    agent_scope: str
    provider_scope: str | None = None
    affected_transaction_refs: tuple[str, ...] = ()
    expected_review_boundary: str = "human review boundary; not proof of wrongdoing"
    anomaly_positive: bool = False
    false_positive_case: bool = False


@dataclass(frozen=True)
class GeneratedScenario:
    definition: ScenarioDefinition
    seed: str
    run_ref: str
    start_timestamp: datetime
    profile: ProfileName
    transactions: tuple[GeneratedTransaction, ...]
    provider_balances: tuple[GeneratedBalanceSnapshot, ...]
    shared_cash: tuple[GeneratedBalanceSnapshot, ...]
    feed_statuses: tuple[GeneratedFeedStatus, ...]
    ground_truth: tuple[GroundTruthEvent, ...]
    agent_available: bool = True
    generated_counts: dict[str, int] = field(default_factory=dict)
    fingerprint: str = ""


@dataclass(frozen=True)
class ScenarioRunResult:
    run_ref: str
    scenario_code: str
    status: str
    seed: str
    fingerprint: str
    generated_counts: dict[str, int]
