# PROMPT-0006: Repository Foundation

## Prompt ID
PROMPT-0006

## Prompt Type
implement-module

## Date
2026-07-11

## Objective
Create the first product-code foundation module for FastAPI, Next.js, PostgreSQL local development, SQLAlchemy/Alembic, Docker Compose, product-code CI, and health/readiness checks.

## Module
repository-foundation

## Requirement IDs
ARCH-001, ARCH-002, API-001, DB-001, QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001, DOC-002, DOC-003, SEC-001, SAFE-001, SAFE-002, SAFE-003

## Exact Prompt SHA-256
fe64bb76e89f5b48d484ccfa226fce06255933b10525d4924b88e2c5096b100b

## Exact Prompt
````text
You are implementing the first product-code module of the existing LiquidityLens repository.

The design, governance, architecture, requirements, CI, prompt traceability, and implementation plan already exist.

Do not restart the project.
Do not regenerate the PRD or architecture.
Do not implement business features beyond this module.

# MODULE

Repository Foundation

# REQUIREMENT IDS

* ARCH-001
* ARCH-002
* API-001
* DB-001
* QUALITY-001
* QUALITY-002
* CI-001
* CI-002
* DOC-001
* DOC-002
* DOC-003
* SEC-001
* SAFE-001
* SAFE-002
* SAFE-003

# READ FIRST

Read and follow:

* `README.md`
* `docs/00-project-context.md`
* `docs/01-requirements.md`
* `docs/02-prd.md`
* `docs/03-workflows.md`
* `docs/04-architecture.md`
* `docs/05-database-design.md`
* `docs/06-api-contracts.md`
* `docs/06b-api-schemas.md`
* `docs/07-security-and-safety.md`
* `docs/08-testing-and-metrics.md`
* `docs/09-deployment.md`
* `docs/11-requirement-traceability.md`
* `docs/12-decision-log.md`
* `docs/13-known-risks.md`
* `docs/14-implementation-status.md`
* `docs/15-code-quality-and-commit-policy.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`
* `.github/workflows/ci.yml`
* `sonar-project.properties`
* `.env.example`

Inspect the complete existing repository before making changes.

The documentation is the approved source of truth.

# OBJECTIVE

Create a clean, runnable, tested repository foundation for:

* FastAPI backend
* Next.js TypeScript frontend
* PostgreSQL local development
* SQLAlchemy and Alembic foundation
* Docker Compose
* mandatory product-code CI
* health and readiness checks

Do not implement liquidity forecasting, anomaly detection, alerts, cases, scenario generation, or end-user dashboards in this step.

# IN SCOPE

## 1. Backend Foundation

Create:

```text
backend/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ main.py
â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ config.py
â”‚   â”‚   â”œâ”€â”€ logging.py
â”‚   â”‚   â””â”€â”€ errors.py
â”‚   â”œâ”€â”€ auth/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ providers/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ scenarios/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ validation/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ liquidity/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ anomaly/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ confidence/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ explanations/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ alerts/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ cases/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ audit/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ metrics/
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â””â”€â”€ routes/
â”‚   â”‚       â”œâ”€â”€ __init__.py
â”‚   â”‚       â”œâ”€â”€ health.py
â”‚   â”‚       â””â”€â”€ readiness.py
â”‚   â””â”€â”€ persistence/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ database.py
â”‚       â””â”€â”€ base.py
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ unit/
â”‚   â””â”€â”€ integration/
â”œâ”€â”€ alembic/
â”œâ”€â”€ alembic.ini
â”œâ”€â”€ pyproject.toml
â””â”€â”€ Dockerfile
```

Use Python 3.12.

Configure:

* FastAPI
* Pydantic Settings
* SQLAlchemy 2.x
* Alembic
* PostgreSQL psycopg driver
* Ruff
* MyPy
* Pytest
* pytest-cov
* HTTPX for API tests

Use dependency injection where useful.

Do not create domain database tables yet.

Create only the SQLAlchemy declarative base, engine/session configuration, and Alembic foundation.

## 2. API Foundation

Use the canonical API prefix:

```text
/api/v1
```

Implement only:

```text
GET /api/v1/health
GET /api/v1/readiness
```

### Health endpoint

Return process-level health without requiring the database.

Example:

```json
{
  "status": "ok",
  "service": "liquiditylens-api",
  "version": "0.1.0"
}
```

### Readiness endpoint

Check database connectivity.

Return:

* HTTP 200 when the application is ready
* HTTP 503 when the database is unavailable

Do not leak credentials, connection strings, stack traces, or internal secrets.

Add consistent structured error responses.

## 3. Configuration

Use environment-based configuration.

Support:

* `APP_ENV`
* `APP_NAME`
* `DATABASE_URL`
* `DATABASE_SYNC_URL`
* `NEXT_PUBLIC_API_BASE_URL`
* `LLM_EXPLANATION_PROVIDER`
* `LLM_EXPLANATION_ENABLED`

Defaults must be safe for local development.

The LLM must remain disabled by default.

Do not add a real LLM SDK in this module.

## 4. Logging

Implement structured application logging.

Requirements:

* timestamp
* level
* logger name
* message
* request/correlation ID where available

Never log:

* secrets
* passwords
* tokens
* database URLs containing credentials
* real customer identifiers

## 5. Frontend Foundation

Create a Next.js application under:

```text
frontend/
```

Use:

* Next.js
* TypeScript
* App Router
* ESLint
* Prettier
* Vitest
* React Testing Library

Create:

```text
frontend/src/app/
frontend/src/features/
frontend/src/components/
frontend/src/lib/
frontend/src/types/
```

Implement only a minimal foundation page that displays:

* LiquidityLens
* â€œSafe multi-provider liquidity decision-support prototypeâ€
* API connectivity status using `/api/v1/health`
* Clear â€œSynthetic data onlyâ€ label

Do not build dashboards, charts, alerts, role portals, or financial features yet.

## 6. Docker Compose

Update or replace `docker-compose.yml` to run:

* PostgreSQL
* FastAPI backend
* Next.js frontend

Include:

* health checks
* service dependencies
* named PostgreSQL volume
* environment-file support
* no committed secrets

Canonical local ports:

* frontend: `3000`
* backend: `8000`
* PostgreSQL: `5432`

The stack must start with:

```bash
docker compose up --build
```

## 7. CI Product-Code Mode

Once `backend/` and `frontend/` exist, CI must treat product checks as mandatory.

Ensure `.github/workflows/ci.yml` runs:

### Backend

* Ruff format check
* Ruff lint
* MyPy
* Pytest
* coverage generation
* minimum initial coverage threshold of 80% for foundation code

### Frontend

* Prettier check
* ESLint
* TypeScript type check
* Vitest
* coverage generation
* production build

Remove any behavior that silently treats missing required scripts as success after scaffolding.

Ensure coverage files match `sonar-project.properties`:

* `backend/coverage.xml`
* `frontend/coverage/lcov.info`

Keep:

* commit-range traceability validation
* prompt-record validation
* requirement-ID validation
* governance tests
* SonarQube scan
* Quality Gate job

Do not weaken existing governance checks.

## 8. Tests

Add tests for:

### Backend

* health endpoint success
* readiness success with available database
* readiness failure with unavailable database
* configuration loading
* secrets not exposed in error responses
* application startup

### Frontend

* foundation page renders
* synthetic-data label renders
* API health success state
* API unavailable state

### Docker/configuration

Validate configuration files where practical.

All tests must be deterministic.

## 9. Documentation Updates

Update:

* `README.md`
* `docs/09-deployment.md`
* `docs/11-requirement-traceability.md`
* `docs/14-implementation-status.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`

Mark only Repository Foundation as implemented after tests pass.

Do not mark database schema, scenario engine, analytics, APIs, or UI modules implemented.

Document exact commands for:

```bash
docker compose up --build
docker compose down
pytest
npm test
```

## 10. Prompt Traceability

Create the next available prompt record under:

```text
prompts/history/
```

Expected ID:

```text
PROMPT-0006
```

Use the next sequential ID if that ID already exists.

The record must include:

* Prompt ID
* Prompt type
* date
* objective
* module
* requirement IDs
* exact prompt
* SHA-256 checksum
* in scope
* out of scope
* files read
* files changed
* tests run
* SonarQube status
* human audit status
* final outcome

Store this exact prompt verbatim.

Do not include secrets.

## 11. Commit

Prepare one focused commit:

```text
feat(foundation): scaffold backend frontend and local runtime

Requirement-IDs: ARCH-001, ARCH-002, API-001, DB-001, QUALITY-001, QUALITY-002, CI-001, DOC-001, DOC-002, DOC-003
Prompt-ID: <CURRENT-PROMPT-ID>
Module: repository-foundation
Tests: backend, frontend, Docker configuration, governance, and coverage checks passed
```

Do not include unrelated features.

Do not claim SonarQube passed until remote CI confirms it.

# OUT OF SCOPE

Do not implement:

* database domain tables
* business migrations
* synthetic transactions
* providers or agents
* scenario engine
* liquidity forecasting
* anomaly detection
* confidence fusion
* LLM integration
* alerts
* cases
* authentication logic
* provider-scope authorization logic
* dashboards
* metrics endpoint
* demo reset/replay
* production deployment

Only interfaces, empty module boundaries, health/readiness, tooling, local runtime, and tests are allowed.

# ACCEPTANCE CRITERIA

This module is complete only when:

1. `docker compose up --build` starts PostgreSQL, backend, and frontend.
2. `/api/v1/health` returns HTTP 200.
3. `/api/v1/readiness` returns HTTP 200 when PostgreSQL is available.
4. `/api/v1/readiness` returns HTTP 503 when PostgreSQL is unavailable.
5. Frontend displays the API health state.
6. Backend formatting, linting, typing, tests, and coverage pass.
7. Frontend formatting, linting, typing, tests, build, and coverage pass.
8. Governance tests still pass.
9. Prompt traceability validation passes.
10. Requirement-ID validation passes.
11. No secrets are committed.
12. Documentation accurately reflects the completed module.
13. The final working tree is clean after commit.

# FINAL RESPONSE FORMAT

Return only:

## Prompt Record Created

## Files Created

## Files Updated

## Backend Foundation

## Frontend Foundation

## Docker Compose

## CI Product-Code Transition

## Tests Run

## Coverage

## Validation Results

## Commit Created

## Git Status

## Remote CI Result

## SonarQube Result

## Quality Gate Result

## Remaining Blockers

## Recommended Next Module

Do not begin Database Schema and Migrations.
````

## In Scope
- FastAPI backend foundation with health/readiness endpoints.
- SQLAlchemy declarative base, engine/session setup, and Alembic foundation without domain tables.
- Next.js TypeScript foundation page with API health state and synthetic-data label.
- Docker Compose local runtime for PostgreSQL, backend, and frontend.
- Product-code CI transition while preserving governance checks.
- Documentation/status updates and prompt traceability.

## Out of Scope
- Domain database tables or business migrations.
- Synthetic transactions, provider ingestion, scenarios, forecasting, anomaly detection, alerts, cases, metrics endpoints, dashboards, auth logic, LLM integration, reset/replay, and production deployment.

## Files Read
- README.md
- docs/09-deployment.md
- docs/11-requirement-traceability.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- .github/workflows/ci.yml
- sonar-project.properties
- .env.example
- docker-compose.yml
- scripts/validate_prompt_records.py
- scripts/check_ci_mode.py
- C:\Users\Rubel\.codex\attachments\6e6f759b-d1bf-4c0f-aab0-ddce7f5aee17\pasted-text.txt

## Files Changed
- .env.example
- .github/workflows/ci.yml
- README.md
- docker-compose.yml
- sonar-project.properties
- backend/
- frontend/
- docs/09-deployment.md
- docs/11-requirement-traceability.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- prompts/history/PROMPT-0006-repository-foundation.md

## Checks Run
- `python -m pytest` from `backend/` passed: 7 tests, 84% coverage.
- `python -m unittest discover tests/governance` passed: 18 tests.
- `python scripts/validate_requirement_ids.py` passed.
- `python scripts/check_ci_mode.py` passed with `CI_MODE=product-code`.
- `docker compose config --quiet` passed.
- `git diff --check` passed.
- `npm.cmd install --ignore-scripts` blocked by offline npm cache and rejected network escalation path.

## Sonar Status
Pending remote GitHub Actions run. SonarQube pass is not claimed locally.

## Audit Status
Human audit pending.

## Final Outcome
Repository foundation scaffolding was implemented locally with backend tests and governance checks passing. Frontend dependency installation, frontend tests, Docker build/start, remote CI, SonarQube analysis, and Quality Gate require network/remote execution outside the current approval-layer limitation.
