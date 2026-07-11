import time
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_

from core.config import settings
from core.database import AsyncSessionLocal
from models.balance import ProviderBalance
from models.transaction import Transaction
from .base import BaseProvider, ProviderBalanceResult, ProviderTransaction


class RocketProvider(BaseProvider):
    name = "rocket"

    async def get_balance(self, agent_id: str) -> ProviderBalanceResult:
        start = time.monotonic()

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ProviderBalance)
                .where(
                    and_(
                        ProviderBalance.agent_id == agent_id,
                        ProviderBalance.provider == self.name,
                    )
                )
                .order_by(ProviderBalance.fetched_at.desc())
                .limit(1)
            )
            row = result.scalar_one_or_none()

        latency_ms = int((time.monotonic() - start) * 1000)

        if not row:
            return ProviderBalanceResult(
                provider=self.name,
                balance=None,
                fetched_at=datetime.now(timezone.utc),
                data_quality="missing",
                latency_ms=latency_ms,
            )

        age_seconds = (datetime.now(timezone.utc) - row.fetched_at).total_seconds()
        quality = "ok" if age_seconds < 120 else "delayed" if age_seconds < 300 else "missing"

        return ProviderBalanceResult(
            provider=self.name,
            balance=float(row.balance) if row.balance is not None else None,
            fetched_at=row.fetched_at,
            data_quality=quality,
            latency_ms=latency_ms,
        )

    async def get_recent_transactions(
        self, agent_id: str, minutes: int = 60
    ) -> list[ProviderTransaction]:
        since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Transaction)
                .where(
                    and_(
                        Transaction.agent_id == agent_id,
                        Transaction.provider == self.name,
                        Transaction.timestamp >= since,
                    )
                )
                .order_by(Transaction.timestamp.desc())
            )
            rows = result.scalars().all()

        return [
            ProviderTransaction(
                id=str(r.id),
                provider=self.name,
                type=r.type,
                amount=float(r.amount),
                account_id=r.account_id or "",
                timestamp=r.timestamp,
                status=r.status,
            )
            for r in rows
        ]


rocket_provider = RocketProvider()
