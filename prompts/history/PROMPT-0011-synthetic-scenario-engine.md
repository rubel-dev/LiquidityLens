# PROMPT-0011 Synthetic Scenario Engine

## Prompt ID
PROMPT-0011

## Prompt Type
Implementation

## Date
2026-07-11

## Objective
Implement the deterministic synthetic scenario engine and seed data lifecycle without implementing provider ingestion, analytics, APIs, alerts, cases, or frontend dashboard work.

## Module
synthetic-scenario-engine

## Requirement IDs
FR-002, FR-009, FR-012, NFR-003, NFR-004, DATA-001, DATA-002, DATA-003, DB-001, SEC-001, SAFE-001, SAFE-002, SAFE-003, DEMO-002, DOC-001, DOC-002, DOC-003

## Exact Prompt SHA-256
df9a20f901c80ab89f4f9cc327a3ab79719624815b0729ea6f0f8f7dcc3a0d85

## Exact Prompt
````text
You are implementing the next approved module of the existing LiquidityLens repository.

Repository Foundation and Database Schema and Migrations have already been implemented.

The latest database commit is:

`63e131d feat(database): add domain schema and initial migration`

Do not restart the project.
Do not regenerate the PRD, architecture, or database design.
Do not implement modules outside this prompt.

# MODULE

Synthetic Scenario Engine and Deterministic Seed Data

# EXPECTED PROMPT ID

Use the next available sequential Prompt ID after the latest prompt record.

Inspect `prompts/history/` first.

Expected next ID is likely:

`PROMPT-0009`

Use the next unused sequential ID if that ID already exists.

# EXECUTION ENVIRONMENT

* Use Git Bash-compatible and POSIX-compatible commands.
* Do not rely on PowerShell-specific syntax.
* Frontend dependencies were successfully installed manually through Git Bash.
* If a command fails because of shell differences, report the exact command and error.
* Do not falsely classify a shell-specific failure as a product-code failure.
* Do not skip required verification silently.

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
* all existing backend persistence models
* all Alembic migrations
* current backend tests
* `.github/workflows/ci.yml`
* `sonar-project.properties`

Inspect recent Git history, current Git status, remote CI status, and SonarQube status before making changes.

The approved Markdown documentation is the source of truth.

# PRE-FLIGHT DATABASE VALIDATION

Before implementing scenario generation:

1. Confirm that the latest database migration passes in remote CI against PostgreSQL.
2. Run, where possible:

```bash
cd backend
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

3. Inspect the current migration implementation.

The current migration may use:

```python
Base.metadata.create_all(...)
Base.metadata.drop_all(...)
```

Evaluate whether this is safe and sufficiently deterministic for the committed Alembic migration.

If it creates migration-history, downgrade-order, enum, constraint, or future autogeneration risks:

* replace it with explicit Alembic operations or a properly generated deterministic migration;
* preserve the approved schema;
* do not redesign tables;
* add regression tests;
* document the correction;
* include it in this focused commit as a necessary pre-flight fix.

Do not proceed with scenario persistence if the schema cannot reliably migrate on PostgreSQL.

# OBJECTIVE

Implement a deterministic synthetic data and scenario engine that creates realistic, safe, reproducible multi-provider operational data for the LiquidityLens hackathon demo.

The module must support:

* multiple logically separate providers;
* agents serving more than one provider;
* shared physical cash;
* provider-specific e-money balances;
* cash-in and cash-out transactions;
* normal and stressed operating conditions;
* intentionally injected anomaly ground truth;
* missing, delayed, stale, and conflicting feed conditions;
* deterministic reset and replay;
* synthetic identifiers only.

This module creates data and scenario state.

It must not perform liquidity forecasting, anomaly detection, confidence scoring, alert creation, case management, LLM explanations, or frontend dashboard work.

# REQUIREMENT IDS

Read the exact IDs from:

* `docs/01-requirements.md`
* `docs/10-data-and-simulation.md`
* `docs/11-requirement-traceability.md`

Use the approved IDs covering at least:

* multi-provider simulation;
* shared physical cash;
* provider-specific balances;
* realistic synthetic data;
* synthetic identifiers;
* scenario reproducibility;
* anomaly ground truth;
* missing/delayed/conflicting data;
* provider separation;
* privacy and safety;
* demo reset/replay;
* prompt and commit traceability.

Do not invent duplicate or conflicting IDs.

# IN SCOPE

## 1. Module Structure

Create or complete:

```text
backend/app/scenarios/
├── __init__.py
├── catalog.py
├── schemas.py
├── random_source.py
├── generators.py
├── transaction_generator.py
├── balance_generator.py
├── feed_generator.py
├── ground_truth.py
├── service.py
├── repository.py
├── reset.py
└── exceptions.py
```

A slightly different grouping is acceptable if it follows the approved architecture and dependency rules.

Domain generation logic must not depend directly on FastAPI.

Use clear service and repository boundaries.

## 2. Canonical Scenario Catalog

Implement these canonical scenarios:

### Scenario A — Normal Day

Purpose:

* stable demand;
* normal transaction velocity;
* balanced provider activity;
* sufficient shared cash;
* no injected anomaly;
* high data completeness.

Expected ground truth:

* no shortage intentionally injected;
* no additional review recommended.

### Scenario B — Eid Rush

Purpose:

* legitimate high demand;
* increased cash-out velocity;
* broad account distribution;
* seasonal event context;
* possible liquidity pressure without automatically treating activity as suspicious.

Expected ground truth:

* legitimate operational demand spike;
* useful for false-positive evaluation.

### Scenario C — Hidden Provider Shortage

Purpose:

* total outlet value appears healthy;
* one provider-specific e-money balance approaches depletion;
* other provider balances remain healthy;
* shared cash may still appear sufficient.

Expected ground truth:

* provider-specific shortage pressure;
* no balance merging or cross-provider transfer.

### Scenario D — Shared Cash Crisis

Purpose:

* cash-out demand across one or more providers reduces shared physical cash;
* provider balances may remain available;
* physical cash is the limiting resource.

Expected ground truth:

* shared-cash shortage pressure.

### Scenario E — Liquidity Pressure with Unusual Activity

Purpose:

* rapid cash-out increase;
* repeated or near-identical transaction amounts;
* concentrated activity from a small synthetic account group;
* provider-specific pressure.

Expected ground truth:

* intentionally injected unusual pattern;
* requires human review;
* not proof of fraud.

### Scenario F — Salary-Day Legitimate Spike

Purpose:

* high but legitimate demand;
* broad account diversity;
* recognizable time/event context;
* tests false-positive handling.

Expected ground truth:

* consistent with expected demand;
* no additional review currently recommended.

### Scenario G — Delayed Feed

Purpose:

* one provider feed timestamp becomes delayed;
* underlying balance is not treated as current.

Expected ground truth:

* reduced data quality and future confidence.

### Scenario H — Missing Feed

Purpose:

* one provider feed is unavailable;
* missing provider balance remains unknown, not zero.

Expected ground truth:

* safe fallback required.

### Scenario I — Conflicting Balance

Purpose:

* provider transaction totals and reported balance disagree;
* inconsistency is intentional.

Expected ground truth:

* data-quality issue requiring review before confident recommendation.

### Scenario J — Agent Unavailable

Purpose:

* agent/outlet operational availability changes;
* future coordination modules can use this scenario.

Expected ground truth:

* service continuity risk;
* no automatic reassignment in this module.

# 3. Deterministic Randomness

Every scenario run must accept or generate a stored random seed.

Requirements:

* same scenario definition;
* same seed;
* same configured start time;
* same generator version;

must produce the same generated dataset.

Do not depend on the machine's current local time inside deterministic generation.

Use an explicit scenario start timestamp.

Persist:

* scenario ID;
* scenario version;
* random seed;
* start timestamp;
* generation configuration;
* run status;
* generated record counts;
* checksum or deterministic dataset fingerprint;
* ground-truth summary.

# 4. Synthetic Identifier Policy

Use clearly synthetic identifiers such as:

```text
SIM-USER-0001
SIM-AGENT-0001
SIM-CUST-0001
SIM-TXN-000001
SIM-PROVIDER-BK
SIM-PROVIDER-NG
SIM-PROVIDER-RK
SIM-SCENARIO-001
SIM-RUN-000001
```

Never generate:

* `017...`
* `018...`
* `019...`
* phone-number-like identifiers;
* real names;
* real NIDs;
* real wallet IDs;
* PINs;
* OTPs;
* passwords;
* credentials.

Add automated validation that rejects phone-number-like synthetic identifiers.

# 5. Provider Separation

Create at least three logically separate synthetic provider contexts for the demo.

They may use approved demonstration labels, but must remain synthetic and independent.

Rules:

* each provider has separate e-money balances;
* provider-specific transactions remain provider-scoped;
* one provider's balance must never satisfy another provider's transaction;
* shared cash belongs to the agent/outlet, not a provider;
* scenario generation must never simulate unauthorized provider-to-provider conversion;
* no transfer, settlement, refill execution, recovery, reversal, blocking, or freezing.

# 6. Money and Balance Consistency

Use Decimal values.

For every generated transaction:

* amount must be positive;
* currency must be explicit where required;
* transaction type must be valid;
* provider account must match provider scope;
* timestamps must be timezone-aware;
* transaction IDs must be unique.

Model cash movement consistently.

Document and test the accounting convention for:

* cash-in;
* cash-out;
* provider e-money increase/decrease;
* shared physical cash increase/decrease.

Do not silently allow negative balances unless a scenario explicitly models invalid/conflicting source data.

Invalid source-data scenarios must be clearly marked as data-quality ground truth rather than valid financial state.

# 7. Ground-Truth Labels

Persist machine-readable ground truth for each scenario run.

Ground-truth categories must include at least:

```text
normal
legitimate_demand_spike
provider_liquidity_pressure
shared_cash_pressure
unusual_repeated_amounts
unusual_velocity
account_concentration
delayed_feed
missing_feed
stale_feed
conflicting_balance
agent_unavailable
```

For each injected event store:

* category;
* provider scope if applicable;
* agent scope;
* start time;
* end time;
* affected transaction IDs where practical;
* expected review boundary;
* whether it is intended to count as an anomaly-positive case;
* whether it is intended to count as a normal/false-positive test case.

Do not use ground-truth labels that declare fraud or wrongdoing.

# 8. Scenario Persistence

Use the approved persistence models.

Implement repositories/services to:

* list canonical scenario definitions;
* create a scenario run;
* generate records;
* persist generated records transactionally;
* store run metadata;
* store ground truth;
* complete the run;
* fail the run safely;
* reset a run;
* replay a run.

A failed generation must not leave a partially committed active run.

Use an appropriate database transaction boundary.

Do not expose HTTP endpoints yet unless an existing approved plan explicitly requires internal-only endpoints in this module.

Prefer service-level implementation and CLI commands first.

# 9. CLI Commands

Create safe developer/demo commands.

Examples:

```bash
cd backend
python -m app.scenarios.cli list
python -m app.scenarios.cli run normal_day --seed 1001
python -m app.scenarios.cli run eid_rush --seed 2001
python -m app.scenarios.cli reset --run-id SIM-RUN-000001
python -m app.scenarios.cli replay --run-id SIM-RUN-000001
```

Exact syntax may differ, but must support:

* list;
* run;
* reset;
* replay;
* optional seed;
* optional explicit start timestamp.

Commands must:

* print a concise result summary;
* return non-zero status on failure;
* never expose secrets;
* not modify unrelated scenario runs.

# 10. Reset and Replay

Reset must remove or archive only data owned by the selected scenario run.

Do not truncate unrelated manually created or other-run records.

Replay must:

* use the original seed;
* use the original scenario version;
* use the original start timestamp;
* produce the same deterministic dataset fingerprint.

If replay cannot reproduce due to a version mismatch, fail clearly rather than silently generating different data.

# 11. Idempotency and Duplicate Prevention

Implement protections against:

* running the same requested run ID twice;
* duplicate transaction IDs;
* duplicate generated records after retry;
* replay accumulating duplicate data;
* concurrent reset/replay of the same run.

Use database constraints and service-level checks.

Do not implement distributed locks or Redis.

# 12. Data Volume Profiles

Support configurable demo-sized profiles:

```text
small
medium
demo
```

Recommended targets:

* small: fast unit/integration tests;
* medium: analytics validation;
* demo: smooth live presentation.

Do not create unnecessarily large datasets.

Record actual generated counts.

# 13. Versioning

Add a scenario generator version.

Persist:

* scenario definition version;
* generator version;
* rule/catalog version.

Changing generation behavior must require an explicit version change.

Document this in the decision log only if it introduces a new architectural decision.

# 14. Tests

Add comprehensive tests.

## Unit Tests

Test:

* deterministic output for same seed;
* different output for different seed;
* stable output for explicit start time;
* valid identifier format;
* phone-number-like identifier rejection;
* provider separation;
* shared cash independence;
* positive valid transaction amounts;
* timezone-aware timestamps;
* unique transaction IDs;
* event context generation;
* ground-truth labels;
* legitimate Eid spike label;
* salary-day false-positive label;
* repeated-amount injection;
* velocity injection;
* concentrated-account injection;
* delayed feed generation;
* missing feed generation;
* conflicting balance generation;
* generator version behavior.

## PostgreSQL Integration Tests

Test:

* scenario run transaction commits completely;
* failed run rolls back;
* generated providers, agents, balances, transactions, and feed statuses persist;
* reset affects only selected run-owned data;
* replay reproduces the same fingerprint;
* duplicate run ID is rejected;
* duplicate transaction ID is rejected;
* nullable/unknown missing balance remains null;
* provider account relationships remain isolated.

## Safety Tests

Test repository-wide generated and fixture data for:

* no phone-number-like identifiers;
* no real-looking credentials;
* no fraud-declaration labels;
* no financial-execution action;
* no provider balance merging.

## Performance Test

For the demo profile, measure and document scenario generation time.

Keep the threshold realistic for the demonstrated environment.

# 15. Coverage

Maintain meaningful coverage.

Do not add meaningless tests only to satisfy the threshold.

Ensure scenario module branches are covered, especially:

* success;
* failure;
* reset;
* replay;
* invalid configuration;
* missing provider;
* duplicate ID;
* rollback.

# 16. Documentation Updates

Update:

* `README.md`
* `docs/03-workflows.md` only if implementation details clarify approved workflows
* `docs/08-testing-and-metrics.md`
* `docs/09-deployment.md`
* `docs/10-data-and-simulation.md`
* `docs/11-requirement-traceability.md`
* `docs/12-decision-log.md` only for genuine new decisions
* `docs/13-known-risks.md`
* `docs/14-implementation-status.md`
* `docs/17-implementation-plan.md`
* `docs/18-task-board.md`
* `docs/commit-ledger.md`

Documentation must include:

* scenario catalog;
* seed policy;
* ground-truth policy;
* accounting convention;
* reset/replay behavior;
* CLI commands;
* performance evidence;
* known limitations.

Mark:

* Repository Foundation: Implemented/Verified only according to evidence;
* Database Schema and Migrations: Implemented/Verified only according to CI and PostgreSQL evidence;
* Synthetic Scenario Engine: Implemented only after all required tests pass.

Do not mark validation engine, liquidity engine, anomaly engine, alerts, cases, APIs, auth, or dashboards complete.

# 17. CI and SonarQube

Keep all governance checks.

Ensure CI runs:

* Ruff format;
* Ruff lint;
* MyPy;
* unit tests;
* PostgreSQL scenario integration tests;
* coverage;
* frontend checks;
* governance validation;
* SonarQube analysis;
* Quality Gate.

Do not weaken checks.

Do not claim remote SonarQube success until GitHub Actions confirms it.

# 18. Prompt Traceability

Create:

```text
prompts/history/PROMPT-0009-synthetic-scenario-engine.md
```

or the next unused sequential Prompt ID.

Include:

* Prompt ID;
* prompt type;
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
* generated scenario evidence;
* SonarQube status;
* human audit status;
* final outcome.

Do not include secrets.

# 19. Out of Scope

Do not implement:

* provider ingestion APIs;
* validation engine decisions;
* liquidity forecasting;
* anomaly detection algorithms;
* confidence fusion;
* LLM calls;
* explanation generation;
* alert creation;
* case management;
* authentication;
* provider authorization;
* public scenario REST endpoints;
* dashboards;
* charts;
* metrics API;
* production cloud deployment.

This module only creates safe, deterministic scenario data and lifecycle controls.

# 20. Acceptance Criteria

This module is complete only when:

1. All canonical scenarios are implemented.
2. Same seed and start time produce identical output.
3. Replay produces the same dataset fingerprint.
4. Reset affects only the selected scenario run.
5. Synthetic identifiers never resemble phone numbers.
6. Shared cash remains provider-independent.
7. Provider balances remain separate.
8. Missing balances remain unknown instead of zero.
9. Ground-truth labels are persisted.
10. Legitimate Eid/salary scenarios are distinguishable from injected anomaly-positive scenarios.
11. Failed generation rolls back.
12. PostgreSQL integration tests pass.
13. Ruff, MyPy, Pytest, coverage, and governance checks pass.
14. Documentation matches implemented behavior.
15. Prompt validation passes.
16. Working tree is clean after commit.
17. Remote CI/Sonar status is reported honestly.

# 21. Commit

Prepare one focused commit:

```text
feat(scenarios): add deterministic synthetic scenario engine

Requirement-IDs: <EXACT APPROVED IDS>
Prompt-ID: <CURRENT PROMPT ID>
Module: synthetic-scenario-engine
Tests: deterministic generation, PostgreSQL persistence, rollback, reset, replay, safety, governance, and coverage checks passed
```

Do not combine validation, forecasting, anomaly detection, APIs, or UI work in this commit.

# FINAL RESPONSE FORMAT

Return only:

## Pre-flight Database Validation

## Prompt Record Created

## Requirement IDs Used

## Scenario Catalog

## Synthetic Identifier Policy

## Ground Truth

## Reset and Replay

## Files Created

## Files Updated

## Tests Run

## PostgreSQL Integration Result

## Determinism Evidence

## Performance Evidence

## Coverage

## Documentation Updated

## Commit Created

## Git Status

## Remote CI Result

## SonarQube Result

## Quality Gate Result

## Remaining Blockers

## Recommended Next Module

Do not begin Provider Ingestion and Data Validation.

````

## In Scope
- Canonical scenario catalog A through J.
- Deterministic generator version, catalog version, seed, explicit start timestamp, profiles, counts, and fingerprints.
- Synthetic identifier validation and phone-number-like rejection.
- Provider-separated e-money balances and agent-scoped shared cash.
- Cash-in/cash-out accounting convention.
- Missing, delayed, stale, and conflicting feed conditions.
- Machine-readable audit-backed ground truth.
- Internal CLI commands for list, run, reset, and replay.
- Local PostgreSQL persistence tests, reset/replay tests, safety tests, and documentation updates.

## Out of Scope
- Provider ingestion APIs.
- Validation engine decisions.
- Liquidity forecasting.
- Anomaly detection algorithms.
- Confidence fusion.
- LLM calls or explanation generation.
- Alert creation.
- Case management.
- Authentication and authorization.
- Public REST endpoints.
- Dashboards, charts, metrics APIs, and production deployment.

## Files Read
- README.md
- docs/01-requirements.md
- docs/03-workflows.md
- docs/05-database-design.md
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
- backend/app/persistence/models/*.py
- backend/alembic/versions/20260711_0001_initial_domain_schema.py
- backend/tests/unit/*.py
- backend/tests/integration/*.py
- .github/workflows/ci.yml
- sonar-project.properties

## Files Changed
- README.md
- docs/03-workflows.md
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
- backend/app/scenarios/*.py
- backend/tests/unit/test_scenario_generation.py
- backend/tests/unit/test_scenario_safety.py
- backend/tests/integration/test_scenario_persistence_postgres.py
- prompts/history/PROMPT-0011-synthetic-scenario-engine.md

## Checks Run
- Git Bash check failed with `CreateFileMapping ... Win32 error 5`; PowerShell fallback used.
- Local Alembic cycle against PostgreSQL `hacathon_db`: upgrade, downgrade, upgrade passed.
- `python -m compileall app tests` passed from backend.
- `python -m pytest -q` passed from backend: 39 passed, coverage 90.23%.
- Scenario CLI list, run, replay, and reset passed for `SIM-RUN-990001`.
- `python scripts\validate_requirement_ids.py` passed.
- `python scripts\validate_prompt_records.py` will be rerun after this record update.
- `python -m unittest discover tests/governance` passed.
- Ruff and MyPy were unavailable in detected local Python environments.

## Generated Scenario Evidence
- CLI run `normal_day --seed 1001 --profile small --start-timestamp 2026-07-11T09:00:00+00:00 --run-id SIM-RUN-990001` generated 18 transactions, 6 provider balance snapshots, 2 shared cash snapshots, 3 provider feed statuses, and 1 ground-truth event.
- Replay of `SIM-RUN-990001` reproduced fingerprint `154bb67ce5df79d4abeba6e4bee810b697b7f3c740ff134a6953082f2e4a5b33`.

## Sonar Status
Skipped by latest user instruction to avoid CI and SonarQube during this implementation turn. Best-effort non-blocking Sonar policy remains configured; no pass is claimed.

## Audit Status
Human audit pending.

## Final Outcome
Synthetic scenario engine implemented locally with deterministic generation, persistence, reset/replay, safety validation, PostgreSQL integration tests, documentation updates, and prompt traceability. Remote CI/SonarQube not checked in this turn by user instruction.
