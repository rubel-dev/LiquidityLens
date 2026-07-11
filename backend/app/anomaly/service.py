import uuid
from dataclasses import replace
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.anomaly.detector import detect_near_identical_velocity
from app.anomaly.repository import AnomalyRepository
from app.anomaly.schemas import AnomalyFindingResult, AnomalyRequest, AnomalyRuleConfig


class AnomalyDetectionService:
    def __init__(self, session: Session, config: AnomalyRuleConfig | None = None) -> None:
        self.session = session
        self.config = config or AnomalyRuleConfig()
        self.repository = AnomalyRepository(session)

    def detect_agent(
        self,
        agent_id: uuid.UUID,
        *,
        scenario_run_id: uuid.UUID | None = None,
        detected_at: datetime | None = None,
    ) -> tuple[AnomalyFindingResult, ...]:
        with self.session.begin():
            self.repository.require_agent(agent_id)
            run = self.repository.require_run(scenario_run_id)
            active_time = (
                detected_at or (None if run is None else run.ended_at) or datetime.now(UTC)
            )
            event_context = self.repository.event_context(run)
            findings: list[AnomalyFindingResult] = []
            for provider_id in self.repository.provider_ids_for_agent(agent_id):
                request = AnomalyRequest(
                    agent_id=agent_id,
                    provider_id=provider_id,
                    transactions=self.repository.cash_out_transactions(
                        agent_id,
                        provider_id,
                        scenario_run_id,
                        active_time,
                        self.config,
                    ),
                    detected_at=active_time,
                    data_quality=self.repository.data_quality(
                        agent_id,
                        provider_id,
                        scenario_run_id,
                    ),
                    event_context=event_context,
                    config=self.config,
                )
                finding = detect_near_identical_velocity(request)
                if finding is None:
                    continue
                finding_id = self.repository.persist(finding, self.config)
                findings.append(replace(finding, finding_id=finding_id))
            self.session.flush()
            return tuple(findings)
