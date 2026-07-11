# API Contracts

All paths use `/api/v1`. Contracts only; no routes are implemented in this step.

| Method | Path | Actor | Authorization | Provider Scope | Request | Validation | Response | Status Codes | Errors | Business Rules | Idempotency | Pagination | Concurrency |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GET | /api/v1/session | any | demo session | derived | none | session valid | session roles/scopes | 200,401 | error object | no real auth yet | n/a | n/a | n/a |
| GET | /api/v1/providers | ops/manager | RBAC | scoped | none | role valid | providers[] | 200,403 | error | no leakage | n/a | yes | n/a |
| GET | /api/v1/areas | ops/manager | RBAC | scoped | none | role valid | areas[] | 200,403 | error | area scope | n/a | yes | n/a |
| GET | /api/v1/agents | ops | RBAC | scoped | provider_id,area_id | scope valid | agents[] | 200,403 | error | filtered | n/a | yes | n/a |
| GET | /api/v1/agents/{agent_id}/overview | agent/ops | RBAC | scoped | agent_id | access valid | cash, balances, runway, alerts | 200,403,404 | error | cash separate | n/a | n/a | n/a |
| GET | /api/v1/agents/{agent_id}/cash-snapshots | agent/ops | RBAC | agent scoped | from,to | access valid | snapshots[] | 200,403 | error | not provider feed | n/a | yes | n/a |
| GET | /api/v1/provider-balance-snapshots | ops | RBAC | provider scoped | provider_id,agent_id,from,to | scope valid | snapshots[] | 200,403 | error | provider separate | n/a | yes | n/a |
| GET | /api/v1/transactions | ops/risk | RBAC | provider scoped | provider_id,agent_id,from,to | synthetic only | transactions[] | 200,403 | error | no phone-like IDs | n/a | yes | n/a |
| GET | /api/v1/data-quality-statuses | ops | RBAC | provider scoped | provider_id,run_id | scope valid | feed statuses[] | 200,403 | error | exposes stale/missing/conflict | n/a | yes | n/a |
| GET | /api/v1/liquidity-forecasts | agent/ops | RBAC | scoped | provider_id,agent_id | scope valid | forecasts[] | 200,403 | error | advisory only | n/a | yes | n/a |
| GET | /api/v1/anomaly-findings | ops/risk | RBAC | provider scoped | provider_id,agent_id | scope valid | findings[] | 200,403 | error | requires review only | n/a | yes | n/a |
| GET | /api/v1/alerts | agent/ops/risk | RBAC | scoped | provider_id,status,severity | scope valid | alerts[] | 200,403 | error | scoped list | n/a | yes | n/a |
| GET | /api/v1/alerts/{alert_id} | assigned roles | RBAC | scoped | alert_id | scope valid | alert,evidence,confidence,uncertainty,next_step | 200,403,404 | error | all important fields included | n/a | n/a | n/a |
| POST | /api/v1/alerts/{alert_id}/acknowledge | owner/ops | RBAC | scoped | actor,note | idempotency key | acknowledgement | 200,403,409 | error | no financial action | required | n/a | If-Match |
| POST | /api/v1/alerts/{alert_id}/assign | ops | RBAC | scoped | assignee | assignee valid | assignment | 200,403,409 | error | provider path only | required | n/a | If-Match |
| POST | /api/v1/alerts/{alert_id}/escalate | owner/ops | RBAC | scoped | target_role,reason | target valid | escalation | 200,403,409 | error | provider path only | required | n/a | If-Match |
| GET | /api/v1/cases | ops/risk | RBAC | scoped | provider_id,status | scope valid | cases[] | 200,403 | error | scoped | n/a | yes | n/a |
| GET | /api/v1/cases/{case_id} | assigned roles | RBAC | scoped | case_id | scope valid | case,notes,history | 200,403,404 | error | audit visible | n/a | n/a | n/a |
| POST | /api/v1/cases/{case_id}/notes | owner/risk | RBAC | scoped | note | non-empty | note | 201,403,409 | error | append-only | required | n/a | If-Match |
| POST | /api/v1/cases/{case_id}/resolve | owner/risk | RBAC | scoped | final_status,rationale | rationale required | case | 200,403,409 | error | final status visible | required | n/a | If-Match |
| GET | /api/v1/audit-events | ops/risk/manager | RBAC | scoped | entity,provider | scope valid | audit_events[] | 200,403 | error | append-only | n/a | yes | n/a |
| GET | /api/v1/scenarios | demo operator | RBAC | none | none | role valid | scenarios[] | 200,403 | error | synthetic only | n/a | yes | n/a |
| POST | /api/v1/scenarios/{scenario_id}/run | demo operator | RBAC | none | seed | scenario valid | run | 201,403 | error | deterministic | required | n/a | n/a |
| POST | /api/v1/scenario-runs/{run_id}/reset | demo operator | RBAC | none | none | run valid | reset status | 200,403 | error | no production data | required | n/a | n/a |
| POST | /api/v1/scenario-runs/{run_id}/replay | demo operator | RBAC | none | none | run valid | replay run | 201,403 | error | same seed | required | n/a | n/a |
| GET | /api/v1/metrics | manager/judge | RBAC | aggregate/scoped | run_id | role valid | metrics[] | 200,403 | error | formulas documented | n/a | yes | n/a |
| GET | /api/v1/health | system | none | none | none | none | status | 200 | error | liveness | n/a | n/a | n/a |
| GET | /api/v1/readiness | system | none | none | none | checks | status,checks | 200,503 | error | readiness | n/a | n/a | n/a |

## Response Schema Reference
Detailed response shapes are defined in `docs/06b-api-schemas.md`. Endpoint implementation must keep `/api/v1` responses compatible with those schemas or update the schema document in a traceable governance commit before frontend/backend parallel work begins.

Provider ingestion and validation currently expose internal Python service interfaces only. Public REST ingestion endpoints remain out of scope until the approved backend API module begins.
