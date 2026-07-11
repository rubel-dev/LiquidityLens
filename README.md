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

Run frontend tests from `frontend/` after installing Node dependencies:
```bash
npm test
```

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

The authoritative project key is in `sonar-project.properties`. Do not commit secret values. SonarQube Quality Gate must not be claimed as passed until remote CI confirms it.

## Current Status
Design, governance, prompt traceability, CI, SonarQube configuration, repository foundation, and the database schema module are prepared. Only health/readiness endpoints, empty module boundaries, local Docker runtime, the minimal synthetic-data frontend surface, SQLAlchemy domain models, and the initial Alembic schema migration are implemented. Product business logic, seed scenarios, dashboards, alerts/case services, authentication, and algorithms are intentionally not implemented yet.

## Database Migrations
Run migrations from `backend/` after PostgreSQL is available:
```bash
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

## Recommended First Coding Module
Repository foundation, followed by synthetic scenario fixtures.
