# PROMPT-0016 Operations Layer

## Prompt ID
PROMPT-0016

## Prompt Type
implement-module

## Date
2026-07-11

## Objective
Implement advisory alert generation, traceable case management, provider-safe REST APIs, persistence, tests, OpenAPI documentation, and prompt traceability.

## Module
operations-layer

## Requirement IDs
FR-007, FR-008, NFR-002, NFR-004, API-001, DB-001, SAFE-001, SAFE-002, SAFE-003, FAIL-005, FAIL-006, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
fed0a601a4f57fe762c67939279eefbc17ea8b98b74f6c0ecc76524d0b5be796

## Exact Prompt
````text
Module: Operations Layer

Implement only:

Alert Engine
Case Management
REST API

Use existing:

liquidity engine
anomaly engine
confidence/evidence modules
persistence layer

Do not redesign existing modules.

Alert Engine

Create alerts from existing signals:

liquidity shortage risk
anomaly findings
data quality issues

Each alert must contain:

alert id
type
severity
provider scope
agent/outlet scope
evidence
confidence
recommended next step
owner
status
created time
audit trail

Statuses:

open
acknowledged
escalated
resolved
closed

Rules:

Advisory only.
Human review required.
No fraud declaration.
No automatic blocking.
No money transfer/refill action.

Case Management

Implement workflow:

Alert
 Assign owner
 Acknowledge
 Add notes
 Escalate if needed
 Resolve
 Close

Store:

case
owner
notes
status history
escalation history
resolution information
audit events

Important:

Every status change must be traceable.

REST API

Create APIs:

Alerts:

GET /api/v1/alerts
GET /api/v1/alerts/{id}
POST /api/v1/alerts/{id}/acknowledge
POST /api/v1/alerts/{id}/assign

Cases:

GET /api/v1/cases
GET /api/v1/cases/{id}
POST /api/v1/cases
POST /api/v1/cases/{id}/escalate
POST /api/v1/cases/{id}/resolve

Use existing services.
Do not duplicate business logic inside APIs.

Provider Safety
Keep provider boundaries.
User should only see authorized scope.
Shared cash remains provider-independent.
Do not expose another provider's private data.

Tests

Add:

alert creation test
alert lifecycle test
assignment test
acknowledgement test
escalation test
resolution test
case lifecycle test
audit event test
API validation test
PostgreSQL rollback test

Documentation

Update:

README.md
OpenAPI docs
implementation-status.md
task-board.md
requirement-traceability.md
commit-ledger.md

Create next prompt record:

prompts/history/PROMPT-XXXX-operations-layer.md

with:

exact prompt
checksum
files changed
tests
result




Requirement-IDs: <APPROVED IDS>
Prompt-ID: <NEXT ID>
Module: operations-layer
Tests: unit, api, postgres, audit lifecycle completed

Return only:

Files changed
Alert workflow
Case workflow
API list
Tests
Commit
Remaining blockers



Stop. implement ,i have pushed previous changes to git
````

## In Scope
- Advisory alert generation from existing liquidity, anomaly, and feed-quality records
- Evidence, confidence, assignments, lifecycle audit, and provider/area authorization
- Traceable case notes, history, escalation, resolution, closure, and optimistic versions
- The nine requested FastAPI operations routes and generated OpenAPI contracts
- Unit, API, safety, Neon PostgreSQL persistence, scope, audit, and rollback tests
- Required documentation and traceability updates

## Out of Scope
- Alert-generation REST endpoints
- Authentication credential verification
- Financial transfers, refills, blocking, or automatic operational action
- Fraud or wrongdoing declarations
- LLM decisions or explanations

## Files Read
- Requirements, workflows, architecture, database design, API contracts/schemas, security, traceability, implementation status, plan, task board, and prior prompt records
- Existing liquidity, anomaly, confidence, evidence, persistence, scenario, API, authorization-boundary, and test modules

## Files Changed
- `backend/app/alerts/`
- `backend/app/cases/`
- `backend/app/auth/`
- `backend/app/api/`
- `backend/app/main.py`
- `backend/tests/unit/test_operations_api.py`
- `backend/tests/unit/test_operations_safety.py`
- `backend/tests/integration/test_operations_persistence_postgres.py`
- `README.md`
- `docs/06-api-contracts.md`
- `docs/06b-api-schemas.md`
- `docs/11-requirement-traceability.md`
- `docs/14-implementation-status.md`
- `docs/17-implementation-plan.md`
- `docs/18-task-board.md`
- `docs/commit-ledger.md`
- `prompts/history/PROMPT-0016-operations-layer.md`

## Checks Run
- Focused operations unit/API/safety/Neon PostgreSQL suite: `12 passed`; coverage `84.82%`
- Neon PostgreSQL alert-source, lifecycle, scope, audit, and rollback tests: `7 passed`
- Full backend unit suite: `86 passed`
- Governance suite: `18 passed`
- Ruff format and lint passed; strict MyPy passed for `100` source files; compilation passed
- Prompt-record and requirement-ID validators passed

## Sonar Status
- Pending remote run

## Audit Status
- Pending remote run

## Final Outcome
Implemented and locally verified. Alert and case outputs remain advisory and human-reviewed; no blocking, money movement, wrongdoing declaration, or alert-generation API was added.
