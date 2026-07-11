import uuid

from sqlalchemy.orm import Session

from app.confidence.schemas import ConfidenceOutcome
from app.persistence.models.analytics import ConfidenceAssessment


class ConfidenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def persist_core_outcome(
        self,
        agent_id: uuid.UUID,
        outcome: ConfidenceOutcome,
    ) -> uuid.UUID:
        assessment_id = uuid.uuid4()
        self.session.add(
            ConfidenceAssessment(
                id=assessment_id,
                subject_type="core_intelligence",
                subject_id=agent_id,
                confidence=outcome.score,
                reasons={
                    "tier": outcome.tier,
                    "signal_count": outcome.signal_count,
                    "weakest_signal": str(outcome.weakest_signal),
                    "evidence": list(outcome.evidence),
                    "recommendation": outcome.recommendation,
                    "deterministic": True,
                },
            )
        )
        self.session.flush()
        return assessment_id
