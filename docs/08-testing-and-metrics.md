# Testing and Metrics

## Metrics Registry
| ID | Name | Formula | Dataset | Ground Truth | Target | Evidence Source | Limitation |
|---|---|---|---|---|---|---|---|
| MET-001 | Shortage detection lead time | actual_shortage_at - alert_created_at | SCN-001/002 | injected shortage | >= 30 min | metrics report | synthetic |
| MET-002 | Forecast error | abs(predicted_shortage_at - actual_shortage_at) | SCN-001/002 | injected shortage | <= 20 min median | forecast report | synthetic |
| MET-003 | Anomaly precision | TP/(TP+FP) | SCN-002/005 | injected labels | >= 0.80 | anomaly report | synthetic |
| MET-004 | Anomaly recall | TP/(TP+FN) | SCN-002 | injected labels | >= 0.80 | anomaly report | synthetic |
| MET-005 | False-positive rate | FP/normal_cases | SCN-005 | expected demand labels | <= 0.20 | false-positive report | limited scenarios |
| MET-006 | Explanation coverage | alerts_with_reason_evidence_confidence_uncertainty_next_step / important_alerts | all alerts | alert registry | 100% | explanation report | text quality reviewed manually |
| MET-007 | API p50/p95 latency | percentile(response_ms, 50/95) | smoke/load | timing logs | p95 <= 500ms demo | latency report | demo infra |
| MET-008 | Missing-feed fallback correctness | correct_fallbacks / missing_feed_cases | FAIL-001 | expected fallback | 100% | fallback tests | fixture dependent |
| MET-009 | Case lifecycle completion | completed_required_steps / required_steps | SCN-004 | golden script | 100% | workflow report | may include manual demo |
| MET-010 | Alert acknowledgement time | acknowledged_at - alert_created_at | SCN-004 | audit events | documented target before demo | audit report | role-dependent |
| MET-011 | Resolution time | resolved_at - alert_created_at | SCN-004 | audit events | documented target before demo | audit report | role-dependent |
| MET-012 | SonarQube Quality Gate | pass/fail | CI | SonarQube | pass before accepted completion | CI link | not local |

## Required Difficult Tests
Late data, missing data, stale data, conflicting balance, duplicate event, out-of-order transactions, invalid amount, zero activity, extreme demand, normal Eid spike, unauthorized cross-provider access, duplicate acknowledgement, concurrent assignment, LLM unavailable, malformed LLM output, reset/replay determinism.

## Implemented Scenario Engine Tests
Local PostgreSQL-backed tests cover deterministic generation, different-seed variation, timezone-aware start timestamps, synthetic identifier rejection, provider separation, shared-cash independence, positive transaction amounts, unique transaction IDs, legitimate Eid/salary false-positive fixtures, unusual repeated-amount/velocity/account-concentration labels, delayed/missing/conflicting feeds, transaction rollback, reset scope, replay fingerprint stability, duplicate run IDs, duplicate transaction IDs, and demo-profile generation timing.

Latest local evidence:
- Backend test suite from `backend/`: `39 passed`, coverage `90.23%`.
- PostgreSQL database: `hacathon_db` using `postgresql+psycopg://postgres:12345@localhost:5432/hacathon_db`.
- Scenario CLI smoke: list, run, replay, and reset succeeded for `SIM-RUN-990001`.
- Demo profile generation threshold: integration test requires completion below 5 seconds in the local environment.
- Whole-backend Ruff format/check and MyPy now pass locally after validation closeout cleanup.

## Implemented Validation Metrics Evidence
Latest local backend evidence for provider ingestion and validation:
- Required Git Bash closeout chain from `backend/`: Ruff format check passed, Ruff lint passed, MyPy strict check passed, Pytest passed, coverage XML generated.
- Backend test suite from `backend/`: `70 passed`, coverage `89.49%`.
- Validation-specific tests collected: `31`.
- Valid transaction persistence: accepted once; duplicate retry returned `duplicate_ignored` and did not create a second trusted row.
- Invalid transaction persistence: zero-amount record was rejected, produced quality evidence, and created no trusted transaction row.
- Missing balance correctness: nullable provider balance persisted as `NULL`, not zero.
- Feed quality correctness: delayed feed produced a warning; missing feed and conflicting balance produced quarantined evidence; `provider_feed_statuses`, `data_quality_events`, and audit evidence persisted.
- Sequence quality correctness: incoming source sequence is compared to the latest accepted source sequence and true gaps produce warning evidence.
- Provider-boundary correctness: provider adapters map only provider transaction, provider balance, and provider feed status records; shared cash remains provider-independent.
- Scenario integration: generated scenario transactions validated without reading ground-truth labels.
- Demo-sized validation latency: integration test ingests 40 records under a 5 second local threshold.
- Measured validation latency: 100 accepted transaction ingestions averaged `12.376 ms`; p95 was `20.776 ms`.

Data-quality score scale is `0.00` to `1.00`; quality levels are `high`, `medium`, `low`, and `unusable`. This is a deterministic, rule-based data-quality score, not calibrated model confidence and not machine learning. The score subtracts explainable category penalties and returns an explicit `confidence_multiplier` for future confidence fusion without calculating liquidity/anomaly confidence itself. Duplicate records are dispositioned as `duplicate_ignored` and receive a quality penalty so they do not appear as fully clean trusted new data.

## Confidence Fusion Algorithm
The MVP confidence score starts at `1.00` for a forecast/finding with complete valid input and subtracts data-quality and evidence deductions. It is clamped to `[0.00, 1.00]`.

| Signal | Deduction |
|---|---:|
| Missing provider feed | 0.40 |
| Stale provider feed older than 10 minutes | 0.20 |
| Conflicting provider balance snapshots | 0.30 |
| Duplicate or invalid records in active window | 0.10 |
| Missing baseline for comparison | 0.15 |
| LLM unavailable but deterministic template used | 0.00 |

Display tiers:
- HIGH: score >= 0.75
- MEDIUM: 0.50 <= score < 0.75
- LOW: score < 0.50

If confidence is below `0.40`, UI and API responses must show `Insufficient data - no confident forecast` and must not create a high-confidence alert from that signal alone.
