import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime

from app.scenarios.balance_generator import generate_balances
from app.scenarios.catalog import get_scenario
from app.scenarios.feed_generator import generate_feed_statuses
from app.scenarios.ground_truth import generate_ground_truth
from app.scenarios.schemas import (
    CATALOG_VERSION,
    GENERATOR_VERSION,
    GeneratedScenario,
    ScenarioConfig,
)
from app.scenarios.transaction_generator import generate_transactions


def generate_scenario(
    scenario_code: str,
    seed: str | int,
    run_ref: str,
    config: ScenarioConfig,
) -> GeneratedScenario:
    definition = get_scenario(scenario_code)
    start_timestamp = config.start_timestamp or datetime(2026, 7, 11, 9, 0, tzinfo=UTC)
    if start_timestamp.tzinfo is None:
        raise ValueError("scenario start timestamp must be timezone-aware")

    seed_text = str(seed)
    transactions = generate_transactions(
        definition,
        seed_text,
        run_ref,
        start_timestamp,
        config.profile,
    )
    provider_balances, shared_cash = generate_balances(definition, start_timestamp, transactions)
    feed_statuses = generate_feed_statuses(definition, start_timestamp)
    ground_truth = generate_ground_truth(definition, start_timestamp, transactions)
    generated_counts = {
        "transactions": len(transactions),
        "provider_balance_snapshots": len(provider_balances),
        "shared_cash_snapshots": len(shared_cash),
        "provider_feed_statuses": len(feed_statuses),
        "ground_truth_events": len(ground_truth),
    }
    scenario = GeneratedScenario(
        definition=definition,
        seed=seed_text,
        run_ref=run_ref,
        start_timestamp=start_timestamp,
        profile=config.profile,
        transactions=transactions,
        provider_balances=provider_balances,
        shared_cash=shared_cash,
        feed_statuses=feed_statuses,
        ground_truth=ground_truth,
        agent_available=definition.code != "agent_unavailable",
        generated_counts=generated_counts,
    )
    return replace(scenario, fingerprint=fingerprint_generated_scenario(scenario))


def fingerprint_generated_scenario(scenario: GeneratedScenario) -> str:
    payload = {
        "catalog_version": CATALOG_VERSION,
        "generator_version": GENERATOR_VERSION,
        "scenario_code": scenario.definition.code,
        "scenario_version": scenario.definition.version,
        "seed": scenario.seed,
        "start_timestamp": scenario.start_timestamp.isoformat(),
        "profile": scenario.profile,
        "transactions": [
            {
                "ref": tx.synthetic_transaction_ref,
                "provider": tx.provider_code,
                "account": tx.synthetic_account_ref,
                "customer": tx.synthetic_customer_ref,
                "type": tx.transaction_type.value,
                "amount": str(tx.amount),
                "occurred_at": tx.occurred_at.isoformat(),
            }
            for tx in scenario.transactions
        ],
        "provider_balances": [
            {
                "provider": balance.provider_code,
                "amount": None if balance.amount is None else str(balance.amount),
                "observed_at": balance.observed_at.isoformat(),
                "quality": balance.quality_status,
            }
            for balance in scenario.provider_balances
        ],
        "shared_cash": [
            {
                "amount": None if balance.amount is None else str(balance.amount),
                "observed_at": balance.observed_at.isoformat(),
            }
            for balance in scenario.shared_cash
        ],
        "feeds": [
            {
                "provider": feed.provider_code,
                "status": feed.status.value,
                "observed_at": feed.observed_at.isoformat(),
                "ingested_at": None if feed.ingested_at is None else feed.ingested_at.isoformat(),
            }
            for feed in scenario.feed_statuses
        ],
        "ground_truth": [
            {
                "category": event.category,
                "provider": event.provider_scope,
                "agent": event.agent_scope,
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat(),
                "affected": list(event.affected_transaction_refs),
                "anomaly_positive": event.anomaly_positive,
                "false_positive_case": event.false_positive_case,
            }
            for event in scenario.ground_truth
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()
