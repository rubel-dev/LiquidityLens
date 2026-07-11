# PROMPT-0008: Database Schema and Migrations

## Prompt ID
PROMPT-0008

## Prompt Type
implement-module

## Date
2026-07-11

## Objective
Start the second implementation phase by adding the LiquidityLens database schema and migration foundation while preserving honest reporting of the pre-existing foundation CI failure.

## Module
database-schema-and-migrations

## Requirement IDs
DB-001, FR-001, FR-002, FR-008, NFR-002, NFR-003, NFR-004, DATA-001, DATA-002, DATA-003, SEC-001, SAFE-001, SAFE-002, SAFE-003, DOC-001, DOC-002, DOC-003, QUALITY-001, QUALITY-002, CI-001

## Exact Prompt SHA-256
69c23746869f353d3985dabe36322dd1ec85076ac4be52b34f729f391ce14b18

## Exact Prompt
```text
start 2nd implementation phase
```

## In Scope
- SQLAlchemy typed domain models for all documented MVP database tables.
- Alembic initial domain schema migration.
- Metadata, provider-separation, synthetic-identifier, and PostgreSQL migration tests.
- CI PostgreSQL service configuration for migration tests.
- Documentation and traceability updates.

## Out of Scope
- Scenario generation or seed data.
- Provider feed ingestion.
- Liquidity, anomaly, confidence, explanation, alert, or case business logic.
- Authentication middleware, authorization middleware, APIs, dashboards, and production deployment.

## Files Read
- README.md
- docs/01-requirements.md
- docs/05-database-design.md
- docs/09-deployment.md
- docs/11-requirement-traceability.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- backend/app/persistence/base.py
- backend/app/persistence/database.py
- backend/alembic/env.py
- backend/pyproject.toml
- .github/workflows/ci.yml
- sonar-project.properties

## Files Changed
- .github/workflows/ci.yml
- README.md
- backend/alembic/env.py
- backend/alembic/versions/20260711_0001_initial_domain_schema.py
- backend/app/persistence/base.py
- backend/app/persistence/models/
- backend/tests/integration/test_domain_migration_postgres.py
- backend/tests/unit/test_domain_metadata.py
- backend/tests/unit/test_synthetic_identifiers.py
- docs/05-database-design.md
- docs/09-deployment.md
- docs/11-requirement-traceability.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- prompts/history/PROMPT-0008-database-schema-and-migrations.md

## Checks Run
- `gh run list -R rubel-dev/LiquidityLens --limit 3` showed the latest foundation CI run failed.
- `python -m pytest` from `backend/` passed locally with 16 passed, 2 skipped, and 97.21% coverage.
- PostgreSQL migration tests skipped locally because Docker/PostgreSQL was unavailable.
- `docker compose up -d postgres` failed because Docker Desktop/daemon was not running.

## Migration Result
SQLAlchemy metadata and Alembic migration file are present. PostgreSQL upgrade/downgrade/re-upgrade validation is configured for CI but not locally verified in this sandbox.

## SonarQube Status
Pending remote CI. SonarQube pass is not claimed.

## Human Audit Status
Pending.

## Final Outcome
Database schema code, migration foundation, CI PostgreSQL service configuration, tests, and documentation were added. The module remains In Progress until PostgreSQL migration validation and the pre-existing remote foundation CI failure are inspected and resolved.
