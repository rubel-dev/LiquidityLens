# LiquidityLens

This is the canonical implementation repository for the SUST onsite hackathon project: a safe, explainable, auditable multi-provider liquidity and alert-coordination prototype for simulated mobile financial service agents.

## Safety Boundary
The prototype is decision support only. It must not connect to production financial systems, execute money movement, merge provider balances, block or freeze users, collect credentials, or declare wrongdoing. All customer/account-like identifiers must be synthetic and must not look like real phone numbers.

## Locked MVP Stack
- Architecture: modular monolith.
- Frontend: Next.js with TypeScript.
- Backend: FastAPI with Python.
- Database: PostgreSQL.
- ORM and migrations: SQLAlchemy and Alembic.
- Core analytics: deterministic rules and statistical calculations.
- LLM use: vendor-neutral LLM explanation provider for Bengali, Banglish, English summaries only.
- LLM fallback: deterministic templates.

## Local Development
Prerequisites:
- Docker Compose
- Python 3.12
- Node.js 22

Start the local demo foundation:
```bash
docker compose up --build
```

Stop it:
```bash
docker compose down
```

Run backend tests from `backend/` after installing development dependencies:
```bash
pytest
```

Run deterministic scenarios from `backend/` after PostgreSQL is migrated:
```bash
python -m app.scenarios.cli list
python -m app.scenarios.cli run normal_day --seed 1001 --profile small --start-timestamp 2026-07-11T09:00:00+00:00
python -m app.scenarios.cli replay --run-id SIM-RUN-000001
python -m app.scenarios.cli reset --run-id SIM-RUN-000001
```

Run frontend tests from `frontend/` after installing Node dependencies:
```bash
npm test
```

## Operations API
The operations layer exposes provider-scoped advisory alerts and traceable case workflows
under `/api/v1`. Send the synthetic/demo actor UUID in `X-User-ID`; persisted role,
provider, and area assignments restrict every query. OpenAPI is available at `/docs` and
`/openapi.json`.

Implemented routes:
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{id}`
- `POST /api/v1/alerts/{id}/acknowledge`
- `POST /api/v1/alerts/{id}/assign`
- `GET /api/v1/cases`
- `GET /api/v1/cases/{id}`
- `POST /api/v1/cases`
- `POST /api/v1/cases/{id}/escalate`
- `POST /api/v1/cases/{id}/resolve`

Alerts and recommendations require human review. These endpoints cannot block users or
initiate transfers/refills, and anomaly alerts never declare wrongdoing.

## Operations API
The operations layer exposes provider-scoped advisory alerts and traceable case workflows
under `/api/v1`. Send the synthetic/demo actor UUID in `X-User-ID`; database-backed role,
provider, and area assignments restrict every query. OpenAPI is available at `/docs` and
`/openapi.json`.

Implemented routes:
- `GET /api/v1/alerts`
- `GET /api/v1/alerts/{id}`
- `POST /api/v1/alerts/{id}/acknowledge`
- `POST /api/v1/alerts/{id}/assign`
- `GET /api/v1/cases`
- `GET /api/v1/cases/{id}`
- `POST /api/v1/cases`
- `POST /api/v1/cases/{id}/escalate`
- `POST /api/v1/cases/{id}/resolve`

Alerts and recommendations require human review. These endpoints cannot block users or
initiate transfers/refills, and anomaly alerts never declare wrongdoing.

## CI Mode
The repository is now in product-code mode because `backend/` and `frontend/` are scaffolded. CI keeps governance validation and now requires backend formatting, linting, typing, tests, coverage, frontend formatting, linting, type checking, tests, coverage, and production build.

## Documentation Reading Order
1. `docs/00-project-context.md`
2. `docs/01-requirements.md`
3. `docs/02-prd.md`
4. `docs/03-workflows.md`
5. `docs/04-architecture.md`
6. `docs/05-database-design.md`
7. `docs/06-api-contracts.md`
8. `docs/06b-api-schemas.md`
9. `docs/07-security-and-safety.md`
10. `docs/08-testing-and-metrics.md`
11. `docs/11-requirement-traceability.md`
12. `docs/12-decision-log.md`
13. `docs/17-implementation-plan.md`
14. `docs/18-task-board.md`
15. `docs/19-presentation-outline.md`

## Prompt and Commit Traceability
Every implementation or fix commit must include:
- Prompt-ID
- Requirement-IDs
- Module
- Tests
- A matching exact prompt file under `prompts/history/`

Commit format:
```text
<type>(<scope>): <summary>

Requirement-IDs: <IDs>
Prompt-ID: <PROMPT-ID>
Module: <module-name>
Tests: <result>
```

## CI and SonarQube
CI and SonarQube are configured before product code begins. Required secret names are:
- `SONAR_TOKEN`
- `SONAR_HOST_URL`

The authoritative project key is in `sonar-project.properties`. Do not commit secret values.

Per judge instruction, SonarQube analysis and Quality Gate are best-effort and non-blocking. A SonarQube error, unavailable service, configuration issue, or failed Quality Gate must not block implementation, commits, merging, or demo preparation. Continue attempting SonarQube when practical, but record the result honestly as Passed, Failed, Skipped, Unavailable, or Configuration Error. Never claim SonarQube or Quality Gate passed unless remote CI actually reports a pass.

Mandatory local fallback checks remain: formatter, linter, type checker, unit tests, integration tests, coverage, prompt traceability, requirement-ID validation, governance tests, and security/safety validation where applicable.

## Current Status
Design, governance, prompt traceability, CI, SonarQube configuration, repository foundation, database schema, deterministic synthetic scenario engine, internal provider ingestion/validation engine, contract-aligned frontend demo, and deterministic core intelligence are implemented. Core intelligence combines provider-specific and shared-cash liquidity forecasting, one provider-scoped repeated-amount/velocity anomaly rule, evidence-aware confidence fusion, and safe advisory recommendations. It persists forecasts, anomaly findings, confidence assessments, evidence, and rule versions without creating alerts or executing financial actions. Explanations, alerts/cases, authentication, public feature APIs, backend metrics endpoints, and production deployment remain intentionally unimplemented.

## Liquidity Forecasting
The internal `app.liquidity` service forecasts one outlet at a time and never combines provider balances. Its default deterministic rule uses a 120-minute rolling window, a 240-minute forecast horizon, three minimum validated cash transactions, Decimal arithmetic, and the documented accounting convention. Missing balances remain null; missing or conflicting feeds suppress shortage timestamps. The module persists only analytical evidence and does not create alerts or execute financial actions.

## Core Intelligence
`app.anomaly` implements the single versioned `near_identical_cash_out_velocity` rule using provider-scoped cash-out windows, near-identical amounts, velocity against a synthetic baseline, concentrated synthetic references, time-window deviation, and baseline deviation. `app.confidence` reduces signal confidence for incomplete evidence or poor feeds and fuses liquidity/anomaly results without using an LLM. Recommendations are advisory and never declare fraud or trigger alerts, blocking, transfers, or refills.

## Database Migrations
Run migrations from `backend/` after PostgreSQL is available:
```bash
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

## Recommended First Coding Module
Liquidity forecasting engine.
