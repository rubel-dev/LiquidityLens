# Implementation Plan

| Phase | Module | Status |
|---|---|---|
| 0 | Governance, prompt validation, CI, SonarQube | Configured |
| 1 | Repository foundation | Implemented |
| 2 | Database schema and migrations | Verified locally |
| 3 | Synthetic scenario engine | Implemented |
| 4 | Provider ingestion and validation | Implemented |
| 5 | Liquidity engine | Not Started |
| 6 | Anomaly engine | Not Started |
| 7 | Confidence and decision fusion | Not Started |
| 8 | Explanation service and fallback | Not Started |
| 9 | Alerts and cases | Not Started |
| 10 | Authentication and provider-scope authorization | Not Started |
| 11 | Backend APIs | Not Started |
| 12 | Agent UI | Implemented with demo fixtures; API integration pending |
| 13 | Operations UI | Implemented with demo fixtures; API integration pending |
| 14 | Risk UI | Implemented with demo fixtures; API integration pending |
| 15 | Metrics and observability | Frontend surface implemented; backend pending |
| 16 | Integration and failure testing | Frontend verified; backend pending |
| 17 | Demo packaging | Not Started |
| 18 | Release preparation | Not Started |

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
