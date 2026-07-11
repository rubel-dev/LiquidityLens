# Implementation Plan

| Phase | Module |
|---|---|
| 0 | Governance, prompt validation, CI, SonarQube |
| 1 | Repository foundation |
| 2 | Database schema and migrations |
| 3 | Synthetic scenario engine |
| 4 | Provider ingestion and validation |
| 5 | Liquidity engine |
| 6 | Anomaly engine |
| 7 | Confidence and decision fusion |
| 8 | Explanation service and fallback |
| 9 | Alerts and cases |
| 10 | Backend APIs |
| 11 | Authentication and provider-scope authorization |
| 12 | Agent UI |
| 13 | Operations UI |
| 14 | Risk UI |
| 15 | Metrics and observability |
| 16 | Integration and failure testing |
| 17 | Demo packaging |
| 18 | Release preparation |

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
  P9 --> P10["10 APIs"]
  P10 --> P11["11 Auth/provider scope"]
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
