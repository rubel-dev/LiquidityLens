from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.persistence.models.enums import FeedQualityStatus, TransactionType
from app.scenarios.catalog import CANONICAL_SCENARIOS
from app.scenarios.exceptions import UnsafeSyntheticIdentifierError
from app.scenarios.generators import generate_scenario
from app.scenarios.random_source import validate_synthetic_identifier
from app.scenarios.schemas import GENERATOR_VERSION, ScenarioConfig


def config():
    return ScenarioConfig(profile="small", start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC))


def test_catalog_contains_all_canonical_scenarios():
    assert set(CANONICAL_SCENARIOS) == {
        "normal_day",
        "eid_rush",
        "hidden_provider_shortage",
        "shared_cash_crisis",
        "liquidity_pressure_unusual_activity",
        "salary_day_legitimate_spike",
        "delayed_feed",
        "missing_feed",
        "conflicting_balance",
        "agent_unavailable",
    }


def test_same_seed_and_start_time_produce_same_fingerprint():
    first = generate_scenario("normal_day", 1001, "SIM-RUN-000001", config())
    second = generate_scenario("normal_day", 1001, "SIM-RUN-000001", config())
    assert first.fingerprint == second.fingerprint


def test_different_seed_changes_fingerprint():
    first = generate_scenario("normal_day", 1001, "SIM-RUN-000001", config())
    second = generate_scenario("normal_day", 1002, "SIM-RUN-000001", config())
    assert first.fingerprint != second.fingerprint


def test_generation_rejects_naive_start_time():
    with pytest.raises(ValueError, match="timezone-aware"):
        generate_scenario(
            "normal_day",
            1001,
            "SIM-RUN-000001",
            ScenarioConfig(start_timestamp=datetime(2026, 7, 11, 9, 0)),
        )


def test_identifier_policy_rejects_phone_like_values():
    assert validate_synthetic_identifier("SIM-CUST-0001") == "SIM-CUST-0001"
    with pytest.raises(UnsafeSyntheticIdentifierError):
        validate_synthetic_identifier("01712345678")


def test_provider_balances_are_separate_and_shared_cash_has_no_provider_scope():
    scenario = generate_scenario("hidden_provider_shortage", 1001, "SIM-RUN-000001", config())
    provider_scopes = {snapshot.provider_code for snapshot in scenario.provider_balances}
    shared_scopes = {snapshot.provider_code for snapshot in scenario.shared_cash}

    assert provider_scopes == {"BK", "NG", "RK"}
    assert shared_scopes == {None}
    assert all(tx.provider_code in provider_scopes for tx in scenario.transactions)


def test_transaction_money_and_time_conventions_are_valid():
    scenario = generate_scenario("normal_day", 1001, "SIM-RUN-000001", config())

    assert all(tx.amount > Decimal("0.00") for tx in scenario.transactions)
    assert all(tx.currency == "BDT" for tx in scenario.transactions)
    assert all(tx.occurred_at.tzinfo is not None for tx in scenario.transactions)
    assert {tx.transaction_type for tx in scenario.transactions} <= {
        TransactionType.CASH_IN,
        TransactionType.CASH_OUT,
    }
    transaction_refs = {tx.synthetic_transaction_ref for tx in scenario.transactions}
    assert len(transaction_refs) == len(scenario.transactions)


def test_legitimate_spikes_are_false_positive_ground_truth_not_anomaly_positive():
    for scenario_code in ("eid_rush", "salary_day_legitimate_spike"):
        scenario = generate_scenario(scenario_code, 2001, "SIM-RUN-000001", config())
        assert {event.category for event in scenario.ground_truth} == {"legitimate_demand_spike"}
        assert all(event.false_positive_case for event in scenario.ground_truth)
        assert not any(event.anomaly_positive for event in scenario.ground_truth)


def test_unusual_activity_injects_review_ground_truth_without_fraud_label():
    scenario = generate_scenario(
        "liquidity_pressure_unusual_activity",
        5001,
        "SIM-RUN-000001",
        config(),
    )
    categories = {event.category for event in scenario.ground_truth}

    assert {"unusual_repeated_amounts", "unusual_velocity", "account_concentration"} <= categories
    assert any(event.anomaly_positive for event in scenario.ground_truth)
    assert "fraud" not in str(scenario.ground_truth).lower()


def test_feed_quality_scenarios_generate_expected_statuses_and_unknown_balance():
    delayed = generate_scenario("delayed_feed", 7001, "SIM-RUN-000001", config())
    missing = generate_scenario("missing_feed", 8001, "SIM-RUN-000001", config())
    conflicting = generate_scenario("conflicting_balance", 9001, "SIM-RUN-000001", config())

    assert FeedQualityStatus.DELAYED in {feed.status for feed in delayed.feed_statuses}
    assert FeedQualityStatus.MISSING in {feed.status for feed in missing.feed_statuses}
    assert FeedQualityStatus.CONFLICTING in {feed.status for feed in conflicting.feed_statuses}
    assert any(snapshot.amount is None for snapshot in missing.provider_balances)


def test_generator_version_is_explicit():
    assert GENERATOR_VERSION == "scenario-generator-v1"
