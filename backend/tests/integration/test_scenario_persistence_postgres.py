import os
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.persistence.models.audit import AuditEvent
from app.persistence.models.balance import ProviderBalanceSnapshot
from app.persistence.models.enums import ScenarioRunStatus
from app.persistence.models.feed import ProviderFeedStatus
from app.persistence.models.scenario import ScenarioRun
from app.persistence.models.transaction import Transaction
from app.scenarios.exceptions import DuplicateScenarioRunError
from app.scenarios.repository import ScenarioRepository
from app.scenarios.schemas import ScenarioConfig
from app.scenarios.service import ScenarioService


def database_url() -> str:
    return os.getenv(
        "DATABASE_SYNC_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/liquiditylens_demo",
    )


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
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = postgres_engine()
    try:
        yield engine
    finally:
        engine.dispose()
        command.downgrade(config, "base")


def scenario_config(run_ref: str) -> ScenarioConfig:
    return ScenarioConfig(
        profile="small",
        start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
        requested_run_ref=run_ref,
    )


def test_scenario_run_commits_reference_data_records_and_ground_truth(migrated_engine):
    with Session(migrated_engine) as session:
        result = ScenarioService(session).run_scenario(
            "liquidity_pressure_unusual_activity",
            5001,
            scenario_config("SIM-RUN-900001"),
        )

        assert result.status == ScenarioRunStatus.COMPLETED.value
        assert result.generated_counts["transactions"] == 18
        assert session.scalar(select(func.count()).select_from(Transaction)) == 18
        assert session.scalar(select(func.count()).select_from(ProviderBalanceSnapshot)) == 6
        assert session.scalar(select(func.count()).select_from(ProviderFeedStatus)) == 3
        assert (
            session.scalar(
                select(func.count())
                .select_from(AuditEvent)
                .where(AuditEvent.action == "scenario.ground_truth_event")
            )
            == 4
        )


def test_replay_reproduces_same_fingerprint(migrated_engine):
    with Session(migrated_engine) as session:
        first = ScenarioService(session).run_scenario(
            "normal_day",
            1001,
            scenario_config("SIM-RUN-900002"),
        )

    with Session(migrated_engine) as session:
        replay = ScenarioService(session).replay("SIM-RUN-900002")

    assert replay.fingerprint == first.fingerprint


def test_reset_affects_only_selected_run(migrated_engine):
    with Session(migrated_engine) as session:
        service = ScenarioService(session)
        service.run_scenario("normal_day", 1001, scenario_config("SIM-RUN-900003"))
        service.run_scenario("eid_rush", 2001, scenario_config("SIM-RUN-900004"))

    with Session(migrated_engine) as session:
        ScenarioService(session).reset("SIM-RUN-900003")

    with Session(migrated_engine) as session:
        run_one = ScenarioRepository(session).find_run("SIM-RUN-900003")
        run_two = ScenarioRepository(session).find_run("SIM-RUN-900004")
        run_one_transactions = (
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.scenario_run_id == run_one.id)
        )
        run_two_transactions = (
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.scenario_run_id == run_two.id)
        )
        assert session.scalar(run_one_transactions) == 0
        assert session.scalar(run_two_transactions) == 18


def test_duplicate_requested_run_ref_is_rejected(migrated_engine):
    with Session(migrated_engine) as session:
        service = ScenarioService(session)
        service.run_scenario("normal_day", 1001, scenario_config("SIM-RUN-900005"))
        with pytest.raises(DuplicateScenarioRunError):
            service.run_scenario("normal_day", 1001, scenario_config("SIM-RUN-900005"))


def test_missing_balance_persists_as_null_not_zero(migrated_engine):
    with Session(migrated_engine) as session:
        ScenarioService(session).run_scenario(
            "missing_feed",
            8001,
            scenario_config("SIM-RUN-900006"),
        )
        assert (
            session.scalar(
                select(func.count())
                .select_from(ProviderBalanceSnapshot)
                .where(ProviderBalanceSnapshot.amount.is_(None))
            )
            == 1
        )


def test_duplicate_transaction_ref_is_rejected_by_database(migrated_engine):
    with Session(migrated_engine) as session:
        ScenarioService(session).run_scenario("normal_day", 1001, scenario_config("SIM-RUN-900007"))
        original = session.scalar(select(Transaction).limit(1))
        assert original is not None
        session.add(
            Transaction(
                account_id=original.account_id,
                agent_id=original.agent_id,
                provider_id=original.provider_id,
                synthetic_transaction_ref=original.synthetic_transaction_ref,
                synthetic_account_ref=original.synthetic_account_ref,
                synthetic_customer_ref="SIM-CUST-9999",
                transaction_type=original.transaction_type,
                amount=original.amount,
                currency=original.currency,
                status=original.status,
                occurred_at=original.occurred_at,
                scenario_run_id=original.scenario_run_id,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()


def test_failed_generation_rolls_back_active_run(monkeypatch, migrated_engine):
    def fail_persist(*args, **kwargs):
        raise RuntimeError("forced persistence failure")

    monkeypatch.setattr(ScenarioRepository, "persist_generated_records", fail_persist)
    with Session(migrated_engine) as session:
        with pytest.raises(RuntimeError, match="forced persistence failure"):
            ScenarioService(session).run_scenario(
                "normal_day",
                1001,
                scenario_config("SIM-RUN-900008"),
            )
        assert session.scalar(select(func.count()).select_from(ScenarioRun)) == 0


def test_demo_profile_generation_performance_is_reasonable(migrated_engine):
    start = time.perf_counter()
    with Session(migrated_engine) as session:
        result = ScenarioService(session).run_scenario(
            "shared_cash_crisis",
            4001,
            ScenarioConfig(
                profile="demo",
                start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
                requested_run_ref="SIM-RUN-900009",
            ),
        )
    elapsed = time.perf_counter() - start

    assert result.generated_counts["transactions"] == 90
    assert elapsed < 5.0
