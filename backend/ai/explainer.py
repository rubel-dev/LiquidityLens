"""OpenAI integration — generates Bengali alerts and English narratives."""
import asyncio
from openai import AsyncOpenAI
from core.config import settings
from .prompts import (
    liquidity_alert_bn,
    anomaly_alert_bn,
    anomaly_narrative_en,
    whatif_summary_en,
)
from .fallback import (
    liquidity_alert_bn_fallback,
    anomaly_alert_bn_fallback,
    anomaly_narrative_en_fallback,
)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def _call(prompt: str, model: str, max_tokens: int = 250) -> str | None:
    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.4,
            ),
            timeout=10.0,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


async def generate_liquidity_alert_bn(
    provider: str,
    eta_minutes: int,
    balance: float,
    rate: float,
    recommended_topup: float | None,
) -> str:
    prompt = liquidity_alert_bn(provider, eta_minutes, balance, rate, recommended_topup)
    result = await _call(prompt, settings.OPENAI_MODEL_FAST, max_tokens=200)
    return result or liquidity_alert_bn_fallback(provider, eta_minutes, balance)


async def generate_anomaly_alert_bn(
    provider: str,
    pattern: str,
    evidence_summary: str,
    confidence: float,
) -> str:
    prompt = anomaly_alert_bn(provider, pattern, evidence_summary, confidence)
    result = await _call(prompt, settings.OPENAI_MODEL_FAST, max_tokens=200)
    return result or anomaly_alert_bn_fallback(provider)


async def generate_anomaly_narrative_en(provider: str, evidence: dict) -> str:
    prompt = anomaly_narrative_en(provider, evidence)
    result = await _call(prompt, settings.OPENAI_MODEL_SMART, max_tokens=150)
    return result or anomaly_narrative_en_fallback(provider)


async def generate_whatif_summary(
    provider: str,
    original_eta: int,
    new_eta: int,
    demand_multiplier: float,
) -> str:
    prompt = whatif_summary_en(provider, original_eta, new_eta, demand_multiplier)
    result = await _call(prompt, settings.OPENAI_MODEL_FAST, max_tokens=100)
    return result or f"With {demand_multiplier}× demand, {provider.upper()} balance would deplete in {new_eta} minutes instead of {original_eta} minutes."
