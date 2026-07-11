"""Background poller — runs every 30s, polls providers, fires alerts, pushes WebSocket."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from core.database import AsyncSessionLocal
from models.agent import Agent
from models.balance import ProviderBalance
from models.alert import Alert
from models.case import Case
from providers.bkash import bkash_provider
from providers.nagad import nagad_provider
from providers.rocket import rocket_provider
from engines.liquidity import analyze as liquidity_analyze
from engines.anomaly.velocity import detect as velocity_detect
from engines.anomaly.clustering import detect as clustering_detect
from engines.anomaly.concentration import detect as concentration_detect
from engines.coordinator import route, determine_severity
from ai.explainer import generate_liquidity_alert_bn, generate_anomaly_alert_bn
from api.ws import manager

PROVIDERS = [bkash_provider, nagad_provider, rocket_provider]
LIQUIDITY_THRESHOLD_MINUTES = 90   # alert if ETA < 90 minutes


async def poll_once():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Agent).where(Agent.status == "active"))
        agents = result.scalars().all()

    for agent in agents:
        for provider in PROVIDERS:
            await _check_agent_provider(str(agent.id), provider)


async def _check_agent_provider(agent_id: str, provider):
    balance_result = await provider.get_balance(agent_id)
    transactions = await provider.get_recent_transactions(agent_id, minutes=60)

    # Save latest balance snapshot
    async with AsyncSessionLocal() as db:
        db.add(ProviderBalance(
            agent_id=agent_id,
            provider=provider.name,
            balance=balance_result.balance,
            fetched_at=balance_result.fetched_at,
            data_quality=balance_result.data_quality,
            latency_ms=balance_result.latency_ms,
        ))
        await db.commit()

    # Data quality alert
    if balance_result.data_quality in ("missing", "conflict"):
        await _maybe_fire_alert(
            agent_id=agent_id,
            provider=provider.name,
            alert_type="data_quality",
            severity="medium",
            message_en=f"{provider.name.capitalize()} data feed is {balance_result.data_quality}. Confidence withheld.",
            message_bn=None,
            evidence={"data_quality": balance_result.data_quality},
            confidence=0.15,
            uncertainty="high",
            eta_minutes=None,
        )
        return

    # Liquidity check
    liq = liquidity_analyze(balance_result, transactions)
    if liq.eta_minutes is not None and liq.eta_minutes < LIQUIDITY_THRESHOLD_MINUTES:
        severity = determine_severity(liq.eta_minutes, "liquidity")
        message_bn = await generate_liquidity_alert_bn(
            provider=provider.name,
            eta_minutes=liq.eta_minutes,
            balance=liq.balance or 0,
            rate=liq.rate_per_minute * 60,
            recommended_topup=liq.recommended_topup,
        )
        await _maybe_fire_alert(
            agent_id=agent_id,
            provider=provider.name,
            alert_type="liquidity",
            severity=severity,
            message_en=f"{provider.name.capitalize()} balance depletes in ~{liq.eta_minutes} min. Rate: ৳{liq.rate_per_minute:.0f}/min.",
            message_bn=message_bn,
            evidence={"balance": liq.balance, "rate_per_minute": liq.rate_per_minute, "recommended_topup": liq.recommended_topup},
            confidence=liq.confidence,
            uncertainty=liq.uncertainty,
            eta_minutes=liq.eta_minutes,
        )

    # Anomaly check
    velocity = velocity_detect(transactions)
    clustering = clustering_detect(transactions)
    concentration = concentration_detect(transactions)

    detectors_flagged = [d for d in [velocity.flagged, clustering.flagged, concentration.flagged] if d]
    if len(detectors_flagged) >= 2:
        confidence = round(len(detectors_flagged) / 3, 3)
        patterns = []
        if velocity.flagged:
            patterns.append(f"{velocity.count} transactions in {velocity.window_minutes}min (threshold: {velocity.threshold})")
        if clustering.flagged:
            patterns.append(f"Amounts clustered in {clustering.dominant_range} ({clustering.cluster_ratio*100:.0f}% of window)")
        if concentration.flagged:
            patterns.append(f"{concentration.unique_accounts} unique accounts / {concentration.total_transactions} transactions (ratio: {concentration.concentration_ratio})")

        pattern_summary = "; ".join(patterns)
        severity = "high" if confidence >= 0.67 else "medium"
        message_bn = await generate_anomaly_alert_bn(
            provider=provider.name,
            pattern=pattern_summary,
            evidence_summary=pattern_summary,
            confidence=confidence,
        )
        await _maybe_fire_alert(
            agent_id=agent_id,
            provider=provider.name,
            alert_type="anomaly",
            severity=severity,
            message_en=f"Unusual activity on {provider.name.capitalize()}: {pattern_summary}. Requires human review.",
            message_bn=message_bn,
            evidence={
                "velocity": {"flagged": velocity.flagged, "count": velocity.count, "threshold": velocity.threshold},
                "clustering": {"flagged": clustering.flagged, "ratio": clustering.cluster_ratio, "range": clustering.dominant_range, "amounts": clustering.clustered_amounts},
                "concentration": {"flagged": concentration.flagged, "ratio": concentration.concentration_ratio, "top_accounts": concentration.top_accounts},
            },
            confidence=confidence,
            uncertainty="high" if confidence < 0.7 else "medium",
            eta_minutes=None,
        )


async def _maybe_fire_alert(
    agent_id: str,
    provider: str,
    alert_type: str,
    severity: str,
    message_en: str,
    message_bn: str | None,
    evidence: dict,
    confidence: float,
    uncertainty: str,
    eta_minutes: int | None,
):
    async with AsyncSessionLocal() as db:
        # Deduplicate — skip if open alert of same type+provider exists
        existing = await db.execute(
            select(Alert).where(
                Alert.agent_id == agent_id,
                Alert.provider == provider,
                Alert.type == alert_type,
                Alert.status.in_(["open", "acknowledged"]),
            )
        )
        if existing.scalar_one_or_none():
            return

        routing = route(alert_type, severity, provider)
        alert = Alert(
            id=uuid.uuid4(),
            agent_id=agent_id,
            provider=provider,
            type=alert_type,
            severity=severity,
            message_en=message_en,
            message_bn=message_bn,
            evidence=evidence,
            confidence=confidence,
            uncertainty=uncertainty,
            eta_minutes=eta_minutes,
            owner_role=routing.owner_role,
            owner_name=routing.owner_name,
            status="open",
        )
        db.add(alert)
        await db.flush()

        case = Case(
            id=uuid.uuid4(),
            alert_id=alert.id,
            assigned_to=routing.owner_name,
            assigned_role=routing.owner_role,
            notes=[{
                "author": "System",
                "text": f"Alert created. Assigned to {routing.owner_name}. {routing.recommended_action}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        )
        db.add(case)
        await db.commit()

        # Push to all WebSocket clients
        await manager.broadcast({
            "type": "new_alert",
            "data": {
                "id": str(alert.id),
                "agent_id": agent_id,
                "provider": provider,
                "alert_type": alert_type,
                "severity": severity,
                "message_en": message_en,
                "message_bn": message_bn,
                "confidence": confidence,
                "eta_minutes": eta_minutes,
                "owner_name": routing.owner_name,
            },
        })
