# PROMPT-0001: Finalize Selective Merge and Implementation Readiness

## Prompt ID
PROMPT-0001

## Prompt Type
fix-audit

## Date
2026-07-11

## Objective
Transform the teammate repository into the single canonical implementation-ready repository by selectively merging approved design ideas, correcting conflicts, and preparing documentation, prompt traceability, CI, and SonarQube.

## Module
architecture-governance

## Requirement IDs
DOC-001, QUALITY-001, CI-001, SAFE-001

## Exact Prompt SHA-256
ecae5ce59d0f470c83bb8894e7d5a30b2f3783fa575b4bafc92e4f9c51f99300

## Exact Prompt
``text
You are working inside the teammate repository that will become the final implementation repository for the SUST onsite hackathon project.

Do not clone another repository.
Do not create a second project.
Do not copy files into a parallel repository.
Do not blindly preserve the current architecture.
Do not write product application code in this step.

Your task is to transform this repository into the single canonical, implementation-ready repository by selectively combining the strongest approved ideas from both prior designs.

# Objective

Finalize one coherent source of truth for:

* PRD
* workflows
* architecture
* database design
* API contracts
* security and responsible AI
* testing and metrics
* prompt traceability
* commit policy
* SonarQube
* implementation plan
* demo strategy

The final design must remain hackathon-feasible, safe, explainable, auditable, and aligned with the original problem statement.

# Preserve These Mandatory Principles

The final repository must preserve:

1. Modular monolith architecture.
2. Next.js with TypeScript frontend.
3. FastAPI with Python backend.
4. PostgreSQL database.
5. SQLAlchemy and Alembic.
6. Deterministic analytics and rules for core decisions.
7. LLM only for Bengali/Banglish/English explanation and summaries.
8. Deterministic fallback when the LLM is unavailable.
9. Provider-specific balances remain separate.
10. Shared physical cash remains a separate concept.
11. No wallet merge.
12. No real money transfer.
13. No blocking or freezing.
14. No fraud declaration.
15. Human review for unusual activity.
16. Missing, delayed, stale, or conflicting data must reduce confidence.
17. Important alerts must include:

* reason
* evidence
* confidence
* uncertainty
* owner
* recommended next step
* status

18. Important case actions must be auditable.
19. Every implementation or fix commit must include the exact prompt used.
20. Every pushed commit must run SonarQube analysis.

# Selectively Adopt These Strong Ideas

Integrate these ideas into the final design:

1. Deceptive-total visualization:
   show when total value appears healthy but one provider is near shortage.

2. Provider-specific runway clock:
   show estimated shortage time for each provider and shared physical cash.

3. Evidence fingerprint:
   summarize:

   * repeated or near-identical amounts
   * abnormal transaction velocity
   * concentrated synthetic account group
   * time-window deviation
   * baseline deviation

4. Graceful degradation:
   delayed, stale, missing, or conflicting provider data must visibly reduce confidence.

5. False-positive scenario:
   include a normal Eid or salary-day spike that should not automatically become a suspicious case.

6. Story-driven demo:
   incident starts normal, pressure increases, system explains, alert is assigned, case is reviewed, and resolution is recorded.

7. Demo reset and replay.

8. Strong judge-facing metrics.

9. Detailed implementation task board.

# Reject or Defer These Ideas

Do not make these mandatory for the MVP:

* Redis
* Upstash
* Kafka
* Microservices
* Separate deployment per provider
* Mandatory WebSocket architecture
* Network graph
* Gantt timeline
* Sound alerts
* Complex model-learning feedback loop
* More than one primary anomaly pattern
* Excessive cloud dependencies
* Production-scale claims

Document these as deferred optional scope where appropriate.

# Fix Known Conflicts

Resolve these issues:

1. Remove conflicting AI vendor references.
   Use a vendor-neutral `LLM explanation provider` abstraction.

2. Correct any SonarQube project name or key that refers to another project.

3. Ensure SonarQube does not silently pass when required secrets are missing in the official validation flow.

4. Add automated validation for:

   * Prompt-ID in commit message
   * Requirement-IDs in commit message
   * matching prompt file in `prompts/history/`

5. Ensure shared physical cash is not attributed to any provider feed.

6. Ensure account identifiers are synthetic and not phone-number-like real identities.

7. Replace command-like recommendations such as:
   `Arrange 20,000 taka`
   with safe advisory language such as:
   `Coordinate approved liquidity support through the responsible provider operations channel.`

8. Replace language such as:
   `No fraud indicators`
   with:
   `The pattern is consistent with expected demand; no additional review is currently recommended.`

# Final Documentation Structure

Create or update:

```text
README.md

docs/
â”œâ”€â”€ 00-project-context.md
â”œâ”€â”€ 01-requirements.md
â”œâ”€â”€ 02-prd.md
â”œâ”€â”€ 03-workflows.md
â”œâ”€â”€ 04-architecture.md
â”œâ”€â”€ 05-database-design.md
â”œâ”€â”€ 06-api-contracts.md
â”œâ”€â”€ 07-security-and-safety.md
â”œâ”€â”€ 08-testing-and-metrics.md
â”œâ”€â”€ 09-deployment.md
â”œâ”€â”€ 10-data-and-simulation.md
â”œâ”€â”€ 11-requirement-traceability.md
â”œâ”€â”€ 12-decision-log.md
â”œâ”€â”€ 13-known-risks.md
â”œâ”€â”€ 14-implementation-status.md
â”œâ”€â”€ 15-code-quality-and-commit-policy.md
â”œâ”€â”€ 16-demo-script.md
â”œâ”€â”€ 17-implementation-plan.md
â”œâ”€â”€ 18-task-board.md
â””â”€â”€ commit-ledger.md

prompts/
â”œâ”€â”€ templates/
â””â”€â”€ history/
```

Do not create duplicate versions of the same document.

# PRD Requirements

The PRD must include:

* Product vision
* Problem definition
* Business objective
* Users and stakeholders
* Personas
* User stories
* Functional requirements
* Non-functional requirements
* Acceptance criteria
* Success metrics
* Assumptions
* Constraints
* Out of scope
* Future scope
* Demo scope
* Known limitations

Use measurable Given/When/Then acceptance criteria.

# Workflow Requirements

Document these workflows:

1. Scenario start
2. Synthetic data generation
3. Provider ingestion
4. Data validation
5. Liquidity analysis
6. Anomaly detection
7. Confidence calculation
8. Explanation generation
9. Deterministic fallback
10. Alert generation
11. Alert routing
12. Assignment
13. Acknowledgement
14. Escalation
15. Risk review
16. Resolution
17. Closure
18. Audit logging
19. Missing feed
20. Stale feed
21. Conflicting balance
22. Duplicate event
23. Concurrent case update
24. Unauthorized provider access
25. Demo reset
26. Demo replay

For every workflow include:

* Actor
* Trigger
* Preconditions
* Input
* Processing
* Decision points
* Output
* Failure path
* Safe fallback
* Authorization boundary
* Audit events
* Linked requirement IDs

Add Mermaid diagrams.

# Architecture Requirements

Use a modular monolith.

Include modules for:

* frontend
* backend API
* scenario engine
* provider adapters
* validation
* liquidity
* anomaly
* confidence and decision fusion
* explanation
* alerts
* cases
* audit
* authentication
* authorization
* metrics
* logging
* persistence

Explain provider isolation at:

* API layer
* service layer
* repository/query layer
* UI layer

Create:

* high-level architecture diagram
* component diagram
* data-flow diagram
* deployment diagram
* alert/case sequence diagram
* authorization flow

# Database Requirements

Document complete PostgreSQL tables for:

* users
* roles
* user_role_assignments
* providers
* areas
* agents
* agent_provider_accounts
* shared_cash_snapshots
* provider_balance_snapshots
* transactions
* provider_feed_statuses
* data_quality_events
* liquidity_forecasts
* anomaly_findings
* evidence_items
* confidence_assessments
* explanation_records
* alerts
* alert_assignments
* cases
* case_notes
* case_status_history
* escalations
* audit_events
* scenarios
* scenario_runs
* rule_versions
* human_feedback
* metric_observations

For every table include:

* purpose
* columns
* PostgreSQL types
* PK
* FK
* constraints
* indexes
* relationships
* provider scope
* retention

Add a Mermaid ER diagram.

# API Contract Requirements

Use `/api/v1`.

Document:

* authentication/session assumptions
* providers
* areas
* agents
* agent overview
* cash snapshots
* provider balances
* transactions
* data-quality status
* liquidity forecasts
* anomaly findings
* alerts
* acknowledgement
* assignment
* escalation
* cases
* notes
* resolution
* audit history
* scenarios
* scenario execution
* scenario reset
* scenario replay
* metrics
* health
* readiness

For every endpoint include:

* method
* path
* actor
* authorization
* provider scope
* request
* validation
* response
* status codes
* errors
* business rules
* idempotency
* pagination
* concurrency handling where relevant

# Metrics Requirements

Define:

* shortage detection lead time
* forecast error
* anomaly precision
* anomaly recall
* false-positive rate
* explanation coverage
* API p50 and p95 latency
* missing-feed fallback correctness
* case lifecycle completion rate
* alert acknowledgement time
* resolution time
* SonarQube Quality Gate status

For each metric include:

* formula
* dataset
* ground truth
* target
* evidence source
* limitation

# Prompt and Commit Traceability

Create exact prompt history.

Each implementation or fix commit must have:

* Prompt-ID
* Requirement-IDs
* Module
* Tests

Commit format:

```text
<type>(<scope>): <summary>

Requirement-IDs: <IDs>
Prompt-ID: <PROMPT-ID>
Module: <module-name>
Tests: <result>
```

Create automated checks that validate:

* Prompt-ID exists in commit message
* Requirement-IDs exist
* corresponding prompt file exists

# SonarQube

Create or correct:

* `sonar-project.properties`
* `.github/workflows/ci.yml`
* `.github/workflows/sonarqube.yml`
* `.env.example`

Run analysis on:

* every pushed branch
* pull requests to main

The flow must include:

* format check
* lint
* type check
* unit tests
* integration tests when available
* coverage
* SonarQube scan
* Quality Gate check

Do not include secrets.

Use placeholders:

* SONAR_TOKEN
* SONAR_HOST_URL
* SONAR_PROJECT_KEY

Do not claim SonarQube passed before CI confirms it.

# Implementation Plan

Use this order:

0. Governance, prompt validation, CI, SonarQube
1. Repository foundation
2. Database schema and migrations
3. Synthetic scenario engine
4. Provider ingestion and validation
5. Liquidity engine
6. Anomaly engine
7. Confidence and decision fusion
8. Explanation service and fallback
9. Alerts and cases
10. Backend APIs
11. Authentication and provider-scope authorization
12. Agent UI
13. Operations UI
14. Risk UI
15. Metrics and observability
16. Integration and failure testing
17. Demo packaging
18. Release preparation

# Scope Restriction

Do not implement product business logic in this step.

Do not create:

* ORM models
* migrations
* backend routes
* frontend screens
* algorithms
* real authentication
* production deployment

This step is only for:

* final selective merge
* documentation
* design correction
* prompt traceability
* CI
* SonarQube
* implementation readiness

# Validation Before Completion

Check:

* no duplicate docs
* no undefined requirement IDs
* no provider-boundary violation
* no financial execution
* no fraud declaration
* no secrets
* valid YAML
* valid Mermaid where practical
* correct Sonar project identity
* prompt history exists
* CI validates prompt traceability
* every mandatory requirement is traceable

# Commit Preparation

Create one prompt record for this exact task.

Use the next available Prompt-ID.

Prepare one focused commit:

```text
docs(architecture): finalize selective merge and implementation readiness

Requirement-IDs: DOC-001, QUALITY-001, CI-001, SAFE-001
Prompt-ID: <CURRENT-PROMPT-ID>
Module: architecture-governance
Tests: documentation, YAML, Mermaid, and configuration validation completed
```

Do not claim Quality Gate passed until remote analysis confirms it.

# Final Response Format

Return only:

## Files Created

## Files Updated

## Decisions Kept

## Challenger Ideas Adopted

## Ideas Rejected or Deferred

## Conflicts Resolved

## SonarQube Fixes

## Prompt Traceability

## Validation Performed

## Remaining Blockers

## Exact Commit Message

## Recommended First Coding Module

Do not begin implementation.

``

## In Scope
- Final selective merge
- Documentation
- Design correction
- Prompt traceability
- CI
- SonarQube
- Implementation readiness

## Out of Scope
- Product business logic
- ORM models
- Migrations
- Backend routes
- Frontend screens
- Algorithms
- Real authentication
- Production deployment

## Files Read
- README/top-level repository files
- ARCHITECTURE.md
- IMPLEMENTATION_PLAN.md
- DEMO_SCRIPT.md
- TASK.md
- SUMMARY.md
- JUDGE_PERSPECTIVE.md
- sonar-project.properties
- .github/workflows/sonar.yml
- hackathon.pdf
- Attached prompt file

## Files Changed
- README.md
- .env.example
- sonar-project.properties
- .github/workflows/ci.yml
- .github/workflows/sonarqube.yml
- docs/*
- prompts/templates/*
- prompts/history/PROMPT-0001-finalize-selective-merge.md

## Validation Performed
- Documentation validation
- YAML validation
- Mermaid presence validation
- Sonar configuration validation
- Requirement ID scan
- Secret scan
- Safety language scan
- Prompt traceability check

## Tests/Checks Run
- documentation, YAML, Mermaid, and configuration validation completed

## SonarQube Status
Configured. Quality Gate not claimed as passed until remote CI confirms it.

## Human Audit Status
Pending

## Follow-up Prompt ID
PROMPT-0002

## Final Outcome
Canonical documentation, governance, CI, and SonarQube foundation prepared without product implementation.
