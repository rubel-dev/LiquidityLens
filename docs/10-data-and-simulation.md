# Data and Simulation

## Scenarios
- SCN-001: Hidden provider shortage and deceptive total.
- SCN-002: Liquidity pressure plus unusual activity.
- SCN-003: Missing, delayed, stale, or conflicting provider data.
- SCN-004: Coordinated response and closure.
- SCN-005: Normal Eid or salary-day spike.

## Implemented Canonical Scenario Catalog
| Code | Scenario | Ground truth intent |
|---|---|---|
| `normal_day` | Scenario A - Normal Day | `normal`; no injected shortage or review recommendation |
| `eid_rush` | Scenario B - Eid Rush | legitimate demand spike; false-positive evaluation |
| `hidden_provider_shortage` | Scenario C - Hidden Provider Shortage | provider-specific liquidity pressure without balance merging |
| `shared_cash_crisis` | Scenario D - Shared Cash Crisis | shared physical cash pressure |
| `liquidity_pressure_unusual_activity` | Scenario E - Liquidity Pressure with Unusual Activity | unusual repeated amounts, velocity, and account concentration; human review, not proof |
| `salary_day_legitimate_spike` | Scenario F - Salary-Day Legitimate Spike | legitimate demand spike; false-positive evaluation |
| `delayed_feed` | Scenario G - Delayed Feed | delayed/stale feed quality |
| `missing_feed` | Scenario H - Missing Feed | missing feed and unknown/null balance |
| `conflicting_balance` | Scenario I - Conflicting Balance | intentional balance conflict requiring review |
| `agent_unavailable` | Scenario J - Agent Unavailable | service-continuity risk for future coordination modules |

## Synthetic Identifier Policy
Use IDs like `SIM-CUST-0001`, not phone-number-like values. Never use real names, phone numbers, NIDs, wallet IDs, or balances.

The implemented generator rejects phone-number-like identifiers such as `017...`, `018...`, `019...`, and `+880...`. Generated transaction references include the synthetic run number, for example `SIM-TXN-000001-000001`, so separate scenario runs do not collide while replaying the same run remains deterministic.

## Seed and Fingerprint Policy
Every run uses a scenario code, seed, explicit start timestamp, scenario definition version, catalog version, generator version, and profile (`small`, `medium`, or `demo`). The same values must reproduce the same dataset fingerprint. The current generator version is `scenario-generator-v1`; the current catalog version is `scenario-catalog-v1`.

Run metadata, generated counts, fingerprint, and ground-truth summary are stored as machine-readable `audit_events` tied to the `scenario_runs` row. Ground-truth events are labels for evaluation only and must not declare fraud or wrongdoing.

## Accounting Convention
| Transaction | Shared physical cash | Provider e-money balance |
|---|---:|---:|
| Cash-in | increases | decreases |
| Cash-out | decreases | increases |

The module records safe synthetic source data only. It does not forecast liquidity, detect anomalies, create alerts, open cases, move funds, transfer value across providers, freeze/block accounts, or execute provider operations.

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

Implemented reset/replay currently applies to scenario-owned inputs and ground-truth audit records only. Downstream findings, alerts, cases, explanations, and metrics remain out of scope until those modules exist.
