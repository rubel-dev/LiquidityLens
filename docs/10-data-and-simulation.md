# Data and Simulation

## Scenarios
- SCN-001: Hidden provider shortage and deceptive total.
- SCN-002: Liquidity pressure plus unusual activity.
- SCN-003: Missing, delayed, stale, or conflicting provider data.
- SCN-004: Coordinated response and closure.
- SCN-005: Normal Eid or salary-day spike.

## Synthetic Identifier Policy
Use IDs like `SIM-CUST-0001`, not phone-number-like values. Never use real names, phone numbers, NIDs, wallet IDs, or balances.

## Evidence Fingerprint
Each anomaly finding should summarize repeated/near-identical amounts, abnormal velocity, concentrated synthetic group, time-window deviation, and baseline deviation.

## Rule Configuration
The MVP primary anomaly rule is `near_identical_cash_out_velocity`. It must be deterministic and versioned in `rule_versions.config`.

Default parameters:
- `amount_similarity_pct`: `2.0` means amounts within +/-2% are near-identical.
- `rolling_window_minutes`: `30`.
- `velocity_multiplier`: `3.0` means the current window count must exceed 3x baseline.
- `minimum_cash_out_count`: `5` events in the window.
- `maximum_synthetic_group_size`: `5` unique synthetic customer references.
- `baseline_window_days`: `7` prior synthetic days.
- `minimum_confidence_to_alert`: `0.50`.
- `review_severity_threshold`: `medium`.

`rule_versions.config` JSON schema:
```json
{
  "rule_name": "near_identical_cash_out_velocity",
  "amount_similarity_pct": 2.0,
  "rolling_window_minutes": 30,
  "velocity_multiplier": 3.0,
  "minimum_cash_out_count": 5,
  "maximum_synthetic_group_size": 5,
  "baseline_window_days": 7,
  "minimum_confidence_to_alert": 0.5,
  "review_severity_threshold": "medium"
}
```

SCN-002 is the positive ground-truth fixture for MET-003 and MET-004. SCN-005 is the expected-demand false-positive fixture and must not automatically create a suspicious case.

## Reset Scope
Demo reset is scoped to a scenario run. It must never delete static reference data or rule versions.

| Table | On reset |
|---|---|
| `scenario_runs`, `transactions`, `provider_balance_snapshots`, `shared_cash_snapshots`, `alerts`, `cases`, `case_notes`, `case_status_history`, `escalations`, `audit_events`, `anomaly_findings`, `liquidity_forecasts`, `evidence_items`, `explanation_records`, `human_feedback`, `metric_observations`, `data_quality_events`, `provider_feed_statuses`, `confidence_assessments` | Delete rows for the selected run only. |
| `scenarios`, `providers`, `areas`, `agents`, `agent_provider_accounts`, `users`, `roles`, `user_role_assignments`, `rule_versions` | Preserve. |

Clean state means replaying the same scenario ID and seed generates the same synthetic inputs, expected findings, metrics, and story checkpoints.
