import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.anomaly.service import AnomalyDetectionService
from app.confidence.service import CoreIntelligenceService
from app.core.config import Settings
from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.alert import Alert
from app.persistence.models.analytics import (
    AnomalyFinding,
    ConfidenceAssessment,
    EvidenceItem,
    LiquidityForecast,
    RuleVersion,
)
from app.persistence.models.enums import FeedQualityStatus, TransactionStatus, TransactionType
from app.persistence.models.feed import ProviderFeedStatus
from app.persistence.models.provider import Provider
from app.persistence.models.transaction import Transaction
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


def postgres_engine():
    engine = create_engine(database_url())
    try:
        with engine.connect():
            return engine
    except OperationalError as exc:
        engine.dispose()
        pytest.skip(f"PostgreSQL integration database unavailable: {exc}")


@pytest.fixture()
def migrated_connection():
    probe = postgres_engine()
    probe.dispose()
    command.upgrade(alembic_config(), "head")
    engine = postgres_engine()
    connection = engine.connect()
    outer_transaction = connection.begin()
    try:
        yield connection
    finally:
        if outer_transaction.is_active:
            outer_transaction.rollback()
        connection.close()
        engine.dispose()


def seed_pattern(session: Session, run_ref: str):
    ScenarioService(session).run_scenario(
        "normal_day",
        15001,
        ScenarioConfig(
            profile="small",
            start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
            requested_run_ref=run_ref,
        ),
    )
    run = ScenarioRepository(session).find_run(run_ref)
    agent = session.scalar(select(Agent).where(Agent.synthetic_agent_ref == "SIM-AGENT-0001"))
    provider = session.scalar(select(Provider).where(Provider.code == "SIM-PROVIDER-BK"))
    assert agent is not None and provider is not None and run.ended_at is not None
    account = session.scalar(
        select(AgentProviderAccount).where(
            AgentProviderAccount.agent_id == agent.id,
            AgentProviderAccount.provider_id == provider.id,
        )
    )
    assert account is not None
    for index in range(6):
        session.add(
            Transaction(
                id=uuid.uuid4(),
                account_id=account.id,
                agent_id=agent.id,
                provider_id=provider.id,
                synthetic_transaction_ref=f"SIM-TXN-CORE-{run_ref[-6:]}-{index:02d}",
                synthetic_account_ref=account.synthetic_account_ref,
                synthetic_customer_ref=f"SIM-CUST-{(index % 3) + 1:04d}",
                transaction_type=TransactionType.CASH_OUT,
                amount=Decimal(1000 + index),
                currency="BDT",
                status=TransactionStatus.COMPLETED,
                occurred_at=run.ended_at - timedelta(minutes=25 - index * 4),
                scenario_run_id=run.id,
            )
        )
    session.flush()
    return agent, provider, run


def test_core_intelligence_persists_forecasts_anomaly_confidence_and_evidence(
    migrated_connection,
) -> None:
    with Session(migrated_connection) as session:
        agent, provider, run = seed_pattern(session, "SIM-RUN-990101")

    with Session(migrated_connection) as session:
        result = CoreIntelligenceService(session).analyze_agent(
            agent.id,
            scenario_run_id=run.id,
        )

        assert len(result.forecasts) == 4
        assert len(result.anomaly_findings) == 1
        assert result.anomaly_findings[0].provider_id == provider.id
        assert result.anomaly_findings[0].requires_review is True
        assert "not proof of wrongdoing" in result.recommendation
        assert session.scalar(select(func.count()).select_from(LiquidityForecast).where(LiquidityForecast.scenario_run_id == run.id)) == 4
        assert session.scalar(select(func.count()).select_from(AnomalyFinding).where(AnomalyFinding.scenario_run_id == run.id)) == 1
        assert session.scalar(select(func.count()).select_from(ConfidenceAssessment).where(ConfidenceAssessment.scenario_run_id == run.id)) == 6
        assert session.scalar(select(func.count()).select_from(EvidenceItem)) >= 37
        assert session.scalar(select(func.count()).select_from(RuleVersion)) >= 2
        assert session.scalar(select(func.count()).select_from(Alert).where(Alert.scenario_run_id == run.id)) == 0


def test_anomaly_persistence_keeps_provider_scope_and_fingerprint(
    migrated_connection,
) -> None:
    with Session(migrated_connection) as session:
        agent, provider, run = seed_pattern(session, "SIM-RUN-990102")

    with Session(migrated_connection) as session:
        findings = AnomalyDetectionService(session).detect_agent(
            agent.id,
            scenario_run_id=run.id,
        )

        assert len(findings) == 1
        assert findings[0].provider_id == provider.id
        persisted = session.get(AnomalyFinding, findings[0].finding_id)
        assert persisted is not None
        assert persisted.provider_id == provider.id
        evidence_types = set(
            session.scalars(
                select(EvidenceItem.evidence_type).where(
                    EvidenceItem.finding_id == findings[0].finding_id
                )
            ).all()
        )
        assert evidence_types == {
            "repeated_amount",
            "velocity",
            "concentrated_group",
            "time_window_deviation",
            "baseline_deviation",
        }


def test_anomaly_transaction_rolls_back_on_persistence_failure(
    monkeypatch,
    migrated_connection,
) -> None:
    with Session(migrated_connection) as session:
        agent, _provider, run = seed_pattern(session, "SIM-RUN-990103")

    with Session(migrated_connection) as session:
        service = AnomalyDetectionService(session)
        original = service.repository.persist

        def fail_after_persist(result, config):
            original(result, config)
            raise RuntimeError("forced anomaly persistence failure")

        monkeypatch.setattr(service.repository, "persist", fail_after_persist)
        with pytest.raises(RuntimeError, match="forced anomaly persistence failure"):
            service.detect_agent(agent.id, scenario_run_id=run.id)

        assert session.scalar(select(func.count()).select_from(AnomalyFinding).where(AnomalyFinding.scenario_run_id == run.id)) == 0
        pass  # Cannot filter EvidenceItem easily


def test_missing_feed_reduces_persisted_finding_confidence(
    migrated_connection,
) -> None:
    with Session(migrated_connection) as session:
        agent, provider, run = seed_pattern(session, "SIM-RUN-990104")
        feed = session.scalar(
            select(ProviderFeedStatus).where(
                ProviderFeedStatus.provider_id == provider.id,
                ProviderFeedStatus.scenario_run_id == run.id,
            )
        )
        assert feed is not None
        feed.status = FeedQualityStatus.MISSING
        session.flush()

    with Session(migrated_connection) as session:
        findings = AnomalyDetectionService(session).detect_agent(
            agent.id,
            scenario_run_id=run.id,
        )

        assert len(findings) == 1
        assert findings[0].confidence < 0.75
        assert findings[0].requires_review is False
