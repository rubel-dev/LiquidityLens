from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.providers.exceptions import ProviderAdapterError
from app.providers.schemas import SimulatedProviderRecord
from app.providers.simulated import SimulatedProviderAdapter
from app.validation.schemas import (
    CanonicalProviderBalanceInput,
    CanonicalTransactionInput,
)


def test_simulated_adapter_maps_transaction_without_cross_provider_access():
    adapter = SimulatedProviderAdapter("BK")
    record = SimulatedProviderRecord(
        provider_code="BK",
        agent_ref="SIM-AGENT-0001",
        account_ref="SIM-ACCT-BK-0001",
        record_type="transaction",
        record_ref="SIM-TXN-900001-000001",
        amount=Decimal("100.00"),
        event_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC),
        transaction_type="cash_out",
        synthetic_customer_ref="SIM-CUST-0001",
    )

    canonical = adapter.map_record(record)

    assert isinstance(canonical, CanonicalTransactionInput)
    assert canonical.provider_code == "SIM-PROVIDER-BK"


def test_simulated_adapter_rejects_provider_scope_mismatch():
    adapter = SimulatedProviderAdapter("BK")
    record = SimulatedProviderRecord(
        provider_code="NG",
        agent_ref="SIM-AGENT-0001",
        account_ref="SIM-ACCT-NG-0001",
        record_type="provider_balance",
        record_ref="SIM-BAL-0001",
        amount=Decimal("100.00"),
    )

    with pytest.raises(ProviderAdapterError):
        adapter.map_record(record)


def test_simulated_adapter_maps_nullable_provider_balance():
    adapter = SimulatedProviderAdapter("NG")
    record = SimulatedProviderRecord(
        provider_code="NG",
        agent_ref="SIM-AGENT-0001",
        account_ref="SIM-ACCT-NG-0001",
        record_type="provider_balance",
        record_ref="SIM-BAL-0001",
        amount=None,
        availability_state="missing",
    )

    canonical = adapter.map_record(record)

    assert isinstance(canonical, CanonicalProviderBalanceInput)
    assert canonical.reported_balance is None
