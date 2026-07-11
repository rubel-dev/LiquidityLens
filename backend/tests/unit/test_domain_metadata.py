from decimal import Decimal

from sqlalchemy import DateTime, Numeric, UniqueConstraint

from app.persistence.base import Base, import_all_models

REQUIRED_TABLES = {
    "users",
    "roles",
    "user_role_assignments",
    "providers",
    "areas",
    "agents",
    "agent_provider_accounts",
    "shared_cash_snapshots",
    "provider_balance_snapshots",
    "transactions",
    "provider_feed_statuses",
    "data_quality_events",
    "scenarios",
    "scenario_runs",
    "liquidity_forecasts",
    "anomaly_findings",
    "evidence_items",
    "confidence_assessments",
    "explanation_records",
    "rule_versions",
    "alerts",
    "alert_assignments",
    "cases",
    "case_notes",
    "case_status_history",
    "escalations",
    "audit_events",
    "human_feedback",
    "metric_observations",
}


def metadata_tables():
    import_all_models()
    return Base.metadata.tables


def test_all_required_mvp_tables_exist_in_metadata():
    assert REQUIRED_TABLES <= set(metadata_tables())


def test_required_unique_constraints_exist():
    tables = metadata_tables()
    constraints = {
        table_name: {constraint.name for constraint in table.constraints}
        for table_name, table in tables.items()
    }

    assert "uq_agent_provider_account" in constraints["agent_provider_accounts"]
    assert "uq_agent_provider_synthetic_ref" in constraints["agent_provider_accounts"]
    assert any(
        isinstance(constraint, UniqueConstraint)
        and {column.name for column in constraint.columns} == {"synthetic_transaction_ref"}
        for constraint in tables["transactions"].constraints
    )
    assert "uq_cases_origin_alert" in constraints["cases"]


def test_important_indexes_exist():
    tables = metadata_tables()
    index_names = {index.name for table in tables.values() for index in table.indexes}

    assert "ix_transactions_agent_occurred" in index_names
    assert "ix_transactions_provider_occurred" in index_names
    assert "ix_provider_balance_agent_provider_observed" in index_names
    assert "ix_shared_cash_agent_observed" in index_names
    assert "ix_feed_provider_agent_observed" in index_names
    assert "ix_alerts_status_priority_owner_provider_created" in index_names
    assert "ix_cases_status_owner_provider_updated" in index_names
    assert "ix_audit_entity_created" in index_names
    assert "ix_scenario_runs_scenario_status_started" in index_names
    assert "ix_anomaly_agent_provider_detected" in index_names
    assert "ix_forecasts_agent_provider_time" in index_names


def test_money_fields_use_fixed_precision_numeric():
    tables = metadata_tables()
    money_columns = [
        tables["shared_cash_snapshots"].c.amount,
        tables["provider_balance_snapshots"].c.amount,
        tables["transactions"].c.amount,
    ]

    for column in money_columns:
        assert isinstance(column.type, Numeric)
        assert column.type.precision == 14
        assert column.type.scale == 2

    assert isinstance(Decimal("1.23"), Decimal)


def test_timestamps_are_timezone_aware():
    for table in metadata_tables().values():
        for column in table.columns:
            if column.name.endswith("_at") or column.name in {"observed_at", "occurred_at"}:
                if isinstance(column.type, DateTime):
                    assert column.type.timezone is True


def test_shared_cash_has_no_provider_column():
    assert "provider_id" not in metadata_tables()["shared_cash_snapshots"].columns


def test_provider_balance_has_exact_provider_scope_and_account_fks():
    table = metadata_tables()["provider_balance_snapshots"]
    fk_names = {constraint.name for constraint in table.foreign_key_constraints}

    assert "provider_id" in table.columns
    assert "fk_provider_balance_account_provider" in fk_names
    assert "fk_provider_balance_account_agent" in fk_names


def test_append_only_tables_do_not_use_delete_orphan_cascade():
    import_all_models()
    append_only_tables = {"case_status_history", "escalations", "audit_events"}
    for mapper in Base.registry.mappers:
        if mapper.local_table.name in append_only_tables:
            for relationship in mapper.relationships:
                assert "delete-orphan" not in relationship.cascade
