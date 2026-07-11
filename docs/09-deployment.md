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

## Database Initialization
Repository foundation command:
```bash
docker compose up -d postgres
alembic upgrade head
```

No business migrations exist yet, so `alembic upgrade head` currently validates the migration foundation only.

## Seed and Scenario Commands
Planned commands after scenario engine exists:
```bash
python -m backend.app.scenarios.seed_demo
python -m backend.app.scenarios.run SCN-001
python -m backend.app.scenarios.reset --run-id <run-id>
```

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
- Scenario and audit logs: PostgreSQL audit tables after implementation.

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
- Require SonarQube analysis and Quality Gate before merge once secrets are configured.
- Protect `main` from direct pushes during implementation.

## Quality Gate Merge Protection
Failed Quality Gate blocks merge and accepted completion. Remote Quality Gate status remains Pending until GitHub Actions runs.

## Known Limitations
- No product deployment exists yet.
- No business migrations or seed commands exist yet.
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
