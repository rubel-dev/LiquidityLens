from datetime import datetime, timedelta
from decimal import Decimal

from app.persistence.models.enums import TransactionType
from app.scenarios.random_source import DeterministicRandom, validate_synthetic_identifier
from app.scenarios.schemas import GeneratedTransaction, ProfileName, ScenarioDefinition

PROFILE_TRANSACTION_COUNTS: dict[ProfileName, int] = {"small": 18, "medium": 45, "demo": 90}


def generate_transactions(
    definition: ScenarioDefinition,
    seed: str,
    run_ref: str,
    start_timestamp: datetime,
    profile: ProfileName,
) -> tuple[GeneratedTransaction, ...]:
    random = DeterministicRandom(f"{seed}:{definition.code}:transactions")
    count = PROFILE_TRANSACTION_COUNTS[profile]
    transactions: list[GeneratedTransaction] = []
    customer_span = 12 if definition.false_positive_case else 6

    if definition.code == "normal_day":
        customer_span = 20
    if definition.code == "liquidity_pressure_unusual_activity":
        customer_span = 3

    for index in range(1, count + 1):
        provider_code = ["BK", "NG", "RK"][(index + random.randint(0, 2)) % 3]
        transaction_type = _transaction_type(definition.code, index)
        amount = _amount(definition.code, index, random)
        occurred_at = start_timestamp + timedelta(minutes=index * 4)
        account_ref = validate_synthetic_identifier(f"SIM-ACCT-{provider_code}-0001")
        customer_ref = validate_synthetic_identifier(
            f"SIM-CUST-{((index - 1) % customer_span) + 1:04d}"
        )
        run_number = run_ref.rsplit("-", maxsplit=1)[-1]
        transaction_ref = validate_synthetic_identifier(f"SIM-TXN-{run_number}-{index:06d}")
        transactions.append(
            GeneratedTransaction(
                synthetic_transaction_ref=transaction_ref,
                provider_code=provider_code,
                synthetic_account_ref=account_ref,
                synthetic_customer_ref=customer_ref,
                transaction_type=transaction_type,
                amount=amount,
                occurred_at=occurred_at,
            )
        )
    return tuple(transactions)


def _transaction_type(code: str, index: int) -> TransactionType:
    if code in {"shared_cash_crisis", "liquidity_pressure_unusual_activity"}:
        return TransactionType.CASH_OUT
    if code == "hidden_provider_shortage" and index % 2 == 0:
        return TransactionType.CASH_IN
    if code in {"eid_rush", "salary_day_legitimate_spike"} and index % 4 != 0:
        return TransactionType.CASH_OUT
    return TransactionType.CASH_IN if index % 3 == 0 else TransactionType.CASH_OUT


def _amount(code: str, index: int, random: DeterministicRandom) -> Decimal:
    if code == "liquidity_pressure_unusual_activity" and index <= 12:
        return Decimal("980.00")
    if code in {"eid_rush", "salary_day_legitimate_spike"}:
        return random.money(400, 2400, step=50)
    if code == "shared_cash_crisis":
        return random.money(700, 1800, step=50)
    if code == "hidden_provider_shortage":
        return random.money(500, 1500, step=50)
    return random.money(100, 900, step=50)
