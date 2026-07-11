# Requirements

## Requirement Registry
| ID | Requirement | Priority |
|---|---|---|
| FR-001 | Show shared physical cash separately from provider e-money balances. | Mandatory |
| FR-002 | Show at least two logically separate simulated providers and support three where practical. | Mandatory |
| FR-003 | Show deceptive-total state when total value appears healthy but one provider is near shortage. | Mandatory |
| FR-004 | Show provider-specific and shared-cash runway clocks with estimated shortage time. | Mandatory |
| FR-005 | Detect repeated or near-identical cash-out amounts combined with abnormal transaction velocity from a small synthetic account group. | Mandatory |
| FR-006 | Show evidence fingerprint: repeated amounts, velocity, concentrated group, time-window deviation, baseline deviation. | Mandatory |
| FR-007 | Show reason, evidence, confidence, uncertainty, owner, recommended next step, and status for important alerts. | Mandatory |
| FR-008 | Route, assign, acknowledge, escalate, review, resolve, and close important cases. | Mandatory |
| FR-009 | Support demo reset and replay. | Mandatory |
| FR-010 | Provide Bengali, Banglish, and English explanation support through a vendor-neutral LLM provider abstraction. | Recommended |
| FR-011 | Use deterministic explanation templates when LLM is unavailable or malformed. | Mandatory |
| FR-012 | Include normal Eid or salary-day spike scenario that does not automatically become a review case. | Mandatory |
| NFR-001 | Dashboard and alert interactions should be responsive under demo data volume. | Mandatory |
| NFR-002 | High-impact alerts must be explainable and auditable. | Mandatory |
| NFR-003 | Missing, delayed, stale, malformed, or conflicting data must reduce confidence. | Mandatory |
| NFR-004 | Provider isolation must be enforced at API, service, repository/query, and UI layers. | Mandatory |
| DATA-001 | Use synthetic, mock, anonymized, or safe public data only. | Mandatory |
| DATA-002 | Account identifiers must be synthetic and not phone-number-like real identities. | Mandatory |
| DATA-003 | Shared physical cash must not be modeled as a provider feed. | Mandatory |
| ARCH-001 | Use modular monolith architecture. | Mandatory |
| ARCH-002 | Do not use microservices for MVP. | Mandatory |
| API-001 | Use versioned `/api/v1` contracts. | Mandatory |
| DB-001 | Use PostgreSQL with SQLAlchemy and Alembic. | Mandatory |
| SEC-001 | Do not store credentials, PINs, OTPs, passwords, private keys, or real customer identities. | Mandatory |
| SAFE-001 | Do not execute real financial activity. | Mandatory |
| SAFE-002 | Do not declare wrongdoing or present anomaly scores as proof. | Mandatory |
| SAFE-003 | Recommendations must be advisory, e.g. coordinate approved support through responsible provider operations. | Mandatory |
| MET-001 | Measure shortage detection lead time. | Mandatory |
| MET-002 | Measure forecast error. | Mandatory |
| MET-003 | Measure anomaly precision. | Mandatory |
| MET-004 | Measure anomaly recall. | Mandatory |
| MET-005 | Measure false-positive rate. | Mandatory |
| MET-006 | Measure explanation coverage. | Mandatory |
| MET-007 | Measure API p50 and p95 latency. | Mandatory |
| MET-008 | Measure missing-feed fallback correctness. | Mandatory |
| MET-009 | Measure case lifecycle completion rate. | Mandatory |
| MET-010 | Measure alert acknowledgement time. | Mandatory |
| MET-011 | Measure resolution time. | Mandatory |
| MET-012 | Track SonarQube Quality Gate status. | Mandatory |
| DOC-001 | Every implementation or fix commit must include exact prompt history. | Mandatory |
| DOC-002 | Maintain commit ledger. | Mandatory |
| DOC-003 | Maintain requirement traceability. | Mandatory |
| QUALITY-001 | Configure CI and SonarQube before product code. | Mandatory |
| QUALITY-002 | Validate Prompt-ID, Requirement-IDs, Module, Tests, and matching prompt file in CI. | Mandatory |
| CI-001 | Run CI and SonarQube on every pushed branch and PRs to main. | Mandatory |
| CI-002 | Use only secret names SONAR_TOKEN, SONAR_HOST_URL, SONAR_PROJECT_KEY. | Mandatory |
| DEMO-001 | Demonstrate story-driven golden flow from normal state through resolution. | Mandatory |
| DEMO-002 | Demonstrate reset and replay. | Mandatory |

## Scenario IDs
| ID | Scenario |
|---|---|
| SCN-001 | Hidden provider shortage and deceptive total. |
| SCN-002 | Liquidity pressure plus unusual activity. |
| SCN-003 | Missing, delayed, stale, or conflicting provider data. |
| SCN-004 | Coordinated response and closure. |
| SCN-005 | Normal Eid or salary-day spike. |

## Failure IDs
| ID | Failure |
|---|---|
| FAIL-001 | Missing feed. |
| FAIL-002 | Stale feed. |
| FAIL-003 | Conflicting balance. |
| FAIL-004 | Duplicate event. |
| FAIL-005 | Concurrent case update. |
| FAIL-006 | Unauthorized provider access. |
| FAIL-007 | LLM unavailable or malformed output. |

## Open Decisions
| ID | Question |
|---|---|
| OPEN-001 | Final demo provider labels: real-style names or Provider A/B/C. |
| OPEN-002 | Final hosting target. |
| OPEN-003 | Exact frontend test runner after scaffold. |
