# Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| RISK-001 | Provider balances appear merged. | Separate visual, API, service, and query boundaries. |
| RISK-002 | Unusual activity is interpreted as wrongdoing. | Careful language, uncertainty, human review. |
| RISK-003 | Real-looking identifiers appear in demo. | Synthetic non-phone-like IDs only. |
| RISK-004 | Bad data creates confident advice. | Degrade confidence and show fallback. |
| RISK-005 | SonarQube secrets missing. | Official workflow fails secret validation instead of silently passing. |
| RISK-006 | Optional scope distracts from MVP. | Defer graph, sound, WebSockets, Redis, microservices. |
