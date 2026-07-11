# SUST Onsite Hackathon Repository

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

## CI Mode
The repository is currently in governance-only mode. CI validates documentation, prompt traceability, requirement IDs, Sonar configuration, and governance tests.

After repository foundation scaffolds `backend/` or `frontend/`, product-code mode begins and backend/frontend quality checks become mandatory.

## Documentation Reading Order
1. `docs/00-project-context.md`
2. `docs/01-requirements.md`
3. `docs/02-prd.md`
4. `docs/03-workflows.md`
5. `docs/04-architecture.md`
6. `docs/05-database-design.md`
7. `docs/06-api-contracts.md`
8. `docs/07-security-and-safety.md`
9. `docs/08-testing-and-metrics.md`
10. `docs/11-requirement-traceability.md`
11. `docs/12-decision-log.md`
12. `docs/17-implementation-plan.md`
13. `docs/18-task-board.md`

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
Design, governance, prompt traceability, CI, and SonarQube foundation are prepared. Product business logic, ORM models, migrations, backend routes, frontend screens, and algorithms are intentionally not implemented yet.

## Recommended First Coding Module
Repository foundation, followed by synthetic scenario fixtures.
