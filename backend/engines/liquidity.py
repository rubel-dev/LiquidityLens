"""Liquidity forecasting engine — predicts time to balance depletion per provider."""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from providers.base import ProviderBalanceResult, ProviderTransaction

RATE_WINDOW_MINUTES = 30


@dataclass
class LiquidityResult:
    provider: str
    balance: float | None
    rate_per_minute: float          # BDT outflow per minute
    eta_minutes: int | None         # None = no shortage predicted
    confidence: float               # 0–1
    uncertainty: str                # low|medium|high
    data_quality: str
    recommended_topup: float | None


def _outflow_rate(transactions: list[ProviderTransaction]) -> float:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=RATE_WINDOW_MINUTES)
    cash_outs = [
        t.amount for t in transactions
        if t.type == "cash_out" and t.timestamp >= cutoff
    ]
    if not cash_outs:
        return 0.0
    return sum(cash_outs) / RATE_WINDOW_MINUTES


def _confidence(balance_result: ProviderBalanceResult) -> tuple[float, str]:
    quality = balance_result.data_quality
    age = (datetime.now(timezone.utc) - balance_result.fetched_at).total_seconds()

    if quality in ("missing", "conflict"):
        return 0.15, "high"
    if quality == "delayed" or age > 300:
        return 0.40, "high"
    if age > 120:
        return 0.65, "medium"
    return 0.90, "low"


def analyze(
    balance_result: ProviderBalanceResult,
    transactions: list[ProviderTransaction],
) -> LiquidityResult:
    confidence, uncertainty = _confidence(balance_result)
    rate = _outflow_rate(transactions)
    balance = balance_result.balance

    if balance is None or balance_result.data_quality in ("missing", "conflict"):
        return LiquidityResult(
            provider=balance_result.provider,
            balance=None,
            rate_per_minute=0.0,
            eta_minutes=None,
            confidence=confidence,
            uncertainty=uncertainty,
            data_quality=balance_result.data_quality,
            recommended_topup=None,
        )

    if rate <= 0:
        return LiquidityResult(
            provider=balance_result.provider,
            balance=balance,
            rate_per_minute=0.0,
            eta_minutes=None,
            confidence=confidence,
            uncertainty=uncertainty,
            data_quality=balance_result.data_quality,
            recommended_topup=None,
        )

    eta = int(balance / rate)
    # Suggest enough topup for 4 hours at current rate
    recommended = round(max(0, rate * 240 - balance), 2)

    return LiquidityResult(
        provider=balance_result.provider,
        balance=balance,
        rate_per_minute=round(rate, 2),
        eta_minutes=eta,
        confidence=confidence,
        uncertainty=uncertainty,
        data_quality=balance_result.data_quality,
        recommended_topup=recommended if eta < 120 else None,
    )
