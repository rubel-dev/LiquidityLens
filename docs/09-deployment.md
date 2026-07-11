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
Planned command after repository foundation:
```bash
docker compose up -d postgres
alembic upgrade head
```

## Seed and Scenario Commands
Planned commands after scenario engine exists:
```bash
python -m backend.app.scenarios.seed_demo
python -m backend.app.scenarios.run SCN-001
python -m backend.app.scenarios.reset --run-id <run-id>
```

## Health and Readiness Checks
Planned endpoints:
- `GET /api/v1/health`
- `GET /api/v1/readiness`

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
- No migrations, seed commands, health endpoint, or readiness endpoint exist yet.
- Governance-only CI can pass without product source; product-code mode becomes mandatory after repository foundation.
