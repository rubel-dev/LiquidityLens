# Requirement Traceability

Status values: Documented, Approved, In Progress, Implemented, Verified, Deferred, Blocked.

| Requirement ID | Requirement | Source | Module | API | UI | Test | Metric | Demo Step | Status |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | Shared cash separate from provider balances | PDF | overview | /api/v1/agents/{agent_id}/overview planned | Agent/Ops overview | AC-001 | MET-006 | DEMO-001 | Approved |
| FR-002 | At least two providers, three where practical | PDF | scenario | /api/v1/providers planned | Overview | AC-001 | MET-006 | DEMO-001 | Approved |
| FR-003 | Deceptive-total visualization | Challenger idea | frontend | /api/v1/agents/{agent_id}/overview planned | Agent overview | AC-002 | MET-006 | DEMO-001 | Approved |
| FR-004 | Provider/shared runway clock | Challenger idea | liquidity | /api/v1/liquidity-forecasts planned | Overview/alerts | AC-003 | MET-001, MET-002 | DEMO-001 | Approved |
| FR-005 | Primary anomaly pattern | Locked MVP | anomaly | /api/v1/anomaly-findings planned | Alert detail | AC-004 | MET-003, MET-004 | DEMO-001 | Approved |
| FR-006 | Evidence fingerprint | Challenger idea | evidence | /api/v1/alerts/{alert_id} planned | Alert detail | AC-004 | MET-006 | DEMO-001 | Approved |
| FR-007 | Important alert fields | PDF | alerts | /api/v1/alerts/{alert_id} planned | Alert detail | AC-007 | MET-006 | DEMO-001 | Approved |
| FR-008 | Case lifecycle | PDF | cases | /api/v1/cases/{case_id} planned | Case UI | AC-007 | MET-009, MET-010, MET-011 | DEMO-001 | Approved |
| FR-009 | Reset/replay | Challenger idea | scenarios | CLI implemented; /api/v1/scenario-runs/{run_id}/reset planned | Demo controls planned | AC-009 | MET-009 | DEMO-002 | Implemented |
| FR-010 | Vendor-neutral LLM explanation | Conflict fix | explanation | /api/v1/alerts/{alert_id} planned | Alerts | AC-008 | MET-006 | DEMO-001 | Approved |
| FR-011 | Deterministic fallback | Conflict fix | explanation | /api/v1/alerts/{alert_id} planned | Alerts | AC-008 | MET-006 | DEMO-001 | Approved |
| FR-012 | False-positive scenario | Challenger idea | scenarios | CLI implemented; /api/v1/scenarios planned | Demo planned | AC-009 | MET-005 | DEMO-001 | Implemented |
| NFR-001 | Responsive demo interactions | PDF | platform | planned | All UI | AC-010 | MET-007 | DEMO-001 | Approved |
| NFR-002 | Explainable/auditable alerts | PDF | alerts/audit | /api/v1/audit-events planned | Alert/case UI | AC-007 | MET-006, MET-009 | DEMO-001 | Approved |
| NFR-003 | Bad data reduces confidence | PDF | validation/fusion | /api/v1/data-quality-statuses planned | Alerts | AC-006 | MET-008 | DEMO-001 | Approved |
| NFR-004 | Provider isolation | PDF | auth | all scoped APIs planned | all scoped UI | AC-011 | MET-012 | DEMO-001 | Approved |
| DATA-001 | Synthetic data only | PDF | scenario | CLI implemented; /api/v1/scenarios planned | n/a | AC-009 | MET-005 | DEMO-001 | Implemented |
| DATA-002 | Synthetic non-phone-like IDs | Governance | scenario | CLI implemented; /api/v1/transactions planned | Evidence UI planned | AC-004 | MET-003 | DEMO-001 | Implemented |
| DATA-003 | Shared cash is not provider feed | Governance | data model | CLI seed data implemented; /api/v1/agents/{agent_id}/cash-snapshots planned | Overview planned | AC-001 | MET-006 | DEMO-001 | Implemented |
| ARCH-001 | Modular monolith | Decision | architecture | n/a | n/a | governance validation | MET-012 | n/a | Implemented |
| ARCH-002 | No MVP microservices | Decision | architecture | n/a | n/a | governance validation | MET-012 | n/a | Implemented |
| API-001 | Versioned /api/v1 contracts | API design | api | `/api/v1/health`, `/api/v1/readiness` implemented; feature APIs planned | Foundation page health status only | backend/frontend foundation tests | MET-007 | DEMO-001 | In Progress |
| DB-001 | PostgreSQL with SQLAlchemy/Alembic | DB design | persistence | n/a | n/a | metadata tests and local PostgreSQL migration tests passed; remote CI pending | MET-012 | n/a | Implemented |
| SEC-001 | No credentials or real identities | PDF | security | all APIs planned | all UI | safety validation planned | MET-012 | n/a | Approved |
| SAFE-001 | No real financial activity | PDF | all | no execution endpoint | no command UI | safety validation planned | MET-012 | DEMO-001 | Approved |
| SAFE-002 | No wrongdoing declaration | PDF | explanation | alerts planned | alert UI | safety validation planned | MET-006 | DEMO-001 | Approved |
| SAFE-003 | Advisory recommendations only | Governance | explanation | alerts planned | alert UI | safety validation planned | MET-006 | DEMO-001 | Approved |
| MET-001 | Shortage detection lead time | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-001 | DEMO-001 | Approved |
| MET-002 | Forecast error | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-002 | DEMO-001 | Approved |
| MET-003 | Anomaly precision | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-003 | DEMO-001 | Approved |
| MET-004 | Anomaly recall | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-004 | DEMO-001 | Approved |
| MET-005 | False-positive rate | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-005 | DEMO-001 | Approved |
| MET-006 | Explanation coverage | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-006 | DEMO-001 | Approved |
| MET-007 | API p50/p95 latency | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-007 | DEMO-001 | Approved |
| MET-008 | Missing-feed fallback correctness | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-008 | DEMO-001 | Approved |
| MET-009 | Case lifecycle completion | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-009 | DEMO-001 | Approved |
| MET-010 | Alert acknowledgement time | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-010 | DEMO-001 | Approved |
| MET-011 | Resolution time | Metrics | metrics | /api/v1/metrics planned | metrics UI | AC-010 | MET-011 | DEMO-001 | Approved |
| MET-012 | SonarQube Quality Gate status | Metrics | ci | GitHub Actions | n/a | CI check | MET-012 | n/a | Approved |
| DOC-001 | Exact prompt history per commit | Governance | governance | n/a | n/a | traceability validator | MET-012 | n/a | Implemented |
| DOC-002 | Commit ledger | Governance | governance | n/a | n/a | traceability validator | MET-012 | n/a | Implemented |
| DOC-003 | Requirement traceability | Governance | governance | n/a | n/a | requirement ID validator | MET-012 | n/a | Implemented |
| QUALITY-001 | CI/Sonar before code | Governance | ci | n/a | n/a | CI | MET-012 | n/a | Implemented |
| QUALITY-002 | Commit metadata and prompt file validation | Governance | ci | n/a | n/a | traceability validator | MET-012 | n/a | Implemented |
| CI-001 | CI/Sonar on push and PR | Governance | ci | n/a | n/a | YAML validation | MET-012 | n/a | Implemented |
| CI-002 | Sonar secrets names only | Governance | ci | n/a | n/a | secret scan | MET-012 | n/a | Implemented |
| DEMO-001 | Story-driven golden flow | Demo | demo | planned | demo UI | AC-010 | MET-001, MET-006, MET-009 | DEMO-001 | Approved |
| DEMO-002 | Reset and replay | Demo | demo | /api/v1/scenario-runs/{run_id}/replay planned | demo UI | AC-009 | MET-009 | DEMO-002 | Approved |
