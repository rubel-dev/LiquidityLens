import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.persistence.models.agent import Agent, AgentProviderAccount
from app.persistence.models.area import Area
from app.persistence.models.balance import ProviderBalanceSnapshot, SharedCashSnapshot
from app.persistence.models.enums import AccountStatus, AgentStatus, TransactionStatus, TransactionType
from app.persistence.models.provider import Provider
from app.persistence.models.transaction import Transaction


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


def test_migrate_downgrade_and_reupgrade_against_postgres():
    probe = postgres_engine()
    probe.dispose()
    config = alembic_config()
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    engine = postgres_engine()
    inspector = inspect(engine)
    assert "providers" in inspector.get_table_names()
    assert "transactions" in inspector.get_table_names()
    command.downgrade(config, "base")
    assert "providers" not in inspect(engine).get_table_names()
    command.upgrade(config, "head")
    assert "providers" in inspect(engine).get_table_names()
    engine.dispose()


def seed_scope(session: Session):
    area = Area(code="SIM-AREA-001", display_name="Demo Area")
    agent = Agent(
        area=area,
        synthetic_agent_ref="SIM-AGENT-0001",
        display_code="Demo Outlet",
        status=AgentStatus.ACTIVE,
    )
    provider_a = Provider(code="SIM-PROVIDER-A", display_name="Sim Provider A", boundary_note="separate")
    provider_b = Provider(code="SIM-PROVIDER-B", display_name="Sim Provider B", boundary_note="separate")
    account_a = AgentProviderAccount(
        agent=agent,
        provider=provider_a,
        synthetic_account_ref="SIM-ACCT-A-0001",
        status=AccountStatus.ACTIVE,
    )
    account_b = AgentProviderAccount(
        agent=agent,
        provider=provider_b,
        synthetic_account_ref="SIM-ACCT-B-0001",
        status=AccountStatus.ACTIVE,
    )
    session.add_all([area, agent, provider_a, provider_b, account_a, account_b])
    session.commit()
    return agent, provider_a, provider_b, account_a, account_b


def test_domain_constraints_and_provider_separation(migrated_engine):
    with Session(migrated_engine) as session:
        agent, provider_a, provider_b, account_a, account_b = seed_scope(session)
        observed_at = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)

        session.add(SharedCashSnapshot(agent_id=agent.id, amount=None, observed_at=observed_at))
        session.add(
            ProviderBalanceSnapshot(
                account_id=account_a.id,
                agent_id=agent.id,
                provider_id=provider_a.id,
                amount=Decimal("1000.00"),
                observed_at=observed_at,
                quality_status="complete",
            )
        )
        session.add(
            ProviderBalanceSnapshot(
                account_id=account_b.id,
                agent_id=agent.id,
                provider_id=provider_b.id,
                amount=Decimal("500.00"),
                observed_at=observed_at,
                quality_status="complete",
            )
        )
        session.add(
            Transaction(
                account_id=account_a.id,
                agent_id=agent.id,
                provider_id=provider_a.id,
                synthetic_transaction_ref="SIM-TXN-000001",
                synthetic_account_ref="SIM-ACCT-A-0001",
                synthetic_customer_ref="SIM-CUST-0001",
                transaction_type=TransactionType.CASH_OUT,
                amount=Decimal("120.00"),
                status=TransactionStatus.COMPLETED,
                occurred_at=observed_at,
            )
        )
        session.commit()

        assert session.query(SharedCashSnapshot).one().amount is None

        session.add(
            Transaction(
                account_id=account_a.id,
                agent_id=agent.id,
                provider_id=provider_a.id,
                synthetic_transaction_ref="SIM-TXN-000001",
                synthetic_account_ref="SIM-ACCT-A-0001",
                synthetic_customer_ref="SIM-CUST-0002",
                transaction_type=TransactionType.CASH_OUT,
                amount=Decimal("1.00"),
                status=TransactionStatus.COMPLETED,
                occurred_at=observed_at,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        session.add(
            AgentProviderAccount(
                agent_id=agent.id,
                provider_id=provider_a.id,
                synthetic_account_ref="SIM-ACCT-A-DUP",
                status=AccountStatus.ACTIVE,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        session.add(
            ProviderBalanceSnapshot(
                account_id=account_a.id,
                agent_id=agent.id,
                provider_id=provider_a.id,
                amount=Decimal("-1.00"),
                observed_at=observed_at,
                quality_status="complete",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        session.add(
            Transaction(
                account_id=account_a.id,
                agent_id=agent.id,
                provider_id=provider_a.id,
                synthetic_transaction_ref="SIM-TXN-000002",
                synthetic_account_ref="SIM-ACCT-A-0001",
                synthetic_customer_ref="SIM-CUST-0003",
                transaction_type=TransactionType.CASH_OUT,
                amount=Decimal("0.00"),
                status=TransactionStatus.COMPLETED,
                occurred_at=observed_at,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

        session.add(
            ProviderBalanceSnapshot(
                account_id=account_a.id,
                agent_id=agent.id,
                provider_id=provider_b.id,
                amount=Decimal("5.00"),
                observed_at=observed_at,
                quality_status="complete",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
