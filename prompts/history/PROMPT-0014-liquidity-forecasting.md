# PROMPT-0014 Liquidity Forecasting Engine

## Prompt ID
PROMPT-0014

## Prompt Type
implement-module

## Date
2026-07-11

## Objective
Implement deterministic provider-specific e-money and provider-independent shared-cash runway forecasting with confidence, evidence, persistence, tests, and measured synthetic metrics.

## Module
liquidity-forecasting

## Requirement IDs
FR-001, FR-004, NFR-003, NFR-004, DATA-003, DB-001, SAFE-001, SAFE-002, SAFE-003, MET-001, MET-002, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
870fb9cb4da6b32d26fb12fee29902dde567cbeb4a95c2aeb5a0b73761c6e2a6

## Exact Prompt
````text
hey,look at my backend & the docs & probelem statement at project root ,them implement the next backend module,dont create branch or push to git,i will do it by my own to the main branch ,next module instruction : Implement only this module:

Liquidity Forecasting Engine

Read first:

* `docs/01-requirements.md`
* `docs/04-architecture.md`
* `docs/05-database-design.md`
* `docs/08-testing-and-metrics.md`
* `docs/11-requirement-traceability.md`
* `docs/14-implementation-status.md`
* existing scenario, validation, persistence, and test modules

Do not redesign existing modules.

## Objective

Calculate and persist:

1. Provider-specific e-money runway
2. Shared physical-cash runway
3. Estimated shortage time
4. Forecast confidence
5. Explainable forecast evidence

## Rules

* Provider balances must remain separate.
* Never use one providers balance for another provider.
* Shared cash must remain provider-independent.
* Missing balance must remain unknown, not zero.
* Poor data quality must reduce confidence.
* Do not declare fraud.
* Do not execute transfers, refills, blocking, or financial actions.
* Core forecasting must be deterministic.
* Do not use an LLM in this module.

## Implement

Create or complete:

```text
backend/app/liquidity/
 schemas.py
 demand.py
 forecast.py
 confidence.py
 evidence.py
 repository.py
 service.py
 exceptions.py
```

## Forecast Logic

Use recent validated transactions to estimate demand rates.

Calculate separately:

```text
Provider e-money runway =
current provider balance / expected provider e-money consumption rate
```

```text
Shared cash runway =
current shared cash / expected net physical-cash outflow rate
```

Handle transaction directions correctly:

* Cash-out decreases physical cash.
* Cash-in increases physical cash.
* Provider e-money movement must follow the documented accounting convention.

Support:

* rolling demand window
* configurable forecast horizon
* minimum-data requirement
* volatility adjustment
* data-quality confidence multiplier
* event context such as Eid or salary day
* no-activity case
* insufficient-data case
* delayed or missing feed case

## Output

Every forecast must include:

* agent ID
* provider ID or shared-cash scope
* current known balance
* expected demand rate
* runway minutes
* estimated shortage time
* risk level
* confidence
* data-quality impact
* calculation window
* evidence
* limitations
* generated timestamp
* rule/model version

Risk levels:

```text
healthy
watch
warning
critical
unknown
```

Do not show a shortage time when confidence or data completeness is insufficient. Return `unknown` with evidence.

## Persistence

Persist results using existing:

* `liquidity_forecasts`
* `evidence_items`
* `confidence_assessments`
* `rule_versions`
* `audit_events`

Do not create alerts yet.

## Tests

Add tests for:

* healthy provider balance
* hidden provider shortage
* shared-cash shortage
* provider balances remaining isolated
* cash-in and cash-out accounting
* zero transaction activity
* insufficient history
* missing balance
* delayed feed
* conflicting data
* low data-quality confidence
* volatile demand
* Eid legitimate demand spike
* deterministic output
* Decimal money calculations
* timezone-aware shortage time
* persisted forecast and evidence
* PostgreSQL rollback on failure

Measure:

* forecast error on synthetic scenarios
* shortage detection lead time
* average and p95 processing latency

Do not invent results.

## Documentation

Update:

* `README.md`
* `docs/08-testing-and-metrics.md`
* `docs/11-requirement-traceability.md`
* `docs/14-implementation-status.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`

## Prompt Traceability

Create the next sequential prompt record under:

`prompts/history/`

Store this exact prompt with checksum.

## Out of Scope

Do not implement:

* anomaly detection
* LLM explanations
* alert generation
* case management
* public REST APIs
* authentication
* frontend dashboards

## Acceptance Criteria

Complete only when:

* provider runway works
* shared-cash runway works
* provider isolation is preserved
* missing data returns unknown safely
* data quality changes confidence
* evidence explains every forecast
* PostgreSQL tests pass
* local lint, typing, tests, and coverage run
* documentation matches code
* working tree is clean after commit

Commit:

```text
feat(liquidity): add provider and shared-cash forecasting

Requirement-IDs: <APPROVED IDS>
Prompt-ID: <NEXT PROMPT ID>
Module: liquidity-forecasting
Tests: unit, PostgreSQL, scenario, safety, typing, lint, and coverage checks completed
```

Return only:

* Files changed
* Forecast logic
* Tests
* Metrics
* Commit
* Remaining blockers
* Ready for anomaly engine: YES/NO

Do not start the anomaly engine.
````

## In Scope
- Deterministic provider e-money and shared physical-cash forecasts.
- Confidence degradation, evidence, persistence, scenario integration, metrics, safety tests, and documentation.

## Out of Scope
- Anomaly detection, LLM explanations, alerts, cases, public APIs, authentication, and frontend changes.
- Branch creation or remote push.

## Files Read
- Root problem statement source and README.
- Required requirements, architecture, database, metrics, traceability, and status documents.
- Existing scenario, validation, persistence, migration, and test modules.

## Files Changed
- `backend/app/liquidity/*`
- `backend/tests/unit/test_liquidity_forecasting.py`
- `backend/tests/unit/test_liquidity_metrics.py`
- `backend/tests/unit/test_liquidity_safety.py`
- `backend/tests/integration/test_liquidity_persistence_postgres.py`
- `README.md`
- `docs/08-testing-and-metrics.md`
- `docs/11-requirement-traceability.md`
- `docs/14-implementation-status.md`
- `docs/17-implementation-plan.md`
- `docs/18-task-board.md`
- `docs/commit-ledger.md`

## Checks Run
- Liquidity unit/safety tests: 17 passed.
- Controlled metric tests: 2 passed.
- Neon PostgreSQL integration: 6 passed.
- Combined liquidity suite: 25 passed with 96.01% module coverage.
- Existing full unit suite: 63 tests functionally passed; repository-wide unit-only coverage was 66.53% because legacy destructive integration fixtures were not run against Neon.
- Whole-backend Ruff format/lint, strict MyPy, and compileall: passed.
- Prompt checksum, requirement traceability, and 18 governance tests: passed.

## Sonar Status
Pending remote CI; no push requested.

## Audit Status
Local module, PostgreSQL, safety, typing, lint, coverage, prompt, requirement, and governance checks passed. User-managed commit and remote CI remain pending.

## Final Outcome
Liquidity forecasting passed its local acceptance evidence. No branch, commit, or remote push was created per the user's source-control instruction.
