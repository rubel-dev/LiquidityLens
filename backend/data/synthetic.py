"""Generates realistic synthetic transaction streams for demo agents."""
import random
import uuid
from datetime import datetime, timezone, timedelta


PROVIDERS = ["bkash", "nagad", "rocket"]
TX_TYPES = ["cash_out", "cash_out", "cash_out", "cash_in", "send", "receive"]  # weighted toward cash_out

DEMAND_MULTIPLIERS = {
    "eid": 3.0,
    "eid_before": 2.5,
    "salary_day": 1.8,
    "friday": 1.3,
    "weekday": 1.0,
    "weekend": 0.8,
}


def get_day_type(dt: datetime) -> str:
    day = dt.day
    weekday = dt.weekday()
    if day in (1, 25, 26, 27, 28, 29, 30):
        return "salary_day"
    if weekday == 4:  # Friday
        return "friday"
    if weekday in (5, 6):
        return "weekend"
    return "weekday"


def generate_normal_transactions(
    agent_id: str,
    provider: str,
    hours_back: int = 6,
    day_type: str = "weekday",
) -> list[dict]:
    multiplier = DEMAND_MULTIPLIERS.get(day_type, 1.0)
    base_rate = 8  # transactions per hour
    transactions = []
    now = datetime.now(timezone.utc)

    for h in range(hours_back, 0, -1):
        hour_start = now - timedelta(hours=h)
        count = max(1, int(random.gauss(base_rate * multiplier, 2)))
        for _ in range(count):
            offset = random.uniform(0, 3600)
            ts = hour_start + timedelta(seconds=offset)
            amount = round(random.uniform(500, 8000), 2)
            transactions.append({
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "provider": provider,
                "type": random.choice(TX_TYPES),
                "amount": amount,
                "account_id": f"01{''.join([str(random.randint(0,9)) for _ in range(9)])}",
                "timestamp": ts,
                "status": "completed",
            })

    return transactions


def generate_anomaly_velocity(agent_id: str, provider: str) -> list[dict]:
    """8 cash-out transactions in 12 minutes from 2 accounts — triggers velocity + concentration."""
    now = datetime.now(timezone.utc)
    accounts = [
        f"017{random.randint(10000000, 99999999)}",
        f"018{random.randint(10000000, 99999999)}",
    ]
    transactions = []
    base_amount = round(random.uniform(4800, 5200), 2)

    for i in range(8):
        ts = now - timedelta(minutes=12 - i * 1.4)
        amount = round(base_amount + random.uniform(-80, 80), 2)
        transactions.append({
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "provider": provider,
            "type": "cash_out",
            "amount": amount,
            "account_id": accounts[i % 2],
            "timestamp": ts,
            "status": "completed",
        })

    return transactions


def generate_salary_day_spike(agent_id: str, provider: str) -> list[dict]:
    """Normal high-volume on salary day — should NOT trigger anomaly (baseline-aware)."""
    return generate_normal_transactions(
        agent_id, provider, hours_back=1, day_type="salary_day"
    )


def initial_balances(agent_id: str) -> list[dict]:
    """Starting balances for a demo agent — bKash deliberately low for Scenario A."""
    return [
        {"agent_id": agent_id, "provider": "bkash",  "balance": 1200.00,  "data_quality": "ok"},
        {"agent_id": agent_id, "provider": "nagad",   "balance": 45000.00, "data_quality": "ok"},
        {"agent_id": agent_id, "provider": "rocket",  "balance": 35800.00, "data_quality": "ok"},
    ]


def initial_balances_normal(agent_id: str) -> list[dict]:
    """Healthy balances for supporting agents."""
    return [
        {"agent_id": agent_id, "provider": "bkash",  "balance": round(random.uniform(20000, 80000), 2), "data_quality": "ok"},
        {"agent_id": agent_id, "provider": "nagad",   "balance": round(random.uniform(15000, 60000), 2), "data_quality": "ok"},
        {"agent_id": agent_id, "provider": "rocket",  "balance": round(random.uniform(10000, 50000), 2), "data_quality": "ok"},
    ]
