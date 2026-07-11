# PROMPT-0002: Governance Hardening

## Prompt ID
PROMPT-0002

## Prompt Type
fix-audit

## Date
2026-07-11

## Objective
Create a trustworthy canonical governance commit that hardens prompt-to-commit traceability, CI enforcement, SonarQube evidence ordering, requirement traceability, architecture contracts, deployment documentation, and legacy exception records before product implementation begins.

## Module
governance-hardening

## Requirement IDs
QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001

## Exact Prompt SHA-256
8cbfff85d69ed5c84ffe634d7b84b165fb7ea12f46718c4ce39b3f6365795d62

## Exact Prompt
`````text
You are performing the final governance-hardening step before product implementation.

Do not write product business logic.
Do not create database models, migrations, APIs, algorithms, or frontend screens.

The current repository design is approved in principle, but implementation must not begin until prompt-to-commit traceability, CI enforcement, SonarQube evidence, and architecture contracts are corrected.

# READ FIRST

Read:

* `README.md`
* all files under `docs/`
* all files under `prompts/`
* `.github/workflows/ci.yml`
* `.github/workflows/sonarqube.yml`
* `sonar-project.properties`
* `.env.example`
* recent Git history
* current Git working tree status

# OBJECTIVE

Create one trustworthy canonical governance commit that:

1. Includes all currently approved design and documentation changes.
2. Stores the exact prompt used.
3. Validates every commit in a pushed range.
4. Runs tests and coverage before SonarQube analysis.
5. Makes future repository-foundation checks mandatory rather than silently optional.
6. Completes requirement traceability.
7. Strengthens implementation architecture contracts.
8. Records legacy non-compliant commits without rewriting history.

# 1. Preserve Current Approved Design

Do not remove or reverse:

* modular monolith
* Next.js TypeScript frontend
* FastAPI Python backend
* PostgreSQL
* SQLAlchemy and Alembic
* deterministic core analytics
* vendor-neutral LLM explanation provider
* deterministic explanation fallback
* provider isolation
* shared-cash separation
* safe non-fraud language
* human review
* append-only audit concepts
* deceptive-total visualization
* provider and shared-cash runway
* evidence fingerprint
* false-positive Eid/salary scenario
* case lifecycle
* reset and replay
* deferred Redis, Kafka, microservices, mandatory WebSockets, and network graph

# 2. Create a New Prompt Record

The existing `PROMPT-0001` record represents an earlier commit.

Create the next available prompt record, expected to be:

`prompts/history/PROMPT-0002-governance-hardening.md`

If that ID already exists, use the next sequential ID.

The prompt record must include:

* Prompt ID
* Prompt type
* Date
* Objective
* Module
* Requirement IDs
* Exact prompt used
* In scope
* Out of scope
* Files read
* Files changed
* Validation performed
* Tests/checks run
* SonarQube status
* Human audit status
* Follow-up prompt ID
* Final outcome

Store the exact prompt verbatim inside a valid fenced block or raw text section.

Do not use malformed syntax such as:

```
text
`	ext
```

Add a SHA-256 checksum of the exact prompt text to the record.

Do not include secrets.

# 3. Commit the Current Approved Working Tree

Inspect the working tree.

Ensure all approved documentation, governance, CI, SonarQube, prompt, and configuration changes are included in one focused commit.

Do not include unrelated product code.

Update `docs/commit-ledger.md` with a pending entry for the new Prompt-ID.

Do not write the current commit SHA into the same commit.

# 4. Validate Every Commit in a Push

The current CI validates only `git log -1`.

Replace this with a script, for example:

```text
scripts/validate_commit_traceability.py
```

or:

```text
.github/scripts/validate_commit_traceability.py
```

The validator must inspect every commit introduced by the event.

For push events:

* Validate the range from `github.event.before` to `github.sha`.
* Correctly handle the first push or a zero SHA.
* Validate all commits in the range, not only the latest one.

For pull requests:

* Validate all commits in the pull-request commit range.

For every non-exempt commit require:

* `Requirement-IDs:`
* `Prompt-ID: PROMPT-XXXX`
* `Module:`
* `Tests:`
* a matching file under `prompts/history/PROMPT-XXXX-*.md`

Fail CI when any required field or matching prompt file is missing.

Document narrowly scoped exemptions only for:

* automatic merge commits
* GitHub-generated commits, if unavoidable
* explicitly recorded legacy commits

Do not create a broad exemption that defeats the policy.

Add unit tests for the validator covering:

1. Valid single commit
2. Valid multiple commits
3. Missing Prompt-ID
4. Missing Requirement-IDs
5. Missing Module
6. Missing Tests
7. Missing prompt file
8. Merge commit handling
9. Initial push handling
10. Pull-request range handling

# 5. Record Legacy Commit Exceptions

Recent history contains non-compliant commits such as:

* `Delete prompts directory`
* `Delete frontend directory`

Do not rewrite shared history unless explicitly authorized.

Update:

* `docs/commit-ledger.md`
* `docs/15-code-quality-and-commit-policy.md`

Record these as legacy pre-enforcement exceptions.

State that all commits after the governance-hardening commit are subject to mandatory enforcement.

# 6. Consolidate CI and SonarQube Evidence

Ensure SonarQube analysis runs only after required tests and coverage generation.

Use either:

## Preferred option

One workflow where jobs execute in this order:

```text
traceability
    â†“
backend-quality
    â†“
frontend-quality
    â†“
test-and-coverage
    â†“
sonarqube
    â†“
quality-gate
```

or:

## Acceptable option

Reusable workflows with explicit dependencies and uploaded/downloaded coverage artifacts.

The effective pipeline must:

1. Checkout with full history.
2. Validate all pushed commits.
3. Install dependencies.
4. Run formatting checks.
5. Run linting.
6. Run type checking.
7. Run unit tests.
8. Run integration tests when present.
9. Generate backend `coverage.xml`.
10. Generate frontend `lcov.info`.
11. Run SonarQube scan.
12. Wait for Quality Gate result.

Do not run SonarQube before coverage generation.

Do not silently claim coverage when reports do not exist.

# 7. Handle the Pre-Code Repository Safely

Product source code does not exist yet.

For this final governance commit:

* Documentation/configuration validation may pass without application code.
* SonarQube must still run on the current repository when configured.
* Clearly distinguish `governance-only mode` from `product-code mode`.

In the next repository-foundation phase, CI must become mandatory for:

Backend:

* Ruff format check
* Ruff lint
* MyPy or Pyright
* Pytest
* coverage generation

Frontend:

* formatter check
* ESLint
* TypeScript type check
* unit tests
* production build
* coverage generation

Do not continue using `--if-present` after the repository foundation is scaffolded.

Add an explicit CI mode check or documented transition gate.

# 8. Correct SonarQube Configuration

Choose one authoritative source for the project key.

Preferred:

* Keep `sonar.projectKey` in `sonar-project.properties`.
* Use `SONAR_TOKEN` and `SONAR_HOST_URL` as secrets.
* Do not require a second conflicting project-key secret unless the event rules mandate it.

Set project identity to the actual SUST Onsite project.

Do not scan the entire repository indefinitely.

For governance-only mode, document the temporary source scope.

For product-code mode, plan explicit paths such as:

```text
sonar.sources=backend/app,frontend/src
sonar.tests=backend/tests,frontend/src
```

Use correct test inclusion rules and coverage report paths.

Document when this transition occurs.

Do not exclude files merely to hide issues.

# 9. Complete Requirement Traceability

Update `docs/11-requirement-traceability.md`.

Ensure every approved mandatory requirement in `docs/01-requirements.md` has exactly one or more traceability rows.

Do not use range syntax such as:

```text
MET-009..011
```

Use explicit IDs:

```text
MET-009, MET-010, MET-011
```

Validate:

* every requirement ID exists
* every referenced test ID exists
* every metric ID exists
* every demo ID exists
* every API reference is valid or marked planned
* status values are valid

Add a machine-executable validation script for ID consistency if practical.

# 10. Strengthen Architecture Contracts

Update `docs/04-architecture.md`.

Add:

## Package Layout

Define the intended structure, for example:

```text
backend/
  app/
    core/
    auth/
    providers/
    scenarios/
    validation/
    liquidity/
    anomaly/
    confidence/
    explanations/
    alerts/
    cases/
    audit/
    metrics/
    api/
    persistence/

frontend/
  src/
    app/
    features/
    components/
    lib/
    types/
```

## Dependency Rules

Specify:

* API may call application services.
* Application services may call domain logic and repository interfaces.
* Domain logic must not depend on FastAPI, SQLAlchemy, or LLM vendors.
* Persistence implementations may depend on SQLAlchemy.
* UI must not implement financial decision logic.
* Explanation provider must not create or modify core risk decisions.
* Provider-scoped queries must receive an authorization context.

## Transaction Boundaries

Specify which service owns transactions for:

* scenario execution
* alert creation
* assignment
* acknowledgement
* escalation
* case resolution
* audit event creation

## Concurrency Policy

Specify:

* idempotency keys
* optimistic concurrency/version fields
* duplicate acknowledgement behavior
* concurrent assignment behavior
* append-only case history

## Sync/Async Policy

For MVP:

* core request processing may be synchronous
* long demo generation or explanation may use a simple background task only if necessary
* no Kafka or distributed queue
* deterministic fallback when explanation times out

## Domain Event Policy

Define internal events such as:

* FeedValidated
* LiquidityForecastCreated
* AnomalyFindingCreated
* AlertCreated
* AlertAcknowledged
* CaseEscalated
* CaseResolved

These may initially be in-process events.

# 11. Resolve Immediate Open Decisions

Update `docs/12-decision-log.md`.

Lock:

* Demo providers: synthetic labels representing three logically separate providers, or approved demonstration names if legally appropriate.
* Frontend test runner: choose one and document it.
* Canonical deployment for development/demo: local Docker Compose.
* Optional cloud deployment: document one target as optional, not mandatory.

The exact final hosting target may remain open only if local Docker Compose is fully canonical.

# 12. Improve Deployment Documentation

Expand `docs/09-deployment.md`.

Include:

* local Docker Compose topology
* environment-variable names
* database initialization
* migration command
* seed/scenario command
* demo reset command
* health check
* readiness check
* backup demo procedure
* log locations
* rollback approach
* SonarQube secret setup
* branch-protection recommendation
* Quality Gate merge protection
* known limitations

Do not claim production readiness.

# 13. Replace Brittle Safety Validation

Keep simple grep checks only as supplemental checks.

Add structured safety validation or tests for:

* no financial-execution endpoints
* no freeze/block action
* no provider-balance transfer
* no final wrongdoing classification
* no real account or phone-number-like identifiers in seed data
* missing balances do not default to zero
* provider-scoped access requirements

Document these as mandatory future tests.

# 14. Validation

Before finishing, run:

* YAML validation
* Markdown-link validation where practical
* prompt-record format validation
* commit traceability validator tests
* requirement-ID consistency validation
* Sonar properties validation
* secret scanning
* Git status review

Report commands and results honestly.

Do not claim remote SonarQube Quality Gate passed unless it actually ran and passed.

# 15. Commit Preparation

Prepare one focused commit using:

```text
chore(governance): enforce commit traceability and sonar evidence

Requirement-IDs: QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001
Prompt-ID: <NEW_PROMPT-ID>
Module: governance-hardening
Tests: traceability, YAML, requirement-ID, and configuration validation passed
```

After committing, the working tree must be clean.

If pushing is possible:

* push the commit
* wait for CI and SonarQube
* report the exact run result

If pushing is not possible:

* provide the exact push command
* keep SonarQube and Quality Gate status as Pending

# OUT OF SCOPE

Do not implement:

* ORM models
* Alembic migrations
* business algorithms
* backend APIs
* frontend screens
* production authentication
* real provider integrations

# FINAL RESPONSE FORMAT

Return only:

## Prompt Record Created

## Files Created

## Files Updated

## Commit Traceability Enforcement

## CI and Coverage Flow

## SonarQube Configuration

## Architecture Contracts Added

## Requirement Traceability Fixes

## Legacy Commit Exceptions

## Validation Performed

## Commit Created

## Git Status

## Remote CI/Sonar Result

## Remaining Blockers

## Recommended Next Module

Do not begin product implementation.

````

## Preferred option

One workflow where jobs execute in this order:

```text
traceability
    â†“
backend-quality
    â†“
frontend-quality
    â†“
test-and-coverage
    â†“
sonarqube
    â†“
quality-gate
```

or:

## Acceptable option

Reusable workflows with explicit dependencies and uploaded/downloaded coverage artifacts.

The effective pipeline must:

1. Checkout with full history.
2. Validate all pushed commits.
3. Install dependencies.
4. Run formatting checks.
5. Run linting.
6. Run type checking.
7. Run unit tests.
8. Run integration tests when present.
9. Generate backend `coverage.xml`.
10. Generate frontend `lcov.info`.
11. Run SonarQube scan.
12. Wait for Quality Gate result.

Do not run SonarQube before coverage generation.

Do not silently claim coverage when reports do not exist.

# 7. Handle the Pre-Code Repository Safely

Product source code does not exist yet.

For this final governance commit:

* Documentation/configuration validation may pass without application code.
* SonarQube must still run on the current repository when configured.
* Clearly distinguish `governance-only mode` from `product-code mode`.

In the next repository-foundation phase, CI must become mandatory for:

Backend:

* Ruff format check
* Ruff lint
* MyPy or Pyright
* Pytest
* coverage generation

Frontend:

* formatter check
* ESLint
* TypeScript type check
* unit tests
* production build
* coverage generation

Do not continue using `--if-present` after the repository foundation is scaffolded.

Add an explicit CI mode check or documented transition gate.

# 8. Correct SonarQube Configuration

Choose one authoritative source for the project key.

Preferred:

* Keep `sonar.projectKey` in `sonar-project.properties`.
* Use `SONAR_TOKEN` and `SONAR_HOST_URL` as secrets.
* Do not require a second conflicting project-key secret unless the event rules mandate it.

Set project identity to the actual SUST Onsite project.

Do not scan the entire repository indefinitely.

For governance-only mode, document the temporary source scope.

For product-code mode, plan explicit paths such as:

```text
sonar.sources=backend/app,frontend/src
sonar.tests=backend/tests,frontend/src
```

Use correct test inclusion rules and coverage report paths.

Document when this transition occurs.

Do not exclude files merely to hide issues.

# 9. Complete Requirement Traceability

Update `docs/11-requirement-traceability.md`.

Ensure every approved mandatory requirement in `docs/01-requirements.md` has exactly one or more traceability rows.

Do not use range syntax such as:

```text
MET-009..011
```

Use explicit IDs:

```text
MET-009, MET-010, MET-011
```

Validate:

* every requirement ID exists
* every referenced test ID exists
* every metric ID exists
* every demo ID exists
* every API reference is valid or marked planned
* status values are valid

Add a machine-executable validation script for ID consistency if practical.

# 10. Strengthen Architecture Contracts

Update `docs/04-architecture.md`.

Add:

## Package Layout

Define the intended structure, for example:

```text
backend/
  app/
    core/
    auth/
    providers/
    scenarios/
    validation/
    liquidity/
    anomaly/
    confidence/
    explanations/
    alerts/
    cases/
    audit/
    metrics/
    api/
    persistence/

frontend/
  src/
    app/
    features/
    components/
    lib/
    types/
```

## Dependency Rules

Specify:

* API may call application services.
* Application services may call domain logic and repository interfaces.
* Domain logic must not depend on FastAPI, SQLAlchemy, or LLM vendors.
* Persistence implementations may depend on SQLAlchemy.
* UI must not implement financial decision logic.
* Explanation provider must not create or modify core risk decisions.
* Provider-scoped queries must receive an authorization context.

## Transaction Boundaries

Specify which service owns transactions for:

* scenario execution
* alert creation
* assignment
* acknowledgement
* escalation
* case resolution
* audit event creation

## Concurrency Policy

Specify:

* idempotency keys
* optimistic concurrency/version fields
* duplicate acknowledgement behavior
* concurrent assignment behavior
* append-only case history

## Sync/Async Policy

For MVP:

* core request processing may be synchronous
* long demo generation or explanation may use a simple background task only if necessary
* no Kafka or distributed queue
* deterministic fallback when explanation times out

## Domain Event Policy

Define internal events such as:

* FeedValidated
* LiquidityForecastCreated
* AnomalyFindingCreated
* AlertCreated
* AlertAcknowledged
* CaseEscalated
* CaseResolved

These may initially be in-process events.

# 11. Resolve Immediate Open Decisions

Update `docs/12-decision-log.md`.

Lock:

* Demo providers: synthetic labels representing three logically separate providers, or approved demonstration names if legally appropriate.
* Frontend test runner: choose one and document it.
* Canonical deployment for development/demo: local Docker Compose.
* Optional cloud deployment: document one target as optional, not mandatory.

The exact final hosting target may remain open only if local Docker Compose is fully canonical.

# 12. Improve Deployment Documentation

Expand `docs/09-deployment.md`.

Include:

* local Docker Compose topology
* environment-variable names
* database initialization
* migration command
* seed/scenario command
* demo reset command
* health check
* readiness check
* backup demo procedure
* log locations
* rollback approach
* SonarQube secret setup
* branch-protection recommendation
* Quality Gate merge protection
* known limitations

Do not claim production readiness.

# 13. Replace Brittle Safety Validation

Keep simple grep checks only as supplemental checks.

Add structured safety validation or tests for:

* no financial-execution endpoints
* no freeze/block action
* no provider-balance transfer
* no final wrongdoing classification
* no real account or phone-number-like identifiers in seed data
* missing balances do not default to zero
* provider-scoped access requirements

Document these as mandatory future tests.

# 14. Validation

Before finishing, run:

* YAML validation
* Markdown-link validation where practical
* prompt-record format validation
* commit traceability validator tests
* requirement-ID consistency validation
* Sonar properties validation
* secret scanning
* Git status review

Report commands and results honestly.

Do not claim remote SonarQube Quality Gate passed unless it actually ran and passed.

# 15. Commit Preparation

Prepare one focused commit using:

```text
chore(governance): enforce commit traceability and sonar evidence

Requirement-IDs: QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001
Prompt-ID: <NEW_PROMPT-ID>
Module: governance-hardening
Tests: traceability, YAML, requirement-ID, and configuration validation passed
```

After committing, the working tree must be clean.

If pushing is possible:

* push the commit
* wait for CI and SonarQube
* report the exact run result

If pushing is not possible:

* provide the exact push command
* keep SonarQube and Quality Gate status as Pending

# OUT OF SCOPE

Do not implement:

* ORM models
* Alembic migrations
* business algorithms
* backend APIs
* frontend screens
* production authentication
* real provider integrations

# FINAL RESPONSE FORMAT

Return only:

## Prompt Record Created

## Files Created

## Files Updated

## Commit Traceability Enforcement

## CI and Coverage Flow

## SonarQube Configuration

## Architecture Contracts Added

## Requirement Traceability Fixes

## Legacy Commit Exceptions

## Validation Performed

## Commit Created

## Git Status

## Remote CI/Sonar Result

## Remaining Blockers

## Recommended Next Module

Do not begin product implementation.

`````

## Preferred option

One workflow where jobs execute in this order:

```text
traceability
    â†“
backend-quality
    â†“
frontend-quality
    â†“
test-and-coverage
    â†“
sonarqube
    â†“
quality-gate
```

or:

## Acceptable option

Reusable workflows with explicit dependencies and uploaded/downloaded coverage artifacts.

The effective pipeline must:

1. Checkout with full history.
2. Validate all pushed commits.
3. Install dependencies.
4. Run formatting checks.
5. Run linting.
6. Run type checking.
7. Run unit tests.
8. Run integration tests when present.
9. Generate backend `coverage.xml`.
10. Generate frontend `lcov.info`.
11. Run SonarQube scan.
12. Wait for Quality Gate result.

Do not run SonarQube before coverage generation.

Do not silently claim coverage when reports do not exist.

# 7. Handle the Pre-Code Repository Safely

Product source code does not exist yet.

For this final governance commit:

* Documentation/configuration validation may pass without application code.
* SonarQube must still run on the current repository when configured.
* Clearly distinguish `governance-only mode` from `product-code mode`.

In the next repository-foundation phase, CI must become mandatory for:

Backend:

* Ruff format check
* Ruff lint
* MyPy or Pyright
* Pytest
* coverage generation

Frontend:

* formatter check
* ESLint
* TypeScript type check
* unit tests
* production build
* coverage generation

Do not continue using `--if-present` after the repository foundation is scaffolded.

Add an explicit CI mode check or documented transition gate.

# 8. Correct SonarQube Configuration

Choose one authoritative source for the project key.

Preferred:

* Keep `sonar.projectKey` in `sonar-project.properties`.
* Use `SONAR_TOKEN` and `SONAR_HOST_URL` as secrets.
* Do not require a second conflicting project-key secret unless the event rules mandate it.

Set project identity to the actual SUST Onsite project.

Do not scan the entire repository indefinitely.

For governance-only mode, document the temporary source scope.

For product-code mode, plan explicit paths such as:

```text
sonar.sources=backend/app,frontend/src
sonar.tests=backend/tests,frontend/src
```

Use correct test inclusion rules and coverage report paths.

Document when this transition occurs.

Do not exclude files merely to hide issues.

# 9. Complete Requirement Traceability

Update `docs/11-requirement-traceability.md`.

Ensure every approved mandatory requirement in `docs/01-requirements.md` has exactly one or more traceability rows.

Do not use range syntax such as:

```text
MET-009..011
```

Use explicit IDs:

```text
MET-009, MET-010, MET-011
```

Validate:

* every requirement ID exists
* every referenced test ID exists
* every metric ID exists
* every demo ID exists
* every API reference is valid or marked planned
* status values are valid

Add a machine-executable validation script for ID consistency if practical.

# 10. Strengthen Architecture Contracts

Update `docs/04-architecture.md`.

Add:

## Package Layout

Define the intended structure, for example:

```text
backend/
  app/
    core/
    auth/
    providers/
    scenarios/
    validation/
    liquidity/
    anomaly/
    confidence/
    explanations/
    alerts/
    cases/
    audit/
    metrics/
    api/
    persistence/

frontend/
  src/
    app/
    features/
    components/
    lib/
    types/
```

## Dependency Rules

Specify:

* API may call application services.
* Application services may call domain logic and repository interfaces.
* Domain logic must not depend on FastAPI, SQLAlchemy, or LLM vendors.
* Persistence implementations may depend on SQLAlchemy.
* UI must not implement financial decision logic.
* Explanation provider must not create or modify core risk decisions.
* Provider-scoped queries must receive an authorization context.

## Transaction Boundaries

Specify which service owns transactions for:

* scenario execution
* alert creation
* assignment
* acknowledgement
* escalation
* case resolution
* audit event creation

## Concurrency Policy

Specify:

* idempotency keys
* optimistic concurrency/version fields
* duplicate acknowledgement behavior
* concurrent assignment behavior
* append-only case history

## Sync/Async Policy

For MVP:

* core request processing may be synchronous
* long demo generation or explanation may use a simple background task only if necessary
* no Kafka or distributed queue
* deterministic fallback when explanation times out

## Domain Event Policy

Define internal events such as:

* FeedValidated
* LiquidityForecastCreated
* AnomalyFindingCreated
* AlertCreated
* AlertAcknowledged
* CaseEscalated
* CaseResolved

These may initially be in-process events.

# 11. Resolve Immediate Open Decisions

Update `docs/12-decision-log.md`.

Lock:

* Demo providers: synthetic labels representing three logically separate providers, or approved demonstration names if legally appropriate.
* Frontend test runner: choose one and document it.
* Canonical deployment for development/demo: local Docker Compose.
* Optional cloud deployment: document one target as optional, not mandatory.

The exact final hosting target may remain open only if local Docker Compose is fully canonical.

# 12. Improve Deployment Documentation

Expand `docs/09-deployment.md`.

Include:

* local Docker Compose topology
* environment-variable names
* database initialization
* migration command
* seed/scenario command
* demo reset command
* health check
* readiness check
* backup demo procedure
* log locations
* rollback approach
* SonarQube secret setup
* branch-protection recommendation
* Quality Gate merge protection
* known limitations

Do not claim production readiness.

# 13. Replace Brittle Safety Validation

Keep simple grep checks only as supplemental checks.

Add structured safety validation or tests for:

* no financial-execution endpoints
* no freeze/block action
* no provider-balance transfer
* no final wrongdoing classification
* no real account or phone-number-like identifiers in seed data
* missing balances do not default to zero
* provider-scoped access requirements

Document these as mandatory future tests.

# 14. Validation

Before finishing, run:

* YAML validation
* Markdown-link validation where practical
* prompt-record format validation
* commit traceability validator tests
* requirement-ID consistency validation
* Sonar properties validation
* secret scanning
* Git status review

Report commands and results honestly.

Do not claim remote SonarQube Quality Gate passed unless it actually ran and passed.

# 15. Commit Preparation

Prepare one focused commit using:

```text
chore(governance): enforce commit traceability and sonar evidence

Requirement-IDs: QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001
Prompt-ID: <NEW_PROMPT-ID>
Module: governance-hardening
Tests: traceability, YAML, requirement-ID, and configuration validation passed
```

After committing, the working tree must be clean.

If pushing is possible:

* push the commit
* wait for CI and SonarQube
* report the exact run result

If pushing is not possible:

* provide the exact push command
* keep SonarQube and Quality Gate status as Pending

# OUT OF SCOPE

Do not implement:

* ORM models
* Alembic migrations
* business algorithms
* backend APIs
* frontend screens
* production authentication
* real provider integrations

# FINAL RESPONSE FORMAT

Return only:

## Prompt Record Created

## Files Created

## Files Updated

## Commit Traceability Enforcement

## CI and Coverage Flow

## SonarQube Configuration

## Architecture Contracts Added

## Requirement Traceability Fixes

## Legacy Commit Exceptions

## Validation Performed

## Commit Created

## Git Status

## Remote CI/Sonar Result

## Remaining Blockers

## Recommended Next Module

Do not begin product implementation.

````

## Preferred option

One workflow where jobs execute in this order:

```text
traceability
    â†“
backend-quality
    â†“
frontend-quality
    â†“
test-and-coverage
    â†“
sonarqube
    â†“
quality-gate
```

or:

## Acceptable option

Reusable workflows with explicit dependencies and uploaded/downloaded coverage artifacts.

The effective pipeline must:

1. Checkout with full history.
2. Validate all pushed commits.
3. Install dependencies.
4. Run formatting checks.
5. Run linting.
6. Run type checking.
7. Run unit tests.
8. Run integration tests when present.
9. Generate backend `coverage.xml`.
10. Generate frontend `lcov.info`.
11. Run SonarQube scan.
12. Wait for Quality Gate result.

Do not run SonarQube before coverage generation.

Do not silently claim coverage when reports do not exist.

# 7. Handle the Pre-Code Repository Safely

Product source code does not exist yet.

For this final governance commit:

* Documentation/configuration validation may pass without application code.
* SonarQube must still run on the current repository when configured.
* Clearly distinguish `governance-only mode` from `product-code mode`.

In the next repository-foundation phase, CI must become mandatory for:

Backend:

* Ruff format check
* Ruff lint
* MyPy or Pyright
* Pytest
* coverage generation

Frontend:

* formatter check
* ESLint
* TypeScript type check
* unit tests
* production build
* coverage generation

Do not continue using `--if-present` after the repository foundation is scaffolded.

Add an explicit CI mode check or documented transition gate.

# 8. Correct SonarQube Configuration

Choose one authoritative source for the project key.

Preferred:

* Keep `sonar.projectKey` in `sonar-project.properties`.
* Use `SONAR_TOKEN` and `SONAR_HOST_URL` as secrets.
* Do not require a second conflicting project-key secret unless the event rules mandate it.

Set project identity to the actual SUST Onsite project.

Do not scan the entire repository indefinitely.

For governance-only mode, document the temporary source scope.

For product-code mode, plan explicit paths such as:

```text
sonar.sources=backend/app,frontend/src
sonar.tests=backend/tests,frontend/src
```

Use correct test inclusion rules and coverage report paths.

Document when this transition occurs.

Do not exclude files merely to hide issues.

# 9. Complete Requirement Traceability

Update `docs/11-requirement-traceability.md`.

Ensure every approved mandatory requirement in `docs/01-requirements.md` has exactly one or more traceability rows.

Do not use range syntax such as:

```text
MET-009..011
```

Use explicit IDs:

```text
MET-009, MET-010, MET-011
```

Validate:

* every requirement ID exists
* every referenced test ID exists
* every metric ID exists
* every demo ID exists
* every API reference is valid or marked planned
* status values are valid

Add a machine-executable validation script for ID consistency if practical.

# 10. Strengthen Architecture Contracts

Update `docs/04-architecture.md`.

Add:

## Package Layout

Define the intended structure, for example:

```text
backend/
  app/
    core/
    auth/
    providers/
    scenarios/
    validation/
    liquidity/
    anomaly/
    confidence/
    explanations/
    alerts/
    cases/
    audit/
    metrics/
    api/
    persistence/

frontend/
  src/
    app/
    features/
    components/
    lib/
    types/
```

## Dependency Rules

Specify:

* API may call application services.
* Application services may call domain logic and repository interfaces.
* Domain logic must not depend on FastAPI, SQLAlchemy, or LLM vendors.
* Persistence implementations may depend on SQLAlchemy.
* UI must not implement financial decision logic.
* Explanation provider must not create or modify core risk decisions.
* Provider-scoped queries must receive an authorization context.

## Transaction Boundaries

Specify which service owns transactions for:

* scenario execution
* alert creation
* assignment
* acknowledgement
* escalation
* case resolution
* audit event creation

## Concurrency Policy

Specify:

* idempotency keys
* optimistic concurrency/version fields
* duplicate acknowledgement behavior
* concurrent assignment behavior
* append-only case history

## Sync/Async Policy

For MVP:

* core request processing may be synchronous
* long demo generation or explanation may use a simple background task only if necessary
* no Kafka or distributed queue
* deterministic fallback when explanation times out

## Domain Event Policy

Define internal events such as:

* FeedValidated
* LiquidityForecastCreated
* AnomalyFindingCreated
* AlertCreated
* AlertAcknowledged
* CaseEscalated
* CaseResolved

These may initially be in-process events.

# 11. Resolve Immediate Open Decisions

Update `docs/12-decision-log.md`.

Lock:

* Demo providers: synthetic labels representing three logically separate providers, or approved demonstration names if legally appropriate.
* Frontend test runner: choose one and document it.
* Canonical deployment for development/demo: local Docker Compose.
* Optional cloud deployment: document one target as optional, not mandatory.

The exact final hosting target may remain open only if local Docker Compose is fully canonical.

# 12. Improve Deployment Documentation

Expand `docs/09-deployment.md`.

Include:

* local Docker Compose topology
* environment-variable names
* database initialization
* migration command
* seed/scenario command
* demo reset command
* health check
* readiness check
* backup demo procedure
* log locations
* rollback approach
* SonarQube secret setup
* branch-protection recommendation
* Quality Gate merge protection
* known limitations

Do not claim production readiness.

# 13. Replace Brittle Safety Validation

Keep simple grep checks only as supplemental checks.

Add structured safety validation or tests for:

* no financial-execution endpoints
* no freeze/block action
* no provider-balance transfer
* no final wrongdoing classification
* no real account or phone-number-like identifiers in seed data
* missing balances do not default to zero
* provider-scoped access requirements

Document these as mandatory future tests.

# 14. Validation

Before finishing, run:

* YAML validation
* Markdown-link validation where practical
* prompt-record format validation
* commit traceability validator tests
* requirement-ID consistency validation
* Sonar properties validation
* secret scanning
* Git status review

Report commands and results honestly.

Do not claim remote SonarQube Quality Gate passed unless it actually ran and passed.

# 15. Commit Preparation

Prepare one focused commit using:

```text
chore(governance): enforce commit traceability and sonar evidence

Requirement-IDs: QUALITY-001, QUALITY-002, CI-001, CI-002, DOC-001
Prompt-ID: <NEW_PROMPT-ID>
Module: governance-hardening
Tests: traceability, YAML, requirement-ID, and configuration validation passed
```

After committing, the working tree must be clean.

If pushing is possible:

* push the commit
* wait for CI and SonarQube
* report the exact run result

If pushing is not possible:

* provide the exact push command
* keep SonarQube and Quality Gate status as Pending

# OUT OF SCOPE

Do not implement:

* ORM models
* Alembic migrations
* business algorithms
* backend APIs
* frontend screens
* production authentication
* real provider integrations

# FINAL RESPONSE FORMAT

Return only:

## Prompt Record Created

## Files Created

## Files Updated

## Commit Traceability Enforcement

## CI and Coverage Flow

## SonarQube Configuration

## Architecture Contracts Added

## Requirement Traceability Fixes

## Legacy Commit Exceptions

## Validation Performed

## Commit Created

## Git Status

## Remote CI/Sonar Result

## Remaining Blockers

## Recommended Next Module

Do not begin product implementation.

``

## In Scope
- Prompt traceability hardening
- Commit-range validation
- CI and SonarQube ordering
- Governance-only/product-code mode distinction
- Requirement traceability completion
- Architecture contract strengthening
- Legacy commit exception records
- Deployment and quality policy hardening

## Out of Scope
- ORM models
- Alembic migrations
- Business algorithms
- Backend APIs
- Frontend screens
- Production authentication
- Real provider integrations

## Files Read
- README.md
- docs/*
- prompts/*
- .github/workflows/ci.yml
- .github/workflows/sonarqube.yml
- sonar-project.properties
- .env.example
- recent Git history
- Git working tree status

## Files Changed
- README.md
- sonar-project.properties
- .github/workflows/ci.yml
- docs/04-architecture.md
- docs/09-deployment.md
- docs/11-requirement-traceability.md
- docs/12-decision-log.md
- docs/15-code-quality-and-commit-policy.md
- docs/commit-ledger.md
- prompts/history/PROMPT-0001-finalize-selective-merge.md
- prompts/history/PROMPT-0002-governance-hardening.md
- scripts/check_ci_mode.py
- scripts/validate_commit_traceability.py
- scripts/validate_requirement_ids.py
- tests/governance/test_validate_commit_traceability.py

## Validation Performed
- YAML validation
- Prompt record format validation
- Commit traceability validator tests
- Requirement ID consistency validation
- Sonar properties validation
- Secret scanning
- Git status review

## Tests/Checks Run
- python -m unittest discover tests/governance
- python scripts/validate_requirement_ids.py
- python scripts/validate_commit_traceability.py with explicit commit range
- YAML parsing via Python/PyYAML
- PowerShell content scans for secrets and unsafe language

## SonarQube Status
Configured locally. Remote Quality Gate is Pending until the commit is pushed and GitHub Actions completes with configured SonarQube secrets.

## Human Audit Status
Pending

## Follow-up Prompt ID
PROMPT-0003

## Final Outcome
Governance hardening completed without product implementation.
