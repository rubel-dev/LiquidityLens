"""Detector 2: amount clustering — multiple transactions with near-identical amounts."""
from dataclasses import dataclass
from providers.base import ProviderTransaction
from datetime import datetime, timezone, timedelta

WINDOW_MINUTES = 15
BIN_WIDTH = 100        # BDT — amounts within ±50 of each other are "clustered"
CLUSTER_RATIO = 0.6    # if >60% of amounts fall in one bin → flag
MIN_TXN_COUNT = 4


@dataclass
class ClusteringResult:
    flagged: bool
    cluster_ratio: float
    dominant_range: str
    transaction_count: int
    clustered_amounts: list[float]


def detect(transactions: list[ProviderTransaction]) -> ClusteringResult:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=WINDOW_MINUTES)
    window = [t for t in transactions if t.timestamp >= cutoff and t.type == "cash_out"]

    if len(window) < MIN_TXN_COUNT:
        return ClusteringResult(
            flagged=False,
            cluster_ratio=0.0,
            dominant_range="",
            transaction_count=len(window),
            clustered_amounts=[],
        )

    amounts = [t.amount for t in window]
    bins: dict[int, list[float]] = {}
    for amt in amounts:
        key = int(amt // BIN_WIDTH)
        bins.setdefault(key, []).append(amt)

    if not bins:
        return ClusteringResult(flagged=False, cluster_ratio=0.0, dominant_range="", transaction_count=len(window), clustered_amounts=[])

    dominant_key = max(bins, key=lambda k: len(bins[k]))
    dominant_amounts = bins[dominant_key]
    ratio = len(dominant_amounts) / len(amounts)

    low = dominant_key * BIN_WIDTH
    high = low + BIN_WIDTH

    return ClusteringResult(
        flagged=ratio >= CLUSTER_RATIO,
        cluster_ratio=round(ratio, 3),
        dominant_range=f"৳{low:,.0f}–৳{high:,.0f}",
        transaction_count=len(window),
        clustered_amounts=sorted(dominant_amounts),
    )
