from datetime import datetime, timedelta

from app.scenarios.schemas import GeneratedTransaction, GroundTruthEvent, ScenarioDefinition

ALLOWED_GROUND_TRUTH_CATEGORIES = {
    "normal",
    "legitimate_demand_spike",
    "provider_liquidity_pressure",
    "shared_cash_pressure",
    "unusual_repeated_amounts",
    "unusual_velocity",
    "account_concentration",
    "delayed_feed",
    "missing_feed",
    "stale_feed",
    "conflicting_balance",
    "agent_unavailable",
}


def generate_ground_truth(
    definition: ScenarioDefinition,
    start_timestamp: datetime,
    transactions: tuple[GeneratedTransaction, ...],
) -> tuple[GroundTruthEvent, ...]:
    events: list[GroundTruthEvent] = []
    affected = tuple(tx.synthetic_transaction_ref for tx in transactions[:12])
    provider_scope = (
        "BK" if "provider_liquidity_pressure" in definition.expected_ground_truth else None
    )

    for category in definition.expected_ground_truth:
        if category not in ALLOWED_GROUND_TRUTH_CATEGORIES:
            raise ValueError(f"unsupported ground-truth category: {category}")
        events.append(
            GroundTruthEvent(
                category=category,
                provider_scope=provider_scope if category != "shared_cash_pressure" else None,
                agent_scope="SIM-AGENT-0001",
                start_time=start_timestamp + timedelta(minutes=10),
                end_time=start_timestamp + timedelta(hours=2),
                affected_transaction_refs=affected
                if category
                in {"unusual_repeated_amounts", "unusual_velocity", "account_concentration"}
                else (),
                anomaly_positive=definition.anomaly_positive
                and category
                in {"unusual_repeated_amounts", "unusual_velocity", "account_concentration"},
                false_positive_case=definition.false_positive_case,
            )
        )
    return tuple(events)
