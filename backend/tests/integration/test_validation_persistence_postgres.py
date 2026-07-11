import os
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.persistence.models.audit import AuditEvent
from app.persistence.models.balance import ProviderBalanceSnapshot, SharedCashSnapshot
from app.persistence.models.feed import DataQualityEvent, ProviderFeedStatus
from app.persistence.models.transaction import Transaction
from app.scenarios.repository import ScenarioRepository
from app.scenarios.schemas import ScenarioConfig
from app.scenarios.service import ScenarioService
from app.validation.enums import RecordDisposition
from app.validation.schemas import (
    CanonicalFeedStatusInput,
    CanonicalProviderBalanceInput,
    CanonicalSharedCashInput,
    CanonicalTransactionInput,
)
from app.validation.service import ValidationService


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


def seed_reference(session: Session) -> None:
    ScenarioRepository(session).ensure_reference_data()
    session.commit()


def tx(
    ref: str = "SIM-TXN-910001-000001",
    amount: Decimal = Decimal("100.00"),
    provider_code: str = "BK",
    account_ref: str = "SIM-ACCT-BK-0001",
    sequence: int | None = None,
):
    ts = datetime(2026, 7, 11, 9, 0, tzinfo=UTC)
    return CanonicalTransactionInput(
        provider_code=provider_code,
        agent_ref="SIM-AGENT-0001",
        account_ref=account_ref,
        synthetic_transaction_ref=ref,
        synthetic_account_ref=account_ref,
        synthetic_customer_ref="SIM-CUST-0001",
        transaction_type="cash_out",
        amount=amount,
        currency="BDT",
        event_timestamp=ts,
        received_timestamp=ts + timedelta(seconds=1),
        source_sequence=sequence,
    )


def provider_balance(
    amount: Decimal | None = Decimal("1000.00"),
    ts: datetime = datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
):
    return CanonicalProviderBalanceInput(
        provider_code="BK",
        agent_ref="SIM-AGENT-0001",
        account_ref="SIM-ACCT-BK-0001",
        reported_balance=amount,
        balance_timestamp=ts,
        received_timestamp=ts + timedelta(seconds=1),
    )


def test_valid_transaction_persists_once_and_duplicate_retry_is_idempotent(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)
        first = service.ingest_transaction(tx())
        second = service.ingest_transaction(tx())

        assert first.disposition == RecordDisposition.ACCEPTED
        assert second.disposition == RecordDisposition.DUPLICATE_IGNORED
        assert session.scalar(select(func.count()).select_from(Transaction)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent)) == 2


def test_rejected_transaction_does_not_create_trusted_row_and_persists_evidence(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        result = ValidationService(session).ingest_transaction(tx(amount=Decimal("0.00")))

        assert result.disposition == RecordDisposition.REJECTED
        assert session.scalar(select(func.count()).select_from(Transaction)) == 0
        assert session.scalar(select(func.count()).select_from(DataQualityEvent)) >= 1
        assert session.scalar(select(func.count()).select_from(AuditEvent)) >= 1


def test_warning_transaction_persists_with_quality_event(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)
        service.ingest_transaction(tx(ref="SIM-TXN-910001-000010"))
        older = tx(ref="SIM-TXN-910001-000011")
        older = older.__class__(
            **{
                **older.__dict__,
                "event_timestamp": older.event_timestamp - timedelta(hours=1),
            }
        )
        result = service.ingest_transaction(older)

        assert result.disposition == RecordDisposition.ACCEPTED_WITH_WARNING
        assert session.scalar(select(func.count()).select_from(Transaction)) == 2
        assert session.scalar(select(func.count()).select_from(DataQualityEvent)) >= 1


def test_provider_balance_null_remains_unknown_and_negative_rejected(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)
        null_result = service.ingest_provider_balance(provider_balance(amount=None))
        negative_result = service.ingest_provider_balance(
            provider_balance(amount=Decimal("-1.00"), ts=datetime(2026, 7, 11, 9, 1, tzinfo=UTC))
        )

        assert null_result.disposition == RecordDisposition.ACCEPTED
        assert negative_result.disposition == RecordDisposition.REJECTED
        assert session.scalar(select(func.count()).select_from(ProviderBalanceSnapshot)) == 1
        assert session.scalar(select(ProviderBalanceSnapshot.amount)) is None


def test_conflicting_balance_is_quarantined_and_inspectable(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)
        service.ingest_provider_balance(provider_balance(amount=Decimal("1000.00")))
        result = service.ingest_provider_balance(provider_balance(amount=Decimal("900.00")))

        assert result.disposition == RecordDisposition.QUARANTINED
        assert session.scalar(select(func.count()).select_from(ProviderBalanceSnapshot)) == 1
        assert session.scalar(select(func.count()).select_from(DataQualityEvent)) >= 1


def test_shared_cash_has_no_provider_scope(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        ts = datetime(2026, 7, 11, 9, 0, tzinfo=UTC)
        result = ValidationService(session).ingest_shared_cash(
            CanonicalSharedCashInput(
                agent_ref="SIM-AGENT-0001",
                reported_cash=Decimal("5000.00"),
                snapshot_timestamp=ts,
                received_timestamp=ts + timedelta(seconds=1),
                source="SIM-CASH-SNAPSHOT-0001",
            )
        )
        assert result.disposition == RecordDisposition.ACCEPTED
        assert session.scalar(select(func.count()).select_from(SharedCashSnapshot)) == 1
        assert (
            session.scalar(
                select(AuditEvent.provider_id).where(AuditEvent.entity_type == "shared_cash")
            )
            is None
        )


def test_feed_quality_updates_status_events_and_audit(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        expected = datetime(2026, 7, 11, 9, 0, tzinfo=UTC)
        result = ValidationService(session).evaluate_feed_quality(
            CanonicalFeedStatusInput(
                provider_code="BK",
                agent_ref="SIM-AGENT-0001",
                expected_timestamp=expected,
                received_timestamp=expected + timedelta(minutes=10),
                last_successful_timestamp=expected,
                source_status="complete",
            )
        )
        assert result.disposition == RecordDisposition.ACCEPTED_WITH_WARNING
        assert session.scalar(select(func.count()).select_from(ProviderFeedStatus)) == 1
        assert session.scalar(select(func.count()).select_from(DataQualityEvent)) == 1
        assert session.scalar(select(func.count()).select_from(AuditEvent)) >= 1


def test_missing_feed_persists_missing_quality_event(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        expected = datetime(2026, 7, 11, 9, 0, tzinfo=UTC)
        result = ValidationService(session).evaluate_feed_quality(
            CanonicalFeedStatusInput(
                provider_code="BK",
                agent_ref="SIM-AGENT-0001",
                expected_timestamp=expected,
                received_timestamp=None,
                last_successful_timestamp=None,
                source_status="missing",
            )
        )

        assert result.disposition == RecordDisposition.QUARANTINED
        assert session.scalar(select(DataQualityEvent.event_type)) == "missing_feed"


def test_provider_separation_rejects_account_scope_mismatch(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        result = ValidationService(session).ingest_transaction(
            tx(
                ref="SIM-TXN-910001-000050",
                provider_code="NG",
                account_ref="SIM-ACCT-BK-0001",
            )
        )

        assert result.disposition == RecordDisposition.REJECTED
        assert session.scalar(select(func.count()).select_from(Transaction)) == 0


def test_failed_ingestion_rolls_back_transaction(monkeypatch, migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)

        def fail_audit(**_kwargs):
            raise RuntimeError("forced audit failure")

        monkeypatch.setattr(service.repository, "persist_audit", fail_audit)

        with pytest.raises(RuntimeError, match="forced audit failure"):
            service.ingest_transaction(tx(ref="SIM-TXN-910001-000060"))

        assert session.scalar(select(func.count()).select_from(Transaction)) == 0


def test_sequence_gap_persists_warning_evidence(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)
        first = service.ingest_transaction(tx(ref="SIM-TXN-910001-000070", sequence=1))
        gap = service.ingest_transaction(tx(ref="SIM-TXN-910001-000071", sequence=3))

        assert first.disposition == RecordDisposition.ACCEPTED
        assert gap.disposition == RecordDisposition.ACCEPTED_WITH_WARNING
        assert session.scalar(select(DataQualityEvent.event_type)) == "sequence_gap"


def test_scenario_records_validate_without_using_ground_truth(migrated_engine):
    with Session(migrated_engine) as session:
        ScenarioService(session).run_scenario(
            "liquidity_pressure_unusual_activity",
            5001,
            ScenarioConfig(
                profile="small",
                start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
                requested_run_ref="SIM-RUN-970001",
            ),
        )
        existing = session.scalar(select(Transaction).limit(1))
        assert existing is not None
        existing_type = existing.transaction_type
        existing_amount = existing.amount
        existing_currency = existing.currency
        existing_time = existing.occurred_at
        session.commit()

    with Session(migrated_engine) as session:
        canonical = CanonicalTransactionInput(
            provider_code="SIM-PROVIDER-BK",
            agent_ref="SIM-AGENT-0001",
            account_ref="SIM-ACCT-BK-0001",
            synthetic_transaction_ref="SIM-TXN-970001-999999",
            synthetic_account_ref="SIM-ACCT-BK-0001",
            synthetic_customer_ref="SIM-CUST-0002",
            transaction_type=existing_type,
            amount=existing_amount,
            currency=existing_currency,
            event_timestamp=existing_time,
            received_timestamp=existing_time + timedelta(seconds=1),
            scenario_run_ref="SIM-RUN-970001",
        )
        result = ValidationService(session).ingest_transaction(canonical)
        assert result.disposition in {
            RecordDisposition.ACCEPTED,
            RecordDisposition.ACCEPTED_WITH_WARNING,
        }


def test_demo_sized_validation_latency_is_reasonable(migrated_engine):
    with Session(migrated_engine) as session:
        seed_reference(session)
        service = ValidationService(session)
        start = time.perf_counter()
        for index in range(40):
            service.ingest_transaction(tx(ref=f"SIM-TXN-920001-{index + 1:06d}"))
        elapsed = time.perf_counter() - start

        assert elapsed < 5.0
        assert session.scalar(select(func.count()).select_from(Transaction)) == 40
