# PROMPT-0012 Provider Ingestion and Validation Closeout

## Prompt ID
PROMPT-0012

## Prompt Type
Implementation Closeout

## Date
2026-07-11

## Objective
Complete, test, document, and trace the existing Provider Ingestion and Data Validation Engine implementation before starting liquidity forecasting.

## Module
provider-ingestion-and-validation

## Requirement IDs
FR-001, FR-002, NFR-003, NFR-004, DATA-001, DATA-002, DATA-003, DB-001, SEC-001, SAFE-001, SAFE-002, SAFE-003, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
8867f8474118648f056f9aa491486c85f0e4c002f1a1e8d535b20d2f4e1f50d5

## Exact Prompt
```text
You are closing the Provider Ingestion and Data Validation Engine module before starting liquidity forecasting.

Do not implement liquidity forecasting, anomaly detection, alerts, APIs, authentication, or frontend features.

## Objective

Complete, test, document, and trace the existing validation implementation.

## Required fixes

1. Create the next exact prompt record:

`prompts/history/PROMPT-0012-provider-ingestion-and-validation.md`

Store this exact prompt verbatim with its SHA-256 checksum and required metadata.

2. Add comprehensive validation unit tests covering:

* valid transaction
* zero and negative amount
* invalid currency
* unknown provider
* provider/account mismatch
* phone-like identifier rejection
* duplicate transaction
* true sequence-gap detection
* out-of-order event
* delayed feed
* stale feed
* missing feed
* conflicting balance
* unknown balance remaining null
* shared cash remaining provider-independent
* deterministic quality score
* disposition rules
* structured evidence

3. Add PostgreSQL integration tests covering:

* accepted transaction persists once
* duplicate retry is idempotent
* rejected record does not create a trusted transaction
* accepted-with-warning persists its warning
* quality events persist
* audit events persist
* missing balance remains null
* provider separation remains enforced
* failed ingestion rolls back

4. Implement true sequence-gap detection.

Compare the incoming sequence number with the latest known source sequence.

Do not classify only negative values as sequence gaps.

5. Separate shared-cash ingestion from provider-scoped adapters.

A provider adapter must map only provider-owned records:

* provider transaction
* provider balance
* provider feed status

Shared physical cash must enter through an agent/outlet or scenario-level canonical ingestion path.

Do not attach provider ownership to shared cash.

6. Review quality scoring.

* Keep the deterministic MVP approach.
* Document that it is a rule-based data-quality score, not calibrated model confidence.
* Ensure duplicate records do not misleadingly appear as fully clean trusted data.
* Keep the downstream confidence multiplier explicit and explainable.
* Do not add machine learning.

7. Update stale documentation:

* `README.md`
* `docs/08-testing-and-metrics.md`
* `docs/10-data-and-simulation.md`
* `docs/11-requirement-traceability.md`
* `docs/13-known-risks.md`
* `docs/14-implementation-status.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`

Mark honestly:

* Repository Foundation: Implemented
* Database Schema: Implemented or Verified according to evidence
* Synthetic Scenario Engine: Implemented
* Provider Ingestion and Validation: Implemented only after required tests pass
* Liquidity Engine and later modules: Not Started

8. Run from Git Bash:

```bash
cd backend
ruff format --check .
ruff check .
mypy app
pytest -q
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

Run PostgreSQL integration tests.

Do not silently skip missing dependencies or database failures.

9. Produce measured validation evidence:

* total validation tests
* acceptance/rejection correctness
* duplicate detection correctness
* missing-feed detection correctness
* delayed-feed detection correctness
* conflicting-balance detection correctness
* average and p95 validation latency
* coverage

Do not invent results.

10. Prepare one focused commit:

```text
fix(validation): complete data-quality verification and traceability

Requirement-IDs: <EXACT APPROVED IDS>
Prompt-ID: PROMPT-0012
Module: provider-ingestion-and-validation
Tests: validation unit, PostgreSQL integration, safety, lint, typing, coverage, and governance checks completed
```

## Acceptance criteria

This correction is complete only when:

* prompt record exists and validates
* validation unit tests exist and pass
* PostgreSQL integration tests exist and pass
* true sequence gaps are detected
* shared cash does not enter through a provider-owned adapter
* duplicates are idempotent
* unknown balance remains null
* provider boundaries remain enforced
* quality and audit events persist
* documentation matches code
* working tree is clean after commit
* remote CI and Sonar results are reported honestly

## Final response

Return only:

### Prompt Record

### Validation Tests

### PostgreSQL Tests

### Sequence-Gap Fix

### Shared-Cash Boundary Fix

### Quality-Score Clarification

### Metrics Evidence

### Documentation Updated

### Commit Created

### Git Status

### Remaining Blockers

### Ready for Liquidity Engine

End with exactly:

`YES`

or

`NO`
```

## In Scope
- Closeout corrections for provider ingestion and validation.
- Validation rule completion, PostgreSQL persistence tests, quality scoring clarification, prompt traceability, documentation updates, and local/remote validation evidence.

## Out of Scope
- Liquidity forecasting.
- Anomaly detection.
- Alerts, cases, APIs, authentication, and frontend features.
- Machine learning or calibrated model confidence.

## Files Read
- README.md
- docs/08-testing-and-metrics.md
- docs/10-data-and-simulation.md
- docs/11-requirement-traceability.md
- docs/13-known-risks.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- backend/app/providers/*
- backend/app/validation/*
- backend/app/persistence/models/*
- backend/tests/unit/test_validation_rules.py
- backend/tests/unit/test_provider_adapters.py
- backend/tests/integration/test_validation_persistence_postgres.py

## Files Changed
- backend/app/providers/*
- backend/app/validation/*
- backend/app/persistence/models/*
- backend/app/scenarios/feed_generator.py
- backend/app/api/routes/*
- backend/tests/unit/test_validation_rules.py
- backend/tests/unit/test_provider_adapters.py
- backend/tests/integration/test_validation_persistence_postgres.py
- README.md
- docs/08-testing-and-metrics.md
- docs/10-data-and-simulation.md
- docs/11-requirement-traceability.md
- docs/13-known-risks.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md

## Checks Run
- Git Bash `ruff format --check .`: passed.
- Git Bash `ruff check .`: passed.
- Git Bash `mypy app`: passed.
- Git Bash `pytest -q`: passed with `70 passed`.
- Git Bash `pytest --cov=app --cov-report=term-missing --cov-report=xml`: passed with `89.49%` coverage.
- PostgreSQL integration tests: passed against local `hacathon_db`.
- Prompt record validation: passed.
- Requirement ID validation: passed.
- Governance unit tests: passed.
- Git diff check: passed.

## Sonar Status
Pending remote CI/Sonar check after closeout commit.

## Audit Status
Local prompt, requirement, governance, and diff checks passed. Commit traceability and remote CI/Sonar audit remain pending until after the closeout commit is created and pushed.

## Final Outcome
Provider ingestion and validation closeout passed locally. Remote CI and SonarQube results must be reported honestly after push.
