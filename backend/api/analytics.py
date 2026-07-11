from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from core.database import get_db
from models.agent import Agent
from models.balance import ProviderBalance
from models.transaction import Transaction
from engines.liquidity import analyze as liquidity_analyze
from engines.anomaly.velocity import detect as velocity_detect
from engines.anomaly.clustering import detect as clustering_detect
from engines.anomaly.concentration import detect as concentration_detect
from providers.bkash import bkash_provider
from providers.nagad import nagad_provider
from providers.rocket import rocket_provider
from providers.base import ProviderTransaction
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
PROVIDERS = [bkash_provider, nagad_provider, rocket_provider]


@router.get("/liquidity/{agent_id}")
async def get_liquidity(agent_id: str, db: AsyncSession = Depends(get_db)):
    results = []
    for provider in PROVIDERS:
        balance_result = await provider.get_balance(agent_id)
        transactions = await provider.get_recent_transactions(agent_id, minutes=60)
        liq = liquidity_analyze(balance_result, transactions)
        results.append({
            "provider": liq.provider,
            "balance": liq.balance,
            "rate_per_minute": liq.rate_per_minute,
            "eta_minutes": liq.eta_minutes,
            "confidence": liq.confidence,
            "uncertainty": liq.uncertainty,
            "data_quality": liq.data_quality,
            "recommended_topup": liq.recommended_topup,
        })

    # Physical cash
    agent_result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "agent_id": agent_id,
        "physical_cash": float(agent.physical_cash),
        "providers": results,
        "aggregate_emoney": sum(r["balance"] or 0 for r in results),
    }


@router.get("/anomaly/{agent_id}/{provider}")
async def get_anomaly(agent_id: str, provider: str, db: AsyncSession = Depends(get_db)):
    provider_map = {"bkash": bkash_provider, "nagad": nagad_provider, "rocket": rocket_provider}
    p = provider_map.get(provider)
    if not p:
        raise HTTPException(status_code=400, detail="Invalid provider")

    transactions = await p.get_recent_transactions(agent_id, minutes=30)

    velocity = velocity_detect(transactions)
    clustering = clustering_detect(transactions)
    concentration = concentration_detect(transactions)

    any_flagged = velocity.flagged or clustering.flagged or concentration.flagged
    confidence = round(
        sum([velocity.flagged, clustering.flagged, concentration.flagged]) / 3, 3
    )

    return {
        "agent_id": agent_id,
        "provider": provider,
        "flagged": any_flagged,
        "confidence": confidence,
        "detectors": {
            "velocity": {
                "flagged": velocity.flagged,
                "count": velocity.count,
                "threshold": velocity.threshold,
                "note": velocity.day_type_note,
            },
            "clustering": {
                "flagged": clustering.flagged,
                "cluster_ratio": clustering.cluster_ratio,
                "dominant_range": clustering.dominant_range,
                "clustered_amounts": clustering.clustered_amounts,
            },
            "concentration": {
                "flagged": concentration.flagged,
                "unique_accounts": concentration.unique_accounts,
                "total_transactions": concentration.total_transactions,
                "concentration_ratio": concentration.concentration_ratio,
                "top_accounts": concentration.top_accounts,
            },
        },
    }


class WhatIfBody(BaseModel):
    agent_id: str
    provider: str
    demand_multiplier: float = 1.5


@router.post("/whatif")
async def what_if(body: WhatIfBody):
    provider_map = {"bkash": bkash_provider, "nagad": nagad_provider, "rocket": rocket_provider}
    p = provider_map.get(body.provider)
    if not p:
        raise HTTPException(status_code=400, detail="Invalid provider")

    balance_result = await p.get_balance(body.agent_id)
    transactions = await p.get_recent_transactions(body.agent_id, minutes=60)

    from engines.liquidity import analyze, _outflow_rate
    original = analyze(balance_result, transactions)
    adjusted_rate = original.rate_per_minute * body.demand_multiplier

    if adjusted_rate <= 0 or balance_result.balance is None:
        return {"original_eta": original.eta_minutes, "new_eta": None}

    new_eta = int(balance_result.balance / adjusted_rate)

    from ai.explainer import generate_whatif_summary
    summary = await generate_whatif_summary(
        body.provider,
        original.eta_minutes or 999,
        new_eta,
        body.demand_multiplier,
    )

    return {
        "provider": body.provider,
        "demand_multiplier": body.demand_multiplier,
        "original_eta_minutes": original.eta_minutes,
        "new_eta_minutes": new_eta,
        "original_rate_per_minute": original.rate_per_minute,
        "new_rate_per_minute": round(adjusted_rate, 2),
        "advisory": summary,
    }
