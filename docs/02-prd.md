# Product Requirements Document

## Product Vision
Make a complex multi-provider agent situation simple to understand by connecting liquidity insight, unusual-activity evidence, confidence, and clear coordination without unsafe integration or accusations.

## Problem Definition
Agents have one shared cash drawer and separate provider e-money balances. Total value can look healthy while a specific provider or shared cash reserve is close to shortage.

## Personas
| Persona | Need |
|---|---|
| Agent | Understand provider runway and shared cash pressure. |
| Provider operations | Own and coordinate important alerts. |
| Field officer | Acknowledge and act through approved provider channels. |
| Risk reviewer | Review unusual activity with evidence and uncertainty. |
| Manager/judge | See metrics, traceability, and responsible design. |

## Given/When/Then Acceptance Criteria
| ID | Requirement IDs | Given | When | Then |
|---|---|---|---|---|
| AC-001 | FR-001,FR-002 | A scenario has shared cash and provider balances. | The overview opens. | Shared cash and each provider balance are shown separately. |
| AC-002 | FR-003 | Total value is above threshold but one provider is low. | The deceptive-total widget renders. | The aggregate appears healthy while the provider risk is highlighted. |
| AC-003 | FR-004 | Transactions imply depletion. | Liquidity analysis runs. | Provider and shared-cash runway clocks show estimated shortage times. |
| AC-004 | FR-005,FR-006 | Synthetic transactions contain repeated amounts and abnormal velocity. | Anomaly detection runs. | Evidence fingerprint shows amounts, velocity, concentration, time-window, and baseline deviation. |
| AC-005 | SAFE-002 | An unusual pattern is shown. | Alert text is generated. | It uses "unusual" or "requires review" and never declares wrongdoing. |
| AC-006 | NFR-003 | A feed is missing, delayed, stale, or conflicting. | Forecasts render. | Confidence is visibly reduced and safe fallback text is shown. |
| AC-007 | FR-007,FR-008 | Important alert exists. | Routing runs. | Receiver, owner, next step, status, assignment, acknowledgement, escalation, notes, and final status are auditable. |
| AC-008 | FR-010,FR-011 | LLM is unavailable or malformed. | Explanation is requested. | Deterministic Bengali/Banglish/English template fallback is used. |
| AC-009 | FR-012 | Normal Eid/salary-day spike is replayed. | Detection runs. | The pattern is consistent with expected demand; no additional review is currently recommended. |
| AC-010 | MET-001, MET-002, MET-003, MET-004, MET-005, MET-006, MET-007, MET-008, MET-009, MET-010, MET-011, MET-012 | Demo scenarios run. | Metrics report opens. | Formulas, targets, and evidence sources are shown. |
| AC-011 | NFR-004 | User requests another provider's restricted data. | API/service/query/UI checks run. | Access is denied and audited. |

## Demo Scope
Story starts normal, pressure increases, system explains, alert is assigned, case is reviewed, resolution is recorded, and reset/replay proves repeatability.

## Out of Scope
Redis/Upstash, Kafka, microservices, mandatory WebSockets, separate provider deployments, network graph, Gantt timeline, sound alerts, complex model-learning feedback loops, more than one primary anomaly pattern, production-scale claims.

## Known Limitations
Metrics are based on synthetic scenarios. The prototype is not production risk tooling and does not integrate with real provider systems.

