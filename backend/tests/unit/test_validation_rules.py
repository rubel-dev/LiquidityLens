from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.persistence.models.enums import FeedQualityStatus, TransactionType
from app.validation.enums import ValidationCategory
from app.validation.feed_validator import status_for_findings, validate_feed_status_input
from app.validation.quality_score import score_findings
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalTransactionInput,
    ValidationSettings,
)
from app.validation.transaction_validator import validate_transaction_input


def now() -> datetime:
    return datetime.now(UTC)


def transaction(**overrides) -> CanonicalTransactionInput:
    base = {
        "provider_code": "SIM-PROVIDER-BK",
        "agent_ref": "SIM-AGENT-0001",
        "account_ref": "SIM-ACCT-BK-0001",
        "synthetic_transaction_ref": "SIM-TXN-900001-000001",
        "synthetic_account_ref": "SIM-ACCT-BK-0001",
        "synthetic_customer_ref": "SIM-CUST-0001",
        "transaction_type": TransactionType.CASH_OUT,
        "amount": Decimal("100.00"),
        "currency": "BDT",
        "event_timestamp": now(),
        "received_timestamp": now() + timedelta(seconds=1),
    }
    base.update(overrides)
    return CanonicalTransactionInput(**base)


def provider_agent_account():
    provider = SimpleNamespace(id="provider-id")
    agent = SimpleNamespace(id="agent-id")
    account = SimpleNamespace(provider_id="provider-id", agent_id="agent-id")
    return provider, agent, account


def feed(**overrides) -> CanonicalFeedStatusInput:
    expected = now()
    base = {
        "provider_code": "SIM-PROVIDER-BK",
        "agent_ref": "SIM-AGENT-0001",
        "expected_timestamp": expected,
        "received_timestamp": expected + timedelta(minutes=1),
        "last_successful_timestamp": expected,
        "source_status": FeedQualityStatus.COMPLETE,
    }
    base.update(overrides)
    return CanonicalFeedStatusInput(**base)


def test_valid_transaction_has_high_quality_score():
    findings = validate_transaction_input(
        transaction(),
        ValidationSettings(),
        provider=object(),
        agent=object(),
        account=None,
        duplicate_exists=False,
        latest_transaction_time=None,
    )
    categories = {item.category for item in findings}

    assert ValidationCategory.MISSING_REQUIRED_FIELD in categories
    assert score_findings(tuple()).overall_score == Decimal("1.00")


@pytest.mark.parametrize("amount", [Decimal("0.00"), Decimal("-1.00")])
def test_zero_or_negative_transaction_amount_is_invalid(amount):
    provider, agent, account = provider_agent_account()
    findings = validate_transaction_input(
        transaction(amount=amount),
        ValidationSettings(),
        provider=provider,
        agent=agent,
        account=account,
        duplicate_exists=False,
        latest_transaction_time=None,
    )
    assert ValidationCategory.INVALID_AMOUNT in {item.category for item in findings}


def test_phone_like_identifier_and_secret_metadata_are_rejected():
    provider, agent, account = provider_agent_account()
    findings = validate_transaction_input(
        transaction(
            synthetic_transaction_ref="01712345678",
            source_metadata={"token": "secret-value"},
        ),
        ValidationSettings(),
        provider=provider,
        agent=agent,
        account=account,
        duplicate_exists=False,
        latest_transaction_time=None,
    )
    categories = {item.category for item in findings}
    assert ValidationCategory.INVALID_IDENTIFIER in categories
    assert ValidationCategory.MALFORMED_METADATA in categories


def test_invalid_currency_and_transaction_type_are_rejected():
    provider, agent, account = provider_agent_account()
    findings = validate_transaction_input(
        transaction(currency="USD", transaction_type="unsupported"),
        ValidationSettings(supported_currencies=("BDT",)),
        provider=provider,
        agent=agent,
        account=account,
        duplicate_exists=False,
        latest_transaction_time=None,
    )
    categories = {item.category for item in findings}
    assert ValidationCategory.INVALID_CURRENCY in categories
    assert ValidationCategory.INVALID_TRANSACTION_TYPE in categories


def test_future_timestamp_and_out_of_order_event_are_detected():
    future = now() + timedelta(hours=1)
    provider, agent, account = provider_agent_account()
    findings = validate_transaction_input(
        transaction(event_timestamp=future, received_timestamp=now()),
        ValidationSettings(future_tolerance_minutes=5),
        provider=provider,
        agent=agent,
        account=account,
        duplicate_exists=False,
        latest_transaction_time=now() + timedelta(hours=2),
    )
    categories = {item.category for item in findings}
    assert ValidationCategory.FUTURE_TIMESTAMP in categories
    assert ValidationCategory.OUT_OF_ORDER_EVENT in categories


def test_duplicate_transaction_is_warning_and_score_is_deterministic():
    provider, agent, account = provider_agent_account()
    findings = validate_transaction_input(
        transaction(),
        ValidationSettings(),
        provider=provider,
        agent=agent,
        account=account,
        duplicate_exists=True,
        latest_transaction_time=None,
    )
    first_score = score_findings(findings)
    second_score = score_findings(findings)
    assert ValidationCategory.DUPLICATE_TRANSACTION in {item.category for item in findings}
    assert first_score == second_score
    assert first_score.confidence_multiplier == Decimal("1.00")


def test_feed_delayed_stale_missing_and_conflicting_statuses():
    expected = now()
    delayed = validate_feed_status_input(
        feed(expected_timestamp=expected, received_timestamp=expected + timedelta(minutes=10)),
        ValidationSettings(feed_delay_minutes=5),
        provider=object(),
        agent=object(),
    )
    stale = validate_feed_status_input(
        feed(
            expected_timestamp=expected,
            last_successful_timestamp=expected - timedelta(minutes=30),
        ),
        ValidationSettings(stale_minutes=15),
        provider=object(),
        agent=object(),
    )
    missing = validate_feed_status_input(
        feed(source_status=FeedQualityStatus.MISSING, received_timestamp=None),
        ValidationSettings(),
        provider=object(),
        agent=object(),
    )
    conflict = validate_feed_status_input(
        feed(source_status=FeedQualityStatus.CONFLICTING),
        ValidationSettings(),
        provider=object(),
        agent=object(),
    )

    assert status_for_findings(delayed) == FeedQualityStatus.DELAYED
    assert status_for_findings(stale) == FeedQualityStatus.STALE
    assert status_for_findings(missing) == FeedQualityStatus.MISSING
    assert status_for_findings(conflict) == FeedQualityStatus.CONFLICTING


def test_quality_score_low_for_missing_feed():
    findings = validate_feed_status_input(
        feed(source_status=FeedQualityStatus.MISSING, received_timestamp=None),
        ValidationSettings(),
        provider=object(),
        agent=object(),
    )
    score = score_findings(findings)
    assert score.overall_score < Decimal("0.70")
    assert "confidence" in "confidence_multiplier"
