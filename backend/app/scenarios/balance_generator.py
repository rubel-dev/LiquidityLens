from collections.abc import Iterable
from datetime import datetime, timedelta
from decimal import Decimal

from app.persistence.models.enums import TransactionType
from app.scenarios.schemas import GeneratedBalanceSnapshot, GeneratedTransaction, ScenarioDefinition


def generate_balances(
    definition: ScenarioDefinition,
    start_timestamp: datetime,
    transactions: Iterable[GeneratedTransaction],
) -> tuple[tuple[GeneratedBalanceSnapshot, ...], tuple[GeneratedBalanceSnapshot, ...]]:
    provider_balances: dict[str, Decimal | None] = {
        "BK": Decimal("40000.00"),
        "NG": Decimal("38000.00"),
        "RK": Decimal("36000.00"),
    }
    shared_cash = Decimal("32000.00")
    if definition.code == "hidden_provider_shortage":
        provider_balances["BK"] = Decimal("6500.00")
    if definition.code == "shared_cash_crisis":
        shared_cash = Decimal("12500.00")
    if definition.code == "liquidity_pressure_unusual_activity":
        shared_cash = Decimal("18000.00")

    provider_snapshots: list[GeneratedBalanceSnapshot] = []
    shared_snapshots = [
        GeneratedBalanceSnapshot(None, shared_cash, start_timestamp, "complete"),
    ]
    for provider_code, amount in provider_balances.items():
        provider_snapshots.append(
            GeneratedBalanceSnapshot(provider_code, amount, start_timestamp, "complete"),
        )

    for tx in transactions:
        provider_balance = provider_balances[tx.provider_code]
        if provider_balance is None:
            continue
        if tx.transaction_type == TransactionType.CASH_IN:
            shared_cash += tx.amount
            provider_balances[tx.provider_code] = provider_balance - tx.amount
        if tx.transaction_type == TransactionType.CASH_OUT:
            shared_cash -= tx.amount
            provider_balances[tx.provider_code] = provider_balance + tx.amount
        if shared_cash < 0:
            shared_cash = Decimal("0.00")
        active_provider_balance = provider_balances[tx.provider_code]
        if active_provider_balance is not None and active_provider_balance < 0:
            provider_balances[tx.provider_code] = Decimal("0.00")

    final_time = start_timestamp + timedelta(hours=2)
    if definition.code == "missing_feed":
        provider_balances["NG"] = None
    if definition.code == "conflicting_balance":
        provider_balances["RK"] = Decimal("99999.00")

    for provider_code, amount in provider_balances.items():
        quality_status = "complete"
        if definition.code == "missing_feed" and provider_code == "NG":
            quality_status = "missing"
        if definition.code == "conflicting_balance" and provider_code == "RK":
            quality_status = "conflicting"
        provider_snapshots.append(
            GeneratedBalanceSnapshot(provider_code, amount, final_time, quality_status),
        )
    shared_snapshots.append(GeneratedBalanceSnapshot(None, shared_cash, final_time, "complete"))
    return tuple(provider_snapshots), tuple(shared_snapshots)
