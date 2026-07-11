import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.anomaly.service import AnomalyDetectionService
from app.confidence.engine import fuse_core_confidence
from app.confidence.repository import ConfidenceRepository
from app.confidence.schemas import CoreIntelligenceResult, CoreSignal
from app.liquidity.schemas import RiskLevel
from app.liquidity.service import LiquidityForecastingService


class CoreIntelligenceService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ConfidenceRepository(session)

    def analyze_agent(
        self,
        agent_id: uuid.UUID,
        *,
        scenario_run_id: uuid.UUID | None = None,
        generated_at: datetime | None = None,
    ) -> CoreIntelligenceResult:
        forecasts = LiquidityForecastingService(self.session).forecast_agent(
            agent_id,
            scenario_run_id=scenario_run_id,
            generated_at=generated_at,
        )
        findings = AnomalyDetectionService(self.session).detect_agent(
            agent_id,
            scenario_run_id=scenario_run_id,
            detected_at=generated_at,
        )
        signals = tuple(
            CoreSignal(
                signal_id=str(item.forecast_id or "unpersisted"),
                signal_type=f"liquidity:{item.scope.value}",
                confidence=item.confidence,
                material_risk=item.risk_level in {RiskLevel.WARNING, RiskLevel.CRITICAL},
                review_required=False,
            )
            for item in forecasts
        ) + tuple(
            CoreSignal(
                signal_id=str(item.finding_id or "unpersisted"),
                signal_type=f"anomaly:{item.pattern}",
                confidence=item.confidence,
                material_risk=False,
                review_required=item.requires_review,
            )
            for item in findings
        )
        outcome = fuse_core_confidence(signals)
        with self.session.begin():
            assessment_id = self.repository.persist_core_outcome(agent_id, outcome)
        return CoreIntelligenceResult(
            agent_id=agent_id,
            forecasts=forecasts,
            anomaly_findings=findings,
            confidence=outcome,
            recommendation=outcome.recommendation,
            confidence_assessment_id=assessment_id,
        )
