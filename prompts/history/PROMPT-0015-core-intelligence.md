# PROMPT-0015 Core Intelligence

## Prompt ID
PROMPT-0015

## Prompt Type
implement-module

## Date
2026-07-11

## Objective
Implement deterministic liquidity forecasting, anomaly detection, and confidence fusion with evidence, advisory recommendations, persistence, and PostgreSQL verification.

## Module
core-intelligence

## Requirement IDs
FR-001, FR-004, FR-005, FR-006, NFR-003, NFR-004, DATA-002, DATA-003, DB-001, SAFE-001, SAFE-002, SAFE-003, MET-003, MET-004, MET-005, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
751beec4754ad1530cfee6e81680517f12c780319998801b42876401b7fca780

## Exact Prompt
````text
i have commited & pushed ,Module: Core Intelligence






Implement:



- Liquidity Forecasting

- Anomaly Detection

- Confidence Engine



Rules



- Keep provider balances isolated.

- Shared cash is separate.

- Unknown balance stays unknown.

- Deterministic calculations only.

- No LLM decisions.

- No fraud declaration.



Output



- runway

- shortage time

- anomaly findings

- confidence

- evidence

- recommendation



Persist:



- liquidity_forecasts

- anomaly_findings

- confidence_assessments

- evidence_items



Tests:



- provider shortage

- shared cash shortage

- repeated amount

- velocity spike

- delayed feed

- missing feed

- deterministic output

- confidence reduction

- PostgreSQL persistence



Update docs as per previous prompt i said you in details & saave prompt

 



Stop.

Do not implement alerts or APIs.
````

## In Scope
- Deterministic provider-scoped anomaly detection and five-part evidence fingerprint
- Feed-quality-aware signal confidence and deterministic core signal fusion
- Advisory recommendations without financial execution or fraud declarations
- PostgreSQL persistence through existing anomaly, confidence, and evidence tables
- Unit, safety, metric, rollback, and Neon PostgreSQL tests
- Documentation and prompt traceability updates

## Out of Scope
- Alerts
- Public APIs
- LLM decisions or explanations
- Fraud declarations
- Transfers, refills, blocking, or other financial actions

## Files Read
- Root problem statement and backend configuration
- Requirements, architecture, database, testing, traceability, implementation-status, implementation-plan, task-board, and prior prompt records
- Existing liquidity, scenario, validation, persistence, model, migration, and test modules

## Files Changed
- `backend/app/anomaly/`
- `backend/app/confidence/`
- `backend/tests/unit/test_anomaly_detection.py`
- `backend/tests/unit/test_confidence_engine.py`
- `backend/tests/unit/test_core_intelligence_metrics.py`
- `backend/tests/unit/test_core_intelligence_safety.py`
- `backend/tests/integration/test_core_intelligence_persistence_postgres.py`
- `README.md`
- `docs/08-testing-and-metrics.md`
- `docs/10-data-and-simulation.md`
- `docs/11-requirement-traceability.md`
- `docs/14-implementation-status.md`
- `docs/17-implementation-plan.md`
- `docs/18-task-board.md`
- `docs/commit-ledger.md`
- `prompts/history/PROMPT-0015-core-intelligence.md`

## Checks Run
- Combined liquidity, anomaly, confidence, and Neon PostgreSQL suite: `47 passed`; module coverage `96.16%`
- Full backend unit suite: `81 passed`
- Core-intelligence Neon persistence and rollback suite: `4 passed`
- New unit, metric, and safety suite: `18 passed`
- Governance suite: `18 passed`
- Ruff format and lint passed; strict MyPy passed for `88` source files; compilation passed
- Prompt-record and requirement-ID validators passed
- Controlled four-fixture anomaly precision `1.0000`, recall `1.0000`, false-positive rate `0.0000`
- Deterministic anomaly-plus-confidence latency average `0.1542 ms`, p95 `0.3454 ms` over 250 runs

## Sonar Status
- Pending remote run

## Audit Status
- Pending remote run

## Final Outcome
Implemented and locally verified. No alerts, public APIs, LLM decisions, fraud declarations, or financial actions were added.
