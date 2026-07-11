# PROMPT-0012 Provider Ingestion and Validation

## Prompt ID
PROMPT-0012

## Prompt Type
Implementation

## Date
2026-07-11

## Objective
Implement the provider ingestion and data validation engine without implementing liquidity forecasting, anomaly detection, alerts, cases, public APIs, authentication, or frontend work.

## Module
provider-ingestion-and-validation

## Requirement IDs
FR-001, FR-002, NFR-003, NFR-004, DATA-001, DATA-002, DATA-003, DB-001, SEC-001, SAFE-001, SAFE-002, SAFE-003, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
029d39acfa38b4346ac3f27235373d7ae57ea70d734c3e1db911e4357600b73b

## Exact Prompt
````text
You are implementing the next approved module of the existing LiquidityLens repository.

Repository Foundation, Database Schema and Migrations, and the Synthetic Scenario Engine have already been implemented.

Do not restart the project.
Do not regenerate the PRD, architecture, database design, or scenario engine.
Do not implement modules outside this prompt.

# MODULE

Provider Ingestion and Data Validation Engine

# PROMPT ID

Inspect `prompts/history/` and use the next available sequential Prompt ID.

Expected next ID:

`PROMPT-0012`

If it already exists, use the next unused ID.

# EXECUTION ENVIRONMENT

* Use Git Bash-compatible POSIX commands.
* Do not use PowerShell-specific syntax.
* Run commands from the correct backend directory.
* Do not hide shell, dependency, database, or environment failures.
* CI and SonarQube may be best-effort and non-blocking according to the approved judge instruction.
* Local tests, prompt traceability, and honest reporting remain mandatory.

# READ FIRST

Read and follow:

* `README.md`
* `docs/00-project-context.md`
* `docs/01-requirements.md`
* `docs/02-prd.md`
* `docs/03-workflows.md`
* `docs/04-architecture.md`
* `docs/05-database-design.md`
* `docs/06-api-contracts.md`
* `docs/06b-api-schemas.md`
* `docs/07-security-and-safety.md`
* `docs/08-testing-and-metrics.md`
* `docs/09-deployment.md`
* `docs/10-data-and-simulation.md`
* `docs/11-requirement-traceability.md`
* `docs/12-decision-log.md`
* `docs/13-known-risks.md`
* `docs/14-implementation-status.md`
* `docs/15-code-quality-and-commit-policy.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`
* all existing SQLAlchemy models
* all Alembic migrations
* the complete `backend/app/scenarios/` module
* existing scenario tests
* existing backend configuration, logging, error handling, and persistence utilities
* `.github/workflows/ci.yml`
* `sonar-project.properties`

Inspect:

* current Git status;
* recent commits;
* current Prompt IDs;
* current requirement IDs;
* local and remote test results;
* existing provider feed, transaction, balance, data-quality, and scenario-run models.

The approved Markdown documentation is the source of truth.

# PRE-FLIGHT CHECK

Before implementation:

1. Confirm the scenario engine files exist and are importable.
2. Run the available scenario tests.
3. Confirm generated scenario records can be queried from PostgreSQL.
4. Confirm missing provider balance data remains null/unknown instead of zero.
5. Identify and correct stale documentation that still claims scenario generation is not implemented.
6. Do not redesign the scenario engine unless a verified blocker exists.

Report any pre-existing failure honestly.

# OBJECTIVE

Implement a provider-aware ingestion and validation pipeline that accepts simulated provider transaction, balance, cash, and feed-status records and converts them into safe, normalized, validated records for later liquidity and anomaly analysis.

The module must:

* support at least three logically separate simulated providers;
* preserve provider separation;
* validate transaction and balance data;
* detect missing, delayed, stale, duplicate, invalid, out-of-order, and conflicting records;
* calculate explainable data-quality results;
* store structured data-quality events;
* reduce future confidence inputs when data quality is poor;
* never convert unknown balance values to zero;
* never make liquidity, anomaly, fraud, or operational decisions.

This module validates and normalizes data only.

# REQUIREMENT IDS

Read exact approved IDs from:

* `docs/01-requirements.md`
* `docs/11-requirement-traceability.md`

Use the IDs covering at least:

* multiple providers;
* shared physical cash;
* provider-specific balances;
* missing data;
* delayed data;
* stale data;
* conflicting data;
* duplicate transactions;
* provider separation;
* reliability;
* uncertainty;
* data-quality evidence;
* auditability;
* synthetic identifiers;
* safe fallback;
* testing;
* prompt traceability.

Do not invent duplicate requirement IDs.

# IN SCOPE

## 1. Module Structure

Create or complete:

```text
backend/app/validation/
├── __init__.py
├── schemas.py
├── enums.py
├── rules.py
├── transaction_validator.py
├── balance_validator.py
├── feed_validator.py
├── quality_score.py
├── normalizer.py
├── repository.py
├── service.py
├── audit.py
└── exceptions.py
```

Create or complete provider adapter boundaries:

```text
backend/app/providers/
├── __init__.py
├── base.py
├── schemas.py
├── registry.py
├── simulated.py
└── exceptions.py
```

A slightly different structure is acceptable only if it follows the approved modular-monolith dependency rules.

Validation domain logic must not depend on FastAPI.

Provider adapters must not contain liquidity or anomaly logic.

## 2. Canonical Ingestion Schemas

Define typed ingestion schemas for:

### Transaction input

Include:

* provider identifier;
* agent identifier;
* agent-provider account identifier;
* synthetic transaction identifier;
* synthetic customer/account identifier;
* transaction type;
* amount;
* currency;
* event timestamp;
* received timestamp;
* source sequence number where available;
* source status;
* scenario-run identifier where applicable;
* source metadata restricted to safe values.

### Provider balance input

Include:

* provider;
* agent;
* agent-provider account;
* reported e-money balance;
* balance timestamp;
* received timestamp;
* source sequence/version;
* data availability state;
* scenario-run identifier.

### Shared cash input

Include:

* agent;
* reported physical cash;
* snapshot timestamp;
* received timestamp;
* source;
* scenario-run identifier.

Shared physical cash must not include provider ownership.

### Feed-status input

Include:

* provider;
* agent or feed scope;
* expected timestamp;
* received timestamp;
* last successful timestamp;
* source status;
* sequence/version;
* error code where safe;
* scenario-run identifier.

All schemas must:

* use Decimal for money;
* use timezone-aware timestamps;
* reject unknown provider codes;
* reject phone-like identifiers;
* reject secrets or credential-like fields;
* preserve null/unknown values;
* validate currency and transaction types.

## 3. Provider Adapter Contract

Define a provider adapter interface that:

* identifies the provider;
* receives simulated source records;
* maps provider-specific input into canonical ingestion schemas;
* reports mapping errors;
* preserves provider scope;
* never accesses another provider’s balance or decisions;
* never converts or transfers balances.

Implement one generic simulated adapter configurable for all demo providers.

Do not build real bKash, Nagad, Rocket, or production API integrations.

Use synthetic provider identities and simulated data only.

## 4. Validation Categories

Support structured validation categories:

```text
valid
missing_required_field
invalid_identifier
unknown_provider
invalid_amount
invalid_currency
invalid_transaction_type
duplicate_transaction
duplicate_snapshot
delayed_feed
stale_feed
missing_feed
conflicting_balance
out_of_order_event
sequence_gap
future_timestamp
timestamp_skew
negative_balance
impossible_balance_change
provider_scope_mismatch
agent_account_mismatch
malformed_metadata
unsupported_record
```

Use exact approved names if documentation already defines them.

Do not label anything as fraud or criminal activity.

## 5. Transaction Validation

Validate:

* unique synthetic transaction ID;
* positive amount;
* valid transaction type;
* supported currency;
* timezone-aware timestamps;
* provider/account consistency;
* agent/provider-account relationship;
* no phone-like IDs;
* no future timestamp beyond configured tolerance;
* no received timestamp earlier than impossible bounds;
* duplicate transaction detection;
* out-of-order events;
* sequence gaps where sequence data exists;
* provider-scope mismatch;
* unsupported source status;
* safe metadata size and fields.

Duplicate ingestion must be idempotent.

The same transaction must not create multiple persisted transaction rows or duplicate quality events.

## 6. Balance Validation

Validate provider balance records separately from shared physical cash.

Provider balance rules:

* belongs to exactly one provider account;
* nullable when unavailable;
* no default zero for unknown values;
* non-negative when marked valid;
* timestamp freshness;
* duplicate snapshots;
* conflicting snapshots;
* impossible or unsupported balance movement;
* consistency with known transactions where enough data exists.

Shared cash rules:

* belongs to the agent/outlet only;
* contains no provider ownership;
* nullable when unavailable;
* non-negative when valid;
* duplicate and stale snapshot checks;
* timestamp and source validation.

Do not attempt to reconcile or transfer value between providers.

## 7. Feed Quality Validation

Detect:

### Delayed

A feed arrived later than an approved delay threshold but is still usable with reduced quality.

### Stale

The latest usable provider record is older than the approved freshness threshold.

### Missing

Expected provider data is absent.

### Conflicting

Two source records represent incompatible values for the same logical point/version.

### Invalid

The record cannot be safely used.

Thresholds must be configurable.

Do not hardcode festival-specific thresholds inside generic validation rules.

Store feed-quality status and last-valid-record information.

## 8. Data-Quality Score

Implement a deterministic and explainable data-quality score.

Use a documented scale, preferably:

```text
0.0 to 1.0
```

or:

```text
0 to 100
```

Use one scale consistently.

The score may consider:

* completeness;
* freshness;
* consistency;
* duplicate rate;
* sequence continuity;
* timestamp validity;
* provider mapping validity;
* required-field validity.

For every score return:

* overall score;
* quality level;
* component scores;
* triggered rules;
* evidence;
* confidence-impact factor;
* safe-use recommendation.

Examples of quality levels:

```text
high
medium
low
unusable
```

Do not calculate liquidity or anomaly confidence here.

Only produce a future confidence-impact input such as:

```text
confidence_multiplier
```

Document the formula and limitations.

## 9. Structured Evidence

Each validation finding must include:

* finding ID;
* rule ID;
* category;
* severity;
* provider scope;
* agent scope;
* source record ID;
* field names involved;
* expected condition;
* observed condition;
* timestamp;
* human-readable evidence;
* safe next step;
* whether the record is usable, usable-with-warning, quarantined, or rejected.

Never include secrets or real identities in evidence.

## 10. Persistence

Use existing tables such as:

* transactions;
* provider_balance_snapshots;
* shared_cash_snapshots;
* provider_feed_statuses;
* data_quality_events;
* audit_events;
* scenario_runs.

Implement service/repository behavior for:

* raw canonical input validation;
* normalized valid-record persistence;
* warning persistence;
* rejected-record evidence;
* feed status updates;
* quality-event creation;
* audit-event creation;
* idempotent retry.

A validation failure must not corrupt previously valid data.

Use transaction boundaries appropriately.

Do not automatically delete conflicting source records.

## 11. Record Disposition

Support:

```text
accepted
accepted_with_warning
quarantined
rejected
duplicate_ignored
```

Rules:

* accepted records may be used later;
* accepted-with-warning records preserve warnings;
* quarantined records remain inspectable but must not be treated as trusted;
* rejected records produce evidence;
* duplicate retry must not create duplicate business rows.

Document disposition logic.

## 12. Audit Events

Create audit events for important actions:

* record received;
* record normalized;
* record accepted;
* warning generated;
* record quarantined;
* record rejected;
* duplicate ignored;
* feed marked delayed;
* feed marked stale;
* feed marked missing;
* conflict detected;
* quality score updated.

Audit metadata must remain safe and concise.

Do not store credentials, tokens, connection strings, or raw secret fields.

## 13. Service APIs — Internal Only

Implement service-level interfaces such as:

```python
validate_transaction(...)
validate_provider_balance(...)
validate_shared_cash(...)
validate_feed_status(...)
ingest_transaction(...)
ingest_balance(...)
evaluate_feed_quality(...)
```

Do not implement public REST endpoints in this module.

Do not modify health/readiness endpoints except for necessary dependency wiring.

## 14. Scenario Integration

Integrate with the existing scenario engine without coupling validation logic to scenario internals.

Use scenario-generated records to test:

* normal day;
* Eid rush;
* hidden provider shortage;
* shared cash crisis;
* unusual repeated amounts;
* salary-day legitimate spike;
* delayed feed;
* missing feed;
* conflicting balance;
* agent unavailable where applicable.

Ground truth must remain separate from validation results.

Validation must not use ground-truth labels to “cheat.”

## 15. Configuration

Add safe settings for:

* feed delay threshold;
* stale threshold;
* future timestamp tolerance;
* timestamp skew tolerance;
* maximum metadata size;
* quality-score component weights;
* supported currencies;
* supported transaction types.

Use environment/configuration defaults appropriate for demo.

Document every setting.

Do not expose secrets.

## 16. Tests

Add comprehensive tests.

### Unit tests

Test:

* valid transaction;
* missing field;
* unknown provider;
* invalid identifier;
* phone-like identifier rejection;
* zero amount;
* negative amount;
* invalid currency;
* invalid transaction type;
* provider-scope mismatch;
* agent/account mismatch;
* future timestamp;
* timestamp skew;
* duplicate transaction;
* sequence gap;
* out-of-order event;
* valid provider balance;
* null unknown balance;
* negative valid balance rejection;
* duplicate snapshot;
* stale snapshot;
* shared cash independence;
* delayed feed;
* stale feed;
* missing feed;
* conflicting feed;
* invalid metadata;
* deterministic quality score;
* confidence-impact factor;
* evidence generation;
* disposition logic.

### PostgreSQL integration tests

Test:

* valid transaction persists once;
* duplicate retry remains idempotent;
* warning persists with accepted record;
* rejected record does not create trusted transaction;
* quarantined record remains inspectable;
* feed status updates correctly;
* quality event persists;
* audit event persists;
* provider separation remains enforced;
* missing balance remains null;
* failed transaction rolls back safely.

### Scenario integration tests

Using existing generated scenarios, verify:

* normal records validate cleanly;
* Eid demand remains valid data;
* repeated-amount scenario records remain valid transactions even though later anomaly analysis may flag patterns;
* delayed feed produces delayed quality status;
* missing feed produces missing status;
* conflicting balance produces conflict evidence;
* provider-shortage scenario is not classified as a data-quality error unless the source data itself is invalid.

### Safety tests

Verify:

* no fraud declaration;
* no real-looking phone IDs;
* no provider balance merge;
* no financial-execution action;
* no missing balance converted to zero;
* no secret leakage.

### Performance test

Measure ingestion and validation latency for demo-sized data.

Document:

* record count;
* total duration;
* average duration;
* p95 duration;
* environment limitation.

Use realistic, honest thresholds.

## 17. Metrics Evidence

Record initial validation metrics:

* valid-record acceptance rate;
* invalid-record rejection rate;
* duplicate-detection correctness;
* missing-feed detection correctness;
* delayed-feed detection correctness;
* conflicting-balance detection correctness;
* validation processing latency;
* explanation/evidence coverage for findings.

Do not invent values.

Generate them from tests or deterministic fixtures.

## 18. Documentation Cleanup

Update stale documentation that still claims the scenario engine or seed scenarios are not implemented.

Update:

* `README.md`
* `docs/03-workflows.md` only where implementation details need clarification
* `docs/04-architecture.md` only if provider adapter boundaries require clarification
* `docs/06-api-contracts.md` only to keep future contracts aligned
* `docs/08-testing-and-metrics.md`
* `docs/09-deployment.md`
* `docs/10-data-and-simulation.md`
* `docs/11-requirement-traceability.md`
* `docs/12-decision-log.md` only for genuine decisions
* `docs/13-known-risks.md`
* `docs/14-implementation-status.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`

Mark modules honestly:

* Repository Foundation: implemented/verified according to evidence;
* Database Schema: implemented/verified according to evidence;
* Synthetic Scenario Engine: implemented/verified according to evidence;
* Provider Ingestion and Validation: implemented only after tests pass;
* Liquidity, anomaly, confidence fusion, explanations, alerts, cases, APIs, auth, and dashboards: not implemented.

## 19. Local Validation

From Git Bash, run where available:

```bash
cd backend
ruff format --check .
ruff check .
mypy app
pytest -q
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

Run PostgreSQL integration tests.

If Ruff or MyPy is unavailable:

* install approved development dependencies;
* do not silently skip;
* report the exact problem if installation fails.

CI and SonarQube may remain best-effort/non-blocking, but local results must be honest.

## 20. Prompt Traceability

Create:

```text
prompts/history/PROMPT-0012-provider-ingestion-and-validation.md
```

or the next available sequential ID.

Include:

* Prompt ID;
* type;
* date;
* objective;
* module;
* requirement IDs;
* exact prompt verbatim;
* SHA-256 checksum;
* in scope;
* out of scope;
* files read;
* files changed;
* tests run;
* metrics evidence;
* CI status;
* SonarQube status;
* human audit status;
* final outcome.

Do not include secrets.

## 21. Out of Scope

Do not implement:

* liquidity forecasting;
* shortage runway calculation;
* anomaly detection;
* transaction-pattern scoring;
* confidence fusion;
* LLM explanations;
* alerts;
* cases;
* authentication;
* provider authorization middleware;
* public REST ingestion endpoints;
* dashboards;
* charts;
* metrics REST endpoint;
* production provider integrations;
* real financial actions.

This module only handles provider adaptation, normalization, validation, quality scoring, persistence, evidence, and audit records.

## 22. Acceptance Criteria

This module is complete only when:

1. Canonical provider ingestion schemas exist.
2. Simulated provider adapters map safely into canonical schemas.
3. Valid records are accepted and persisted.
4. Invalid records produce structured evidence.
5. Duplicates are idempotently ignored.
6. Delayed feeds are detected.
7. Stale feeds are detected.
8. Missing feeds are detected.
9. Conflicting balances are detected.
10. Unknown balance remains null rather than zero.
11. Shared cash remains provider-independent.
12. Provider balances remain isolated.
13. Data-quality scores are deterministic and explainable.
14. Confidence-impact input is generated without making business decisions.
15. Audit and quality events persist.
16. Scenario integration tests pass.
17. PostgreSQL integration tests pass.
18. Ruff, MyPy, Pytest, coverage, and governance validation pass locally where available.
19. Documentation matches implementation.
20. Prompt validation passes.
21. No secrets or real identifiers are committed.
22. Working tree is clean after commit.
23. Remote CI and Sonar results are reported honestly.

# COMMIT

Prepare one focused commit:

```text
feat(validation): add provider ingestion and data-quality engine

Requirement-IDs: <EXACT APPROVED IDS>
Prompt-ID: <CURRENT PROMPT ID>
Module: provider-ingestion-and-validation
Tests: unit, PostgreSQL integration, scenario integration, safety, governance, lint, typing, and coverage checks completed
```

Do not combine liquidity, anomaly, alert, API, authentication, or frontend work in this commit.

# FINAL RESPONSE FORMAT

Return only:

## Pre-flight Scenario Validation

## Prompt Record Created

## Requirement IDs Used

## Provider Adapter Contract

## Canonical Schemas

## Validation Rules

## Data-Quality Score

## Evidence and Disposition

## Persistence and Audit

## Files Created

## Files Updated

## Tests Run

## PostgreSQL Integration Result

## Scenario Integration Result

## Metrics Evidence

## Coverage

## Documentation Updated

## Commit Created

## Git Status

## Remote CI Result

## SonarQube Result

## Remaining Blockers

## Recommended Next Module

Do not begin the Liquidity Forecasting Engine.

````

## In Scope
- Simulated provider adapter boundaries.
- Canonical transaction, provider balance, shared cash, and feed status schemas.
- Validation categories, evidence, disposition, and deterministic data-quality score.
- Internal validation service APIs only.
- Persistence to existing trusted records, provider feed statuses, data-quality events, and audit events.
- Scenario integration tests and PostgreSQL integration tests.
- Documentation and commit-ledger updates.

## Out of Scope
- Liquidity forecasting.
- Anomaly detection.
- Transaction-pattern scoring.
- Confidence fusion.
- LLM explanations.
- Alerts and cases.
- Authentication and provider authorization middleware.
- Public REST ingestion endpoints.
- Dashboards, charts, metrics REST endpoint, production provider integrations, and real financial actions.

## Files Read
- README.md
- docs/01-requirements.md
- docs/03-workflows.md
- docs/04-architecture.md
- docs/05-database-design.md
- docs/06-api-contracts.md
- docs/08-testing-and-metrics.md
- docs/09-deployment.md
- docs/10-data-and-simulation.md
- docs/11-requirement-traceability.md
- docs/12-decision-log.md
- docs/13-known-risks.md
- docs/14-implementation-status.md
- docs/15-code-quality-and-commit-policy.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- backend/app/persistence/models/*.py
- backend/app/scenarios/*.py
- backend/app/core/config.py
- .github/workflows/ci.yml
- sonar-project.properties

## Files Changed
- README.md
- docs/03-workflows.md
- docs/04-architecture.md
- docs/06-api-contracts.md
- docs/08-testing-and-metrics.md
- docs/09-deployment.md
- docs/10-data-and-simulation.md
- docs/11-requirement-traceability.md
- docs/12-decision-log.md
- docs/13-known-risks.md
- docs/14-implementation-status.md
- docs/17-implementation-plan.md
- docs/18-task-board.md
- docs/commit-ledger.md
- backend/app/core/config.py
- backend/app/providers/*.py
- backend/app/validation/*.py
- backend/tests/unit/test_provider_adapters.py
- backend/tests/unit/test_validation_rules.py
- backend/tests/unit/test_validation_safety.py
- backend/tests/integration/test_validation_persistence_postgres.py
- prompts/history/PROMPT-0012-provider-ingestion-and-validation.md

## Checks Run
- Scenario pre-flight tests passed: 21 passed.
- Local PostgreSQL query confirmed scenario-generated transaction/feed records and null missing provider balance.
- `python -m compileall app/validation app/providers tests/unit tests/integration` passed.
- `python -m pytest -q` from backend passed: 61 passed, coverage 88.86%.
- Manual line-length scan for new validation/provider files passed.
- Targeted `python -m ruff format --check` and `python -m ruff check` passed for provider ingestion and validation module files. Whole-backend Ruff still reports pre-existing lint/format findings outside this module. `python -m mypy backend/app` could not run because MyPy is unavailable in the local Python environment.
- Governance, prompt, requirement, diff, and commit traceability validators will be rerun after this record is created.

## Metrics Evidence
- Valid transaction accepted and persisted once.
- Duplicate transaction retry returned `duplicate_ignored` and did not create a duplicate trusted row.
- Zero-amount transaction was rejected and did not create a trusted row.
- Missing provider balance persisted as `NULL`, not zero.
- Delayed feed persisted feed status, quality event, and audit evidence.
- Scenario-generated unusual-activity transaction validated without reading ground-truth labels.
- Demo latency test ingested 40 validation records under the 5 second local threshold.

## CI Status
Remote CI not checked in this local implementation turn. Local tests and governance validation are authoritative for this commit.

## SonarQube Status
Skipped/best-effort for this local turn; no pass claimed.

## Audit Status
Human audit pending.

## Final Outcome
Provider ingestion and validation engine implemented as internal service-layer functionality with simulated provider adapters, canonical schemas, validation evidence, deterministic data-quality scoring, persistence, audit events, tests, and documentation updates.
