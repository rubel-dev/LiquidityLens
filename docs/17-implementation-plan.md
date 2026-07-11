# Implementation Plan

| Phase | Module | Status |
|---|---|---|
| 0 | Governance, prompt validation, CI, SonarQube | Configured |
| 1 | Repository foundation | Implemented |
| 2 | Database schema and migrations | Implemented |
| 3 | Synthetic scenario engine | Pending |
| 4 | Provider ingestion and validation | Pending |
| 5 | Liquidity engine | Pending |
| 6 | Anomaly engine | Pending |
| 7 | Confidence and decision fusion | Pending |
| 8 | Explanation service and fallback | Pending |
| 9 | Alerts and cases | Pending |
| 10 | Authentication and provider-scope authorization | Pending |
| 11 | Backend APIs | Pending |
| 12 | Agent UI | Pending |
| 13 | Operations UI | Pending |
| 14 | Risk UI | Pending |
| 15 | Metrics and observability | Pending |
| 16 | Integration and failure testing | Pending |
| 17 | Demo packaging | Pending |
| 18 | Release preparation | Pending |

```mermaid
flowchart TD
  P0["0 Governance/CI/Sonar"] --> P1["1 Repository foundation"]
  P1 --> P2["2 DB schema/migrations"]
  P2 --> P3["3 Scenario engine"]
  P3 --> P4["4 Provider ingestion/validation"]
  P4 --> P5["5 Liquidity"]
  P4 --> P6["6 Anomaly"]
  P5 --> P7["7 Confidence fusion"]
  P6 --> P7
  P7 --> P8["8 Explanation/fallback"]
  P8 --> P9["9 Alerts/cases"]
  P9 --> P10["10 Auth/provider scope"]
  P10 --> P11["11 APIs"]
  P11 --> P12["12 Agent UI"]
  P11 --> P13["13 Ops UI"]
  P11 --> P14["14 Risk UI"]
  P12 --> P15["15 Metrics"]
  P13 --> P15
  P14 --> P15
  P15 --> P16["16 Failure tests"]
  P16 --> P17["17 Demo packaging"]
  P17 --> P18["18 Release"]
```
