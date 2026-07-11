# Deployment

Deployment is demo-only. Do not claim production readiness.

## Canonical Local Docker Compose Topology
Local Docker Compose is the canonical development/demo topology until a cloud target is explicitly approved.

```text
browser -> Next.js dev server -> FastAPI app -> PostgreSQL
                                -> local filesystem/log output
```

## Environment Variable Names
- APP_ENV
- APP_NAME
- DATABASE_URL
- DATABASE_SYNC_URL
- NEXT_PUBLIC_API_BASE_URL
- LLM_EXPLANATION_PROVIDER
- LLM_EXPLANATION_ENABLED
- SONAR_TOKEN
- SONAR_HOST_URL
- VALIDATION_FEED_DELAY_MINUTES
- VALIDATION_STALE_MINUTES
- VALIDATION_FUTURE_TOLERANCE_MINUTES
- VALIDATION_TIMESTAMP_SKEW_MINUTES
- VALIDATION_MAX_METADATA_KEYS
- VALIDATION_MAX_METADATA_VALUE_LENGTH
- VALIDATION_SUPPORTED_CURRENCIES

## Database Initialization
Repository foundation command:
```bash
docker compose up -d postgres
alembic upgrade head
```

The initial domain schema migration exists. Scenario data is created by the internal scenario CLI after migrations run.

After the database schema module, the initial domain migration is:
```bash
cd backend
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

Local PostgreSQL must be running before those commands execute. In GitHub Actions, backend jobs provide a PostgreSQL service for migration tests.

## Seed and Scenario Commands
Implemented internal developer/demo commands from `backend/`:
```bash
python -m app.scenarios.cli list
python -m app.scenarios.cli run normal_day --seed 1001 --profile small --start-timestamp 2026-07-11T09:00:00+00:00
python -m app.scenarios.cli run hidden_provider_shortage --seed 3001 --profile small --start-timestamp 2026-07-11T09:00:00+00:00
python -m app.scenarios.cli run liquidity_pressure_unusual_activity --seed 5001 --profile small --start-timestamp 2026-07-11T09:00:00+00:00
python -m app.scenarios.cli replay --run-id SIM-RUN-000001
python -m app.scenarios.cli reset --run-id SIM-RUN-000001
```

Reset and replay are scoped to a single synthetic run ID and must not truncate reference data or unrelated runs.

## Health and Readiness Checks
Implemented foundation endpoints:
- `GET /api/v1/health`
- `GET /api/v1/readiness`

Local stack commands:
```bash
docker compose up --build
docker compose down
```

Backend test command from `backend/`:
```bash
pytest
```

Frontend test command from `frontend/`:
```bash
npm test
```

## Backup Demo Procedure
- Keep deterministic scenario seed files.
- Keep screenshots or a short video of the golden flow.
- Keep a local fallback runbook.
- Do not switch to production data as a fallback.

## Logs
Planned locations:
- FastAPI application logs: standard output in local Docker Compose.
- Frontend logs: Next.js dev/build output.
- Scenario and audit logs: PostgreSQL `scenario_runs`, `provider_feed_statuses`, `data_quality_events`, and `audit_events`.

## Rollback Approach
- Use Git commit rollback for code/config changes.
- Use deterministic demo seed reset for scenario state.
- Do not perform destructive database resets without explicit approval.

## SonarQube Secret Setup
Configure GitHub Actions secrets:
- SONAR_TOKEN
- SONAR_HOST_URL

Project key is authoritative in `sonar-project.properties`.

## Branch Protection Recommendation
- Require CI traceability job.
- Require backend-quality, frontend-quality, and test-and-coverage jobs after repository foundation.
- Keep SonarQube analysis and Quality Gate configured as best-effort, non-blocking checks.
- Protect `main` from direct pushes during implementation.

## Quality Gate Merge Protection
Failed, skipped, unavailable, or configuration-error Quality Gate results must be recorded honestly but do not block implementation, commits, merging, or demo preparation. Remote Quality Gate status remains Pending until GitHub Actions runs.

## Known Limitations
- No product deployment exists yet.
- Deterministic scenario commands and internal provider validation services exist; downstream business engines remain planned.
- Repository foundation implements health/readiness only; feature APIs remain planned.
- Product-code CI is mandatory after repository foundation.

## README Completion Checklist
Before release/demo packaging, README must include:
- One-paragraph project overview.
- Safety boundary and synthetic-data statement.
- Prerequisites: Docker, Node.js target version, Python target version.
- Environment setup: copy `.env.example` to `.env` and fill local placeholders.
- `docker compose up` steps for local demo.
- Alembic migration command after backend scaffold exists.
- Seed, scenario run, reset, and replay commands after scenario engine exists.
- Links to `docs/16-demo-script.md`, `docs/04-architecture.md`, and `docs/19-presentation-outline.md`.

## Sonar Project Key Policy
`SONAR_TOKEN` and `SONAR_HOST_URL` are GitHub secrets. `SONAR_PROJECT_KEY` is intentionally not required as a secret because `sonar.projectKey` is authoritative in `sonar-project.properties`. If a future CI provider requires the project key as an environment value, update this document, `sonar-project.properties`, and CI in one traceable commit.
