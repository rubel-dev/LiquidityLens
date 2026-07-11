"""Analysis pipeline: Scenario → Forecast → Anomaly → Alert in one call.

POST /api/v1/analyze/{run_ref}

After a scenario run generates raw transactions/balances/feeds, this endpoint
chains all deterministic engines and surfaces alerts the frontend can display.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.alerts.exceptions import AlertSourceError
from app.alerts.service import AlertService
from app.anomaly.service import AnomalyDetectionService
from app.api.schemas import AnalysisResponse, FindingSummary, ForecastSummary
from app.auth.scope import AccessScope, get_access_scope
from app.explanations.service import explain_finding, explain_forecast
from app.liquidity.schemas import RiskLevel
from app.liquidity.service import LiquidityForecastingService
from app.persistence.database import get_db_session
from app.persistence.models.agent import Agent
from app.persistence.models.enums import FeedQualityStatus
from app.persistence.models.feed import ProviderFeedStatus
from app.persistence.models.provider import Provider
from app.scenarios.exceptions import ScenarioNotFoundError
from app.scenarios.repository import ScenarioRepository

router = APIRouter(prefix="/analyze", tags=["Analytics"])
logger = logging.getLogger(__name__)
SESSION = Depends(get_db_session)
ACCESS = Depends(get_access_scope)

_ACTIONABLE_RISK = {RiskLevel.CRITICAL, RiskLevel.WARNING, RiskLevel.WATCH}


@router.post("/analyze/{run_ref}", response_model=AnalysisResponse, status_code=201)
def analyze_run(
    run_ref: str,
    session: Session = SESSION,
    scope: AccessScope = ACCESS,
) -> AnalysisResponse:
    """Run forecasting → anomaly detection → alert generation for a scenario run."""
    if not scope.has_any_role("ops", "risk", "manager", "demo"):
        raise HTTPException(status_code=403, detail="ops, risk, manager, or demo role required")

    # ── 1. Locate the scenario run & agent ────────────────────────────────────
    scenario_repo = ScenarioRepository(session)
    with session.begin():
        try:
            run = scenario_repo.find_run(run_ref)
            run_id = run.id
        except ScenarioNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        agent_id = session.scalar(select(Agent.id).where(Agent.synthetic_agent_ref == "SIM-AGENT-0001"))
        
    if agent_id is None:
        raise HTTPException(status_code=404, detail="demo agent not found — run a scenario first")

    # ── 2. Liquidity forecasting ──────────────────────────────────────────────
    forecast_results = LiquidityForecastingService(session).forecast_agent(
        agent_id, scenario_run_id=run_id
    )

    # ── 3. Anomaly detection ──────────────────────────────────────────────────
    finding_results = AnomalyDetectionService(session).detect_agent(
        agent_id, scenario_run_id=run_id
    )

    # ── 4. Build provider name lookup ─────────────────────────────────────────
    with session.begin():
        provider_names: dict[uuid.UUID, str] = {}
        for provider in session.scalars(select(Provider)).all():
            provider_names[provider.id] = provider.display_name

    # ── 5. Generate alerts from forecasts ────────────────────────────────────
    alert_service = AlertService(session)
    alert_ids: list[uuid.UUID] = []

    for forecast in forecast_results:
        if forecast.risk_level not in _ACTIONABLE_RISK:
            continue
        if forecast.forecast_id is None:
            continue
        try:
            alert = alert_service.create_liquidity_alert(forecast.forecast_id)
            alert_ids.append(alert.alert_id)
        except AlertSourceError:
            logger.exception("Failed to create liquidity alert for forecast_id=%s", forecast.forecast_id)

    # ── 6. Generate alerts from anomaly findings ──────────────────────────────
    for finding in finding_results:
        if finding.finding_id is None:
            continue
        try:
            alert = alert_service.create_anomaly_alert(finding.finding_id)
            alert_ids.append(alert.alert_id)
        except AlertSourceError:
            logger.exception("Failed to create anomaly alert for finding_id=%s", finding.finding_id)

    # ── 7. Generate alerts from degraded feed statuses ────────────────────────
    with session.begin():
        degraded_feed_ids = session.scalars(
            select(ProviderFeedStatus.id).where(
                ProviderFeedStatus.scenario_run_id == run_id,
                ProviderFeedStatus.status != FeedQualityStatus.COMPLETE,
                ProviderFeedStatus.agent_id.is_not(None),
            )
        ).all()

    for feed_id in degraded_feed_ids:
        try:
            alert = alert_service.create_data_quality_alert(feed_id)
            alert_ids.append(alert.alert_id)
        except (AlertSourceError, Exception):
            logger.exception("Failed to create data quality alert for feed_id=%s", feed_id)

    # ── 9. Build response with explanations ───────────────────────────────────
    forecast_summaries: list[ForecastSummary] = []
    for f in forecast_results:
        pname = "Shared cash" if f.provider_id is None else provider_names.get(f.provider_id, str(f.provider_id))
        en, bn = explain_forecast(f, pname)
        forecast_summaries.append(
            ForecastSummary(
                forecast_id=f.forecast_id or uuid.uuid4(),
                provider_id=f.provider_id,
                provider_name=pname,
                scope=f.scope.value,
                risk_level=f.risk_level.value,
                runway_minutes=None if f.runway_minutes is None else float(f.runway_minutes),
                confidence=float(f.confidence),
                explanation_en=en,
                explanation_bn=bn,
            )
        )

    finding_summaries: list[FindingSummary] = []
    for fi in finding_results:
        pname = provider_names.get(fi.provider_id, str(fi.provider_id))
        en, bn = explain_finding(fi, pname)
        finding_summaries.append(
            FindingSummary(
                finding_id=fi.finding_id or uuid.uuid4(),
                provider_id=fi.provider_id,
                severity=fi.severity.value,
                pattern=fi.pattern,
                confidence=float(fi.confidence),
                explanation_en=en,
                explanation_bn=bn,
            )
        )

    return AnalysisResponse(
        run_ref=run_ref,
        agent_id=agent_id,
        forecasts_created=len(forecast_results),
        findings_created=len(finding_results),
        alerts_created=len(alert_ids),
        forecasts=forecast_summaries,
        findings=finding_summaries,
        alert_ids=alert_ids,
    )
