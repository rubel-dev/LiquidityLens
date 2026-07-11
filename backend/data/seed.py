"""
Seed script — run once to populate Neon with demo data.
Usage:  cd backend && python -m data.seed
"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import insert
from core.database import AsyncSessionLocal, engine, Base
from models.agent import Agent
from models.balance import ProviderBalance
from models.transaction import Transaction
from models.baseline import TransactionBaseline
from data.synthetic import (
    generate_normal_transactions,
    generate_anomaly_velocity,
    initial_balances,
    initial_balances_normal,
    get_day_type,
)

DEMO_AGENTS = [
    {"name": "Karim Mia",      "area": "Mirpur-10, Dhaka",       "phone": "01711000001", "physical_cash": 8500.00},
    {"name": "Rina Begum",     "area": "Dhanmondi-15, Dhaka",    "phone": "01819000002", "physical_cash": 22000.00},
    {"name": "Salam Ahmed",    "area": "Uttara Sector-7, Dhaka", "phone": "01711000003", "physical_cash": 15000.00},
    {"name": "Fatema Khatun",  "area": "Motijheel, Dhaka",       "phone": "01819000004", "physical_cash": 31000.00},
    {"name": "Rubel Hossain",  "area": "Gulshan-2, Dhaka",       "phone": "01711000005", "physical_cash": 18000.00},
]

PROVIDERS = ["bkash", "nagad", "rocket"]
HOURS_OF_DAY = list(range(24))
DAY_TYPES = ["weekday", "weekend", "eid", "eid_before", "salary_day", "friday"]


async def seed():
    async with AsyncSessionLocal() as db:
        # Create agents
        agent_ids = {}
        for i, a in enumerate(DEMO_AGENTS):
            agent_id = uuid.uuid4()
            agent_ids[a["name"]] = agent_id
            db.add(Agent(
                id=agent_id,
                name=a["name"],
                area=a["area"],
                phone=a["phone"],
                physical_cash=a["physical_cash"],
                status="active",
            ))

        await db.flush()

        # Balances — Karim Mia gets low bKash (Scenario A), others healthy
        karim_id = str(agent_ids["Karim Mia"])
        for bal in initial_balances(karim_id):
            db.add(ProviderBalance(
                agent_id=bal["agent_id"],
                provider=bal["provider"],
                balance=bal["balance"],
                data_quality=bal["data_quality"],
                fetched_at=datetime.now(timezone.utc),
            ))

        for name, aid in agent_ids.items():
            if name == "Karim Mia":
                continue
            for bal in initial_balances_normal(str(aid)):
                db.add(ProviderBalance(
                    agent_id=bal["agent_id"],
                    provider=bal["provider"],
                    balance=bal["balance"],
                    data_quality=bal["data_quality"],
                    fetched_at=datetime.now(timezone.utc),
                ))

        await db.flush()

        # Transactions — normal 6h history for all agents
        now = datetime.now(timezone.utc)
        day_type = get_day_type(now)
        for name, aid in agent_ids.items():
            for provider in PROVIDERS:
                txns = generate_normal_transactions(str(aid), provider, hours_back=6, day_type=day_type)
                for t in txns:
                    db.add(Transaction(
                        id=uuid.UUID(t["id"]),
                        agent_id=aid,
                        provider=t["provider"],
                        type=t["type"],
                        amount=t["amount"],
                        account_id=t["account_id"],
                        timestamp=t["timestamp"],
                        status=t["status"],
                    ))

        # Anomaly seed for Karim bKash — velocity + clustering
        for t in generate_anomaly_velocity(karim_id, "bkash"):
            db.add(Transaction(
                id=uuid.UUID(t["id"]),
                agent_id=uuid.UUID(karim_id),
                provider=t["provider"],
                type=t["type"],
                amount=t["amount"],
                account_id=t["account_id"],
                timestamp=t["timestamp"],
                status=t["status"],
            ))

        # Baselines — per provider, per hour, per day type
        BASELINE_COUNTS = {
            "weekday":    {"avg": 8,  "stddev": 2},
            "weekend":    {"avg": 5,  "stddev": 1.5},
            "friday":     {"avg": 10, "stddev": 2.5},
            "salary_day": {"avg": 14, "stddev": 3},
            "eid":        {"avg": 24, "stddev": 5},
            "eid_before": {"avg": 20, "stddev": 4},
        }
        for aid in agent_ids.values():
            for provider in PROVIDERS:
                for hour in HOURS_OF_DAY:
                    for day_type_key, stats in BASELINE_COUNTS.items():
                        hour_factor = 1.5 if 10 <= hour <= 18 else 0.5
                        db.add(TransactionBaseline(
                            agent_id=aid,
                            provider=provider,
                            hour_of_day=hour,
                            day_type=day_type_key,
                            avg_count=round(stats["avg"] * hour_factor, 2),
                            avg_amount=5000.0,
                            stddev=round(stats["stddev"] * hour_factor, 2),
                        ))

        await db.commit()
        print("Seed complete - Neon database populated.")
        print(f"   Demo agent: Karim Mia  id={karim_id}")


if __name__ == "__main__":
    asyncio.run(seed())
