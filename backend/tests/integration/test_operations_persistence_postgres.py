import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.alerts.exceptions import AlertNotFoundError
from app.alerts.service import AlertService
from app.auth.scope import AccessScope
from app.cases.service import CaseService
from app.core.config import Settings
from app.persistence.models.agent import Agent
from app.persistence.models.alert import Alert, AlertAssignment
from app.persistence.models.analytics import (
    AnomalyFinding,
    ConfidenceAssessment,
    EvidenceItem,
    LiquidityForecast,
    RuleVersion,
)
from app.persistence.models.audit import AuditEvent
from app.persistence.models.case import Case, CaseNote, CaseStatusHistory, Escalation
from app.persistence.models.enums import AlertStatus, CaseStatus, FeedQualityStatus
from app.persistence.models.feed import ProviderFeedStatus
from app.persistence.models.provider import Provider
from app.persistence.models.user import Role, User, UserRoleAssignment
from app.scenarios.repository import ScenarioRepository
from app.scenarios.schemas import ScenarioConfig
from app.scenarios.service import ScenarioService


def database_url() -> str:
    return Settings().database_sync_url


def alembic_config() -> Config:
    backend_root = Path(__file__).resolve().parents[2]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url())
    return config


@pytest.fixture()
def migrated_connection():
    engine = create_engine(database_url())
    try:
        with engine.connect():
            pass
    except OperationalError as exc:
        engine.dispose()
        pytest.skip(f"PostgreSQL integration database unavailable: {exc}")
    command.upgrade(alembic_config(), "head")
    connection = engine.connect()
    outer_transaction = connection.begin()
    try:
        yield connection
    finally:
        if outer_transaction.is_active:
            outer_transaction.rollback()
        connection.close()
        engine.dispose()


def seed_operations(session: Session, run_ref: str):
    ScenarioService(session).run_scenario(
        "normal_day",
        16001,
        ScenarioConfig(
            profile="small",
            start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
            requested_run_ref=run_ref,
        ),
    )
    with session.begin():
        run = ScenarioRepository(session).find_run(run_ref)
        agent = session.scalar(select(Agent).where(Agent.synthetic_agent_ref == "SIM-AGENT-0001"))
        providers = session.scalars(select(Provider).order_by(Provider.code)).all()
        assert agent is not None and len(providers) >= 2 and run.ended_at is not None
        provider, other_provider = providers[:2]
        ops_role = session.scalar(select(Role).where(Role.name == "ops"))
        risk_role = session.scalar(select(Role).where(Role.name == "risk"))
        if ops_role is None:
            ops_role = Role(id=uuid.uuid4(), name="ops")
            session.add(ops_role)
        if risk_role is None:
            risk_role = Role(id=uuid.uuid4(), name="risk")
            session.add(risk_role)
        session.flush()
        operator = User(
            id=uuid.uuid4(),
            display_name="Synthetic Operations",
            synthetic_user_ref=f"SIM-USER-{run_ref[-6:]}-OPS",
        )
        reviewer = User(
            id=uuid.uuid4(),
            display_name="Synthetic Risk",
            synthetic_user_ref=f"SIM-USER-{run_ref[-6:]}-RSK",
        )
        outsider = User(
            id=uuid.uuid4(),
            display_name="Synthetic Other Provider",
            synthetic_user_ref=f"SIM-USER-{run_ref[-6:]}-OUT",
        )
        session.add_all([operator, reviewer, outsider])
        session.flush()
        session.add_all(
            [
                UserRoleAssignment(
                    user_id=operator.id,
                    role_id=ops_role.id,
                    provider_id=None,
                    area_id=None,
                ),
                UserRoleAssignment(
                    user_id=reviewer.id,
                    role_id=risk_role.id,
                    provider_id=provider.id,
                    area_id=None,
                ),
                UserRoleAssignment(
                    user_id=outsider.id,
                    role_id=ops_role.id,
                    provider_id=other_provider.id,
                    area_id=None,
                ),
            ]
        )
        forecast = LiquidityForecast(
            id=uuid.uuid4(),
            agent_id=agent.id,
            provider_id=provider.id,
            forecast_type="provider_e_money",
            forecast_time=run.ended_at,
            shortage_at=run.ended_at,
            confidence=Decimal("0.8200"),
        )
        shared_forecast = LiquidityForecast(
            id=uuid.uuid4(),
            agent_id=agent.id,
            provider_id=None,
            forecast_type="shared_cash",
            forecast_time=run.ended_at,
            shortage_at=run.ended_at,
            confidence=Decimal("0.7600"),
        )
        session.add_all([forecast, shared_forecast])
        session.flush()
        for row in (forecast, shared_forecast):
            session.add_all(
                [
                    EvidenceItem(
                        forecast_id=row.id,
                        evidence_type="forecast_summary",
                        payload={
                            "risk_level": "critical",
                            "scope": row.forecast_type,
                            "runway_minutes": "15.00",
                        },
                    ),
                    ConfidenceAssessment(
                        subject_type="liquidity_forecast",
                        subject_id=row.id,
                        confidence=row.confidence,
                        reasons={"tier": "high"},
                    ),
                ]
            )
        feed = ProviderFeedStatus(
            id=uuid.uuid4(),
            provider_id=provider.id,
            agent_id=agent.id,
            scenario_run_id=run.id,
            status=FeedQualityStatus.MISSING,
            observed_at=run.ended_at,
            ingested_at=None,
        )
        session.add(feed)
    global_scope = AccessScope(
        operator.id,
        frozenset({"ops"}),
        frozenset(),
        frozenset(),
        True,
    )
    reviewer_scope = AccessScope(
        reviewer.id,
        frozenset({"risk"}),
        frozenset({provider.id}),
        frozenset(),
    )
    outsider_scope = AccessScope(
        outsider.id,
        frozenset({"ops"}),
        frozenset({other_provider.id}),
        frozenset(),
    )
    return (
        forecast,
        shared_forecast,
        feed,
        operator,
        reviewer,
        global_scope,
        reviewer_scope,
        outsider_scope,
    )


def test_alert_creation_persists_evidence_confidence_and_audit(migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        forecast, *_rest = seed_operations(session, "SIM-RUN-980101")
        alert = AlertService(session).create_liquidity_alert(forecast.id)

        assert alert.alert_type == "liquidity_shortage"
        assert alert.provider_id == forecast.provider_id
        assert alert.confidence == Decimal("0.8200")
        assert alert.human_review_required is True
        assert any(item.evidence_type == "forecast_summary" for item in alert.evidence)
        assert [event.action for event in alert.audit_trail] == ["alert.created"]
        assert session.scalar(select(func.count()).select_from(Alert)) == 1
        assert (
            session.scalar(
                select(func.count())
                .select_from(ConfidenceAssessment)
                .where(ConfidenceAssessment.subject_type == "alert")
            )
            == 1
        )


def test_data_quality_alert_is_advisory_and_low_confidence(migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        _forecast, _shared, feed, *_rest = seed_operations(session, "SIM-RUN-980102")
        alert = AlertService(session).create_data_quality_alert(feed.id)

        assert alert.alert_type == "data_quality"
        assert alert.confidence == Decimal("0.3000")
        assert alert.status == AlertStatus.OPEN
        assert "Verify feed health" in alert.recommended_next_step


def test_anomaly_finding_creates_review_only_alert(migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        forecast, *_rest = seed_operations(session, "SIM-RUN-980107")
        with session.begin():
            rule = RuleVersion(
                id=uuid.uuid4(),
                name="operations-test-anomaly",
                version="v1",
                config={},
                active=True,
            )
            finding = AnomalyFinding(
                id=uuid.uuid4(),
                provider_id=forecast.provider_id,
                agent_id=forecast.agent_id,
                rule_version_id=rule.id,
                finding_type="near_identical_cash_out_velocity",
                severity="high",
                score=Decimal("0.8800"),
                detected_at=forecast.forecast_time,
                human_review_required=True,
            )
            session.add(rule)
            session.flush([rule])
            session.add(finding)
            session.flush([finding])
            session.add_all(
                [
                    EvidenceItem(
                        finding_id=finding.id,
                        evidence_type="repeated_amount",
                        payload={"count": 6},
                    ),
                    ConfidenceAssessment(
                        subject_type="anomaly_finding",
                        subject_id=finding.id,
                        confidence=Decimal("0.8100"),
                        reasons={"tier": "high"},
                    ),
                ]
            )

        alert = AlertService(session).create_anomaly_alert(finding.id)

        assert alert.alert_type == "anomaly_finding"
        assert alert.provider_id == finding.provider_id
        assert alert.confidence == Decimal("0.8100")
        assert "not proof of wrongdoing" in alert.recommended_next_step


def test_alert_assignment_and_acknowledgement_are_audited(migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        forecast, _shared, _feed, _operator, reviewer, global_scope, *_ = seed_operations(
            session, "SIM-RUN-980103"
        )
        alert = AlertService(session).create_liquidity_alert(forecast.id)
        assigned = AlertService(session).assign(alert.alert_id, reviewer.id, global_scope)
        acknowledged = AlertService(session).acknowledge(
            alert.alert_id, global_scope, "Synthetic acknowledgement"
        )

        assert assigned.owner_user_id == reviewer.id
        assert acknowledged.status == AlertStatus.ACKNOWLEDGED
        assert [event.action for event in acknowledged.audit_trail] == [
            "alert.created",
            "alert.assigned",
            "alert.acknowledged",
        ]
        assert session.scalar(select(func.count()).select_from(AlertAssignment)) == 1


def test_case_escalation_resolution_close_and_audit_lifecycle(migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        (
            forecast,
            _shared,
            _feed,
            _operator,
            reviewer,
            global_scope,
            reviewer_scope,
            _outsider_scope,
        ) = seed_operations(session, "SIM-RUN-980104")
        alert = AlertService(session).create_liquidity_alert(forecast.id)
        AlertService(session).assign(alert.alert_id, reviewer.id, global_scope)
        AlertService(session).acknowledge(alert.alert_id, global_scope)
        case = CaseService(session).create_from_alert(
            alert.alert_id,
            global_scope,
            initial_note="Initial human review.",
        )
        escalated = CaseService(session).escalate(
            case.case_id,
            global_scope,
            to_role="risk",
            reason="Specialist review required.",
            expected_version=case.version,
        )
        resolved = CaseService(session).resolve(
            case.case_id,
            reviewer_scope,
            rationale="Legitimate synthetic activity confirmed.",
            expected_version=escalated.version,
        )
        closed = CaseService(session).close(
            case.case_id,
            global_scope,
            reason="Resolution accepted.",
            expected_version=resolved.version,
        )

        assert closed.status == CaseStatus.CLOSED
        assert closed.resolution_information == "Legitimate synthetic activity confirmed."
        assert [item.to_status for item in closed.status_history] == [
            CaseStatus.ACKNOWLEDGED,
            CaseStatus.ESCALATED,
            CaseStatus.RESOLVED,
            CaseStatus.CLOSED,
        ]
        assert len(closed.escalation_history) == 1
        assert session.scalar(select(func.count()).select_from(Case)) == 1
        assert session.scalar(select(func.count()).select_from(CaseNote)) == 2
        assert session.scalar(select(func.count()).select_from(CaseStatusHistory)) == 4
        assert session.scalar(select(func.count()).select_from(Escalation)) == 1
        assert session.get(Alert, alert.alert_id).status == AlertStatus.CLOSED


def test_provider_scope_hides_other_provider_and_shared_cash(migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        (
            forecast,
            shared,
            _feed,
            _operator,
            _reviewer,
            global_scope,
            _reviewer_scope,
            outsider_scope,
        ) = seed_operations(session, "SIM-RUN-980105")
        provider_alert = AlertService(session).create_liquidity_alert(forecast.id)
        shared_alert = AlertService(session).create_liquidity_alert(shared.id)

        assert len(AlertService(session).list_alerts(global_scope)) == 2
        assert AlertService(session).list_alerts(outsider_scope) == ()
        with pytest.raises(AlertNotFoundError):
            AlertService(session).get_alert(provider_alert.alert_id, outsider_scope)
        with pytest.raises(AlertNotFoundError):
            AlertService(session).get_alert(shared_alert.alert_id, outsider_scope)


def test_alert_creation_rolls_back_on_persistence_failure(monkeypatch, migrated_connection) -> None:
    with Session(migrated_connection, expire_on_commit=False) as session:
        forecast, *_rest = seed_operations(session, "SIM-RUN-980106")
        service = AlertService(session)
        original = service.repository.create

        def fail_after_create(**kwargs):
            original(**kwargs)
            raise RuntimeError("forced operations persistence failure")

        monkeypatch.setattr(service.repository, "create", fail_after_create)
        with pytest.raises(RuntimeError, match="forced operations persistence failure"):
            service.create_liquidity_alert(forecast.id)

        assert session.scalar(select(func.count()).select_from(Alert)) == 0
        assert (
            session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.entity_type == "alert")
            )
            == 0
        )
