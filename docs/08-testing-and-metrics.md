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
