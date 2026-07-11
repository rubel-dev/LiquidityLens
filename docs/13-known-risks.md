# Known Risks

| ID | Risk | Mitigation |
|---|---|---|
| RISK-001 | Provider balances appear merged. | Separate visual, API, service, and query boundaries. |
| RISK-002 | Unusual activity is interpreted as wrongdoing. | Careful language, uncertainty, human review. |
| RISK-003 | Real-looking identifiers appear in demo. | Synthetic non-phone-like IDs only. |
| RISK-004 | Bad data creates confident advice. | Degrade confidence and show fallback. |
| RISK-005 | SonarQube secrets, hosted service, Quality Gate, or integration configuration may fail during the hackathon. | Treat SonarQube as best-effort and non-blocking per judge instruction; continue attempting analysis when practical; record Passed, Failed, Skipped, Unavailable, or Configuration Error honestly with error summary, likely cause, attempts made, known code-quality risk, and local fallback checks. |
| RISK-006 | Optional scope distracts from MVP. | Defer graph, sound, WebSockets, Redis, microservices. |
| RISK-007 | Remote static analysis unavailable may hide code-quality issues that local tools miss. | Require local formatter, linter, type checker, unit tests, integration tests, coverage, governance validation, requirement-ID validation, prompt traceability, and security/safety validation where applicable. |
