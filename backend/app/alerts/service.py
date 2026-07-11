import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.alerts.exceptions import (
    AlertAuthorizationError,
    AlertConflictError,
    AlertSourceError,
)
from app.alerts.repository import AlertRepository
from app.alerts.schemas import AlertEvidence, AlertResult, AlertType
from app.auth.scope import AccessScope
from app.persistence.models.enums import AlertPriority, AlertStatus, FeedQualityStatus


class AlertService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AlertRepository(session)

    def create_liquidity_alert(self, forecast_id: uuid.UUID) -> AlertResult:
        with self.session.begin():
            existing = self.repository.find_source_alert("liquidity_forecast", forecast_id)
            if existing is not None:
                return self.repository.to_result(existing)
            forecast = self.repository.require_forecast(forecast_id)
            evidence = self.repository.source_evidence(forecast_id=forecast.id)
            risk = str(_forecast_summary(evidence).get("risk_level", "unknown"))
            priority = {
                "critical": AlertPriority.CRITICAL,
                "warning": AlertPriority.HIGH,
                "watch": AlertPriority.MEDIUM,
            }.get(risk)
            if priority is None:
                raise AlertSourceError("forecast does not contain actionable shortage risk")
            alert = self.repository.create(
                alert_type=AlertType.LIQUIDITY_SHORTAGE.value,
                priority=priority,
                provider_id=forecast.provider_id,
                agent_id=forecast.agent_id,
                summary=f"{risk.title()} liquidity runway risk requires human review.",
                next_step=(
                    "Review the known balance, demand evidence, and approved operational options. "
                    "Do not initiate an automatic transfer or refill."
                ),
                confidence=self.repository.source_confidence("liquidity_forecast", forecast.id),
                source_type="liquidity_forecast",
                source_id=forecast.id,
                evidence=evidence,
            )
            self.session.flush()
            return self.repository.to_result(alert)

    def create_anomaly_alert(self, finding_id: uuid.UUID) -> AlertResult:
        with self.session.begin():
            existing = self.repository.find_source_alert("anomaly_finding", finding_id)
            if existing is not None:
                return self.repository.to_result(existing)
            finding = self.repository.require_finding(finding_id)
            priority = {
                "critical": AlertPriority.CRITICAL,
                "high": AlertPriority.HIGH,
                "medium": AlertPriority.MEDIUM,
                "low": AlertPriority.LOW,
            }[finding.severity]
            alert = self.repository.create(
                alert_type=AlertType.ANOMALY_FINDING.value,
                priority=priority,
                provider_id=finding.provider_id,
                agent_id=finding.agent_id,
                summary="A deterministic transaction pattern requires human review.",
                next_step=(
                    "Review the evidence fingerprint and legitimate event context. "
                    "This finding is not proof of wrongdoing."
                ),
                confidence=self.repository.source_confidence("anomaly_finding", finding.id),
                source_type="anomaly_finding",
                source_id=finding.id,
                evidence=self.repository.source_evidence(finding_id=finding.id),
            )
            self.session.flush()
            return self.repository.to_result(alert)

    def create_data_quality_alert(self, feed_status_id: uuid.UUID) -> AlertResult:
        with self.session.begin():
            existing = self.repository.find_source_alert("provider_feed_status", feed_status_id)
            if existing is not None:
                return self.repository.to_result(existing)
            feed = self.repository.require_feed_status(feed_status_id)
            if feed.agent_id is None:
                raise AlertSourceError("feed status has no agent scope")
            if feed.status == FeedQualityStatus.COMPLETE:
                raise AlertSourceError("complete feed is not eligible for a data-quality alert")
            priority = (
                AlertPriority.HIGH
                if feed.status
                in {
                    FeedQualityStatus.MISSING,
                    FeedQualityStatus.CONFLICTING,
                    FeedQualityStatus.INVALID,
                }
                else AlertPriority.MEDIUM
            )
            confidence = {
                FeedQualityStatus.DELAYED: Decimal("0.60"),
                FeedQualityStatus.STALE: Decimal("0.60"),
                FeedQualityStatus.MISSING: Decimal("0.30"),
                FeedQualityStatus.CONFLICTING: Decimal("0.40"),
                FeedQualityStatus.INVALID: Decimal("0.20"),
            }[feed.status]
            alert = self.repository.create(
                alert_type=AlertType.DATA_QUALITY.value,
                priority=priority,
                provider_id=feed.provider_id,
                agent_id=feed.agent_id,
                summary=f"{feed.status.value.title()} provider feed reduces decision confidence.",
                next_step="Verify feed health and source timestamps before operational review.",
                confidence=confidence,
                source_type="provider_feed_status",
                source_id=feed.id,
                evidence=(
                    AlertEvidence(
                        "data_quality_status",
                        {
                            "status": feed.status.value,
                            "observed_at": feed.observed_at.isoformat(),
                            "ingested_at": (
                                None if feed.ingested_at is None else feed.ingested_at.isoformat()
                            ),
                        },
                    ),
                ),
            )
            self.session.flush()
            return self.repository.to_result(alert)

    def list_alerts(
        self,
        scope: AccessScope,
        *,
        provider_id: uuid.UUID | None = None,
        status: AlertStatus | None = None,
        severity: AlertPriority | None = None,
    ) -> tuple[AlertResult, ...]:
        return self.repository.list_alerts(
            scope, provider_id=provider_id, status=status, severity=severity
        )

    def get_alert(self, alert_id: uuid.UUID, scope: AccessScope) -> AlertResult:
        return self.repository.to_result(self.repository.require_alert(alert_id, scope))

    def assign(
        self,
        alert_id: uuid.UUID,
        assignee_id: uuid.UUID,
        scope: AccessScope,
    ) -> AlertResult:
        if not scope.has_any_role("ops", "manager"):
            raise AlertAuthorizationError("ops or manager role required")
        with self.session.begin():
            alert = self.repository.require_alert(alert_id, scope)
            if alert.status in {AlertStatus.RESOLVED, AlertStatus.CLOSED}:
                raise AlertConflictError("resolved or closed alert cannot be assigned")
            self.repository.require_assignee_scope(assignee_id, alert)
            self.repository.assign(alert, assignee_id=assignee_id, actor_id=scope.user_id)
            self.session.flush()
            return self.repository.to_result(alert)

    def acknowledge(
        self,
        alert_id: uuid.UUID,
        scope: AccessScope,
        note: str | None = None,
    ) -> AlertResult:
        with self.session.begin():
            alert = self.repository.require_alert(alert_id, scope)
            if alert.status == AlertStatus.ACKNOWLEDGED:
                return self.repository.to_result(alert)
            if alert.status != AlertStatus.OPEN:
                raise AlertConflictError("only an open alert can be acknowledged")
            if alert.owner_user_id != scope.user_id and not scope.has_any_role("ops", "manager"):
                raise AlertAuthorizationError("alert owner, ops, or manager role required")
            self.repository.change_status(
                alert,
                status=AlertStatus.ACKNOWLEDGED,
                actor_id=scope.user_id,
                action="alert.acknowledged",
                metadata={"note": note} if note else None,
            )
            self.session.flush()
            return self.repository.to_result(alert)


def _forecast_summary(evidence: tuple[AlertEvidence, ...]) -> dict[str, object]:
    for item in evidence:
        if item.evidence_type == "forecast_summary":
            return item.payload
    raise AlertSourceError("forecast summary evidence is missing")
