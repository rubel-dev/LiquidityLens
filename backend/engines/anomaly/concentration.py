"""Detector 3: account concentration — same few accounts transacting repeatedly."""
from dataclasses import dataclass
from providers.base import ProviderTransaction
from datetime import datetime, timezone, timedelta

WINDOW_MINUTES = 15
CONCENTRATION_THRESHOLD = 0.4   # unique_accounts / total_txns below this → flag
MIN_TXN_COUNT = 4


@dataclass
class ConcentrationResult:
    flagged: bool
    unique_accounts: int
    total_transactions: int
    concentration_ratio: float
    top_accounts: list[dict]   # [{account_id, count, total_amount}]


def detect(transactions: list[ProviderTransaction]) -> ConcentrationResult:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=WINDOW_MINUTES)
    window = [t for t in transactions if t.timestamp >= cutoff]

    if len(window) < MIN_TXN_COUNT:
        return ConcentrationResult(
            flagged=False,
            unique_accounts=0,
            total_transactions=len(window),
            concentration_ratio=1.0,
            top_accounts=[],
        )

    account_map: dict[str, dict] = {}
    for t in window:
        acc = t.account_id or "unknown"
        if acc not in account_map:
            account_map[acc] = {"count": 0, "total_amount": 0.0}
        account_map[acc]["count"] += 1
        account_map[acc]["total_amount"] += t.amount

    unique = len(account_map)
    total = len(window)
    ratio = unique / total

    top = sorted(
        [{"account_id": k, **v} for k, v in account_map.items()],
        key=lambda x: x["count"],
        reverse=True,
    )[:5]

    return ConcentrationResult(
        flagged=ratio < CONCENTRATION_THRESHOLD,
        unique_accounts=unique,
        total_transactions=total,
        concentration_ratio=round(ratio, 3),
        top_accounts=top,
    )
