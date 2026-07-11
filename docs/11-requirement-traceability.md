# Requirement Traceability

| Requirement ID | Requirement | Source | Module | API | UI | Test | Metric | Demo Step | Status |
|---|---|---|---|---|---|---|---|---|---|
| FR-001 | Shared cash separate from provider balances | PDF | overview | /api/v1/agents/{agent_id}/overview | Agent/Ops overview | AC-001 | MET-006 | DEMO-001 | Approved |
| FR-002 | At least two providers, three where practical | PDF | scenario | /api/v1/providers | Overview | AC-001 | MET-006 | DEMO-001 | Approved |
| FR-003 | Deceptive-total visualization | Challenger idea | frontend | overview | Agent overview | AC-002 | MET-006 | DEMO-001 | Approved |
| FR-004 | Provider/shared runway clock | Challenger idea | liquidity | /api/v1/liquidity-forecasts | Overview/alerts | AC-003 | MET-001,MET-002 | DEMO-001 | Approved |
| FR-005 | Primary anomaly pattern | Locked MVP | anomaly | /api/v1/anomaly-findings | Alert detail | AC-004 | MET-003,MET-004 | DEMO-001 | Approved |
| FR-006 | Evidence fingerprint | Challenger idea | evidence | /api/v1/alerts/{alert_id} | Alert detail | AC-004 | MET-006 | DEMO-001 | Approved |
| FR-007 | Important alert fields | PDF | alerts | /api/v1/alerts/{alert_id} | Alert detail | AC-007 | MET-006 | DEMO-001 | Approved |
| FR-008 | Case lifecycle | PDF | cases | /api/v1/cases/* | Case UI | AC-007 | MET-009..011 | DEMO-001 | Approved |
| FR-009 | Reset/replay | Challenger idea | scenarios | /api/v1/scenario-runs/* | Demo controls | AC-009 | MET-009 | DEMO-002 | Approved |
| FR-010 | Vendor-neutral LLM explanation | Conflict fix | explanation | alert detail | Alerts | AC-008 | MET-006 | DEMO-001 | Approved |
| FR-011 | Deterministic fallback | Conflict fix | explanation | alert detail | Alerts | AC-008 | MET-006 | DEMO-001 | Approved |
| FR-012 | False-positive scenario | Challenger idea | scenarios | scenarios | Demo | AC-009 | MET-005 | DEMO-001 | Approved |
| NFR-003 | Bad data reduces confidence | PDF | validation/fusion | data-quality | alerts | AC-006 | MET-008 | DEMO-001 | Approved |
| NFR-004 | Provider isolation | PDF | auth | all scoped APIs | all scoped UI | AC-011 | n/a | DEMO-001 | Approved |
| DATA-001 | Synthetic data only | PDF | scenario | scenarios | n/a | data review | n/a | DEMO-001 | Approved |
| SAFE-001 | No real financial activity | PDF | all | no execution API | no command UI | safety scan | n/a | DEMO-001 | Approved |
| SAFE-002 | No wrongdoing declaration | PDF | explanation | alerts | alerts | safety scan | MET-006 | DEMO-001 | Approved |
| DOC-001 | Exact prompt history | Audit | governance | n/a | n/a | CI check | n/a | n/a | Approved |
| QUALITY-001 | CI/Sonar before code | Audit | governance | n/a | n/a | CI | MET-012 | n/a | Approved |
| CI-001 | Runs on all pushed branches and PRs | Audit | governance | n/a | n/a | YAML validation | MET-012 | n/a | Approved |
