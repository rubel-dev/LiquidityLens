import time
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.core.config import Settings
from app.liquidity.schemas import ForecastScope, RiskLevel
from app.liquidity.service import LiquidityForecastingService
from app.persistence.models.agent import Agent
from app.persistence.models.analytics import (
    ConfidenceAssessment,
    EvidenceItem,
    LiquidityForecast,
    RuleVersion,
)
from app.persistence.models.audit import AuditEvent
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
def migrated_engine():
    probe = postgres_engine()
    probe.dispose()
    config = alembic_config()
    command.upgrade(config, "head")
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


def run_scenario(session: Session, code: str, run_ref: str):
    ScenarioService(session).run_scenario(
        code,
        5001,
        ScenarioConfig(
            profile="small",
            start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
            requested_run_ref=run_ref,
        ),
    )
    run = ScenarioRepository(session).find_run(run_ref)
    agent = session.scalar(select(Agent).where(Agent.synthetic_agent_ref == "SIM-AGENT-0001"))
    assert agent is not None
    return agent, run


def test_persists_provider_and_shared_cash_forecasts_with_evidence(migrated_engine) -> None:
    with Session(migrated_engine) as session:
        agent, run = run_scenario(
            session,
            "hidden_provider_shortage",
            "SIM-RUN-980001",
        )

    with Session(migrated_engine) as session:
        results = LiquidityForecastingService(session).forecast_agent(
            agent.id,
            scenario_run_id=run.id,
        )

        assert len(results) == 4
        assert sum(item.scope == ForecastScope.PROVIDER_E_MONEY for item in results) == 3
        assert sum(item.scope == ForecastScope.SHARED_CASH for item in results) == 1
        assert session.scalar(select(func.count()).select_from(LiquidityForecast)) == 4
        assert session.scalar(select(func.count()).select_from(ConfidenceAssessment)) == 4
        assert session.scalar(select(func.count()).select_from(EvidenceItem)) == 32
        assert session.scalar(select(func.count()).select_from(RuleVersion)) == 1
        assert (
            session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.action == "liquidity.forecast_created")
            )
            == 4
        )
        provider_ids = [item.provider_id for item in results if item.provider_id is not None]
        assert len(set(provider_ids)) == 3


def test_shared_cash_crisis_forecasts_shared_cash_without_provider_scope(migrated_engine) -> None:
    with Session(migrated_engine) as session:
        agent, run = run_scenario(session, "shared_cash_crisis", "SIM-RUN-980002")

    with Session(migrated_engine) as session:
        results = LiquidityForecastingService(session).forecast_agent(
            agent.id,
            scenario_run_id=run.id,
        )
        shared = next(item for item in results if item.scope == ForecastScope.SHARED_CASH)

        assert shared.provider_id is None
        assert shared.risk_level == RiskLevel.CRITICAL
        persisted = session.get(LiquidityForecast, shared.forecast_id)
        assert persisted is not None
        assert persisted.provider_id is None
        audit = session.scalar(
            select(AuditEvent).where(
                AuditEvent.action == "liquidity.forecast_created",
                AuditEvent.entity_id == shared.forecast_id,
            )
        )
        assert audit is not None
        assert audit.provider_id is None


def test_missing_feed_and_balance_persist_unknown_forecast(migrated_engine) -> None:
    with Session(migrated_engine) as session:
        agent, run = run_scenario(session, "missing_feed", "SIM-RUN-980003")

    with Session(migrated_engine) as session:
        results = LiquidityForecastingService(session).forecast_agent(
            agent.id,
            scenario_run_id=run.id,
        )
        missing = next(
            item
            for item in results
            if item.scope == ForecastScope.PROVIDER_E_MONEY and item.current_balance is None
        )

        assert missing.risk_level == RiskLevel.UNKNOWN
        assert missing.runway_minutes is None
        assert missing.estimated_shortage_at is None
        assert "missing" in missing.data_quality_impact


def test_eid_scenario_records_legitimate_event_context(migrated_engine) -> None:
    with Session(migrated_engine) as session:
        agent, run = run_scenario(session, "eid_rush", "SIM-RUN-980004")

    with Session(migrated_engine) as session:
        results = LiquidityForecastingService(session).forecast_agent(
            agent.id,
            scenario_run_id=run.id,
        )

        assert all(any(item.value == "eid" for item in result.evidence) for result in results)
        assert all("fraud" not in str(result).lower() for result in results)


def test_forecast_transaction_rolls_back_on_persistence_failure(
    monkeypatch, migrated_engine
) -> None:
    with Session(migrated_engine) as session:
        agent, run = run_scenario(session, "normal_day", "SIM-RUN-980005")

    with Session(migrated_engine) as session:
        service = LiquidityForecastingService(session)
        original = service.repository.persist
        calls = 0

        def fail_second(result, config):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("forced forecast persistence failure")
            return original(result, config)

        monkeypatch.setattr(service.repository, "persist", fail_second)
        with pytest.raises(RuntimeError, match="forced forecast persistence failure"):
            service.forecast_agent(agent.id, scenario_run_id=run.id)

        assert session.scalar(select(func.count()).select_from(LiquidityForecast)) == 0
        assert session.scalar(select(func.count()).select_from(EvidenceItem)) == 0


def test_demo_forecast_processing_latency_is_measured(migrated_engine) -> None:
    durations: list[float] = []
    with Session(migrated_engine) as session:
        agent, run = run_scenario(session, "normal_day", "SIM-RUN-980006")

    for _ in range(5):
        with Session(migrated_engine) as session:
            start = time.perf_counter()
            LiquidityForecastingService(session).forecast_agent(
                agent.id,
                scenario_run_id=run.id,
            )
            durations.append((time.perf_counter() - start) * 1000)

    ordered = sorted(durations)
    p95_index = min(len(ordered) - 1, int(len(ordered) * 0.95))
    average_ms = sum(durations) / len(durations)
    p95_ms = ordered[p95_index]
    assert average_ms > 0
    assert p95_ms < 30000
