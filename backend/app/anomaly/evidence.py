from decimal import Decimal

from app.anomaly.schemas import AnomalyEvidence


def fingerprint_evidence(
    *,
    cluster_count: int,
    cluster_low: Decimal,
    cluster_high: Decimal,
    active_count: int,
    baseline_rate: Decimal,
    velocity_ratio: Decimal,
    group_size: int,
    window_minutes: int,
) -> tuple[AnomalyEvidence, ...]:
    return (
        AnomalyEvidence(
            "repeated_amount",
            "Repeated or near-identical amounts",
            f"{cluster_count} events between {cluster_low} and {cluster_high} BDT",
            Decimal("0.25"),
            "Amounts are grouped using the configured deterministic similarity tolerance.",
        ),
        AnomalyEvidence(
            "velocity",
            "Cash-out velocity",
            f"{active_count} events; {velocity_ratio}x baseline",
            Decimal("0.30"),
            "Current provider-scoped window count compared with its prior synthetic baseline.",
        ),
        AnomalyEvidence(
            "concentrated_group",
            "Concentrated synthetic group",
            f"{group_size} synthetic customer references",
            Decimal("0.20"),
            "Only synthetic non-phone-like references are counted.",
        ),
        AnomalyEvidence(
            "time_window_deviation",
            "Time-window deviation",
            f"{active_count} cash-outs in {window_minutes} minutes",
            Decimal("0.10"),
            "The active rolling window is evaluated independently for this provider.",
        ),
        AnomalyEvidence(
            "baseline_deviation",
            "Baseline deviation",
            f"baseline {baseline_rate} events per window",
            Decimal("0.15"),
            "A missing baseline reduces confidence and is never silently treated as certainty.",
        ),
    )
