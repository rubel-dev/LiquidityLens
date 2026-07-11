# Decision Log

| ID | Decision | Status | Rationale |
|---|---|---|---|
| DEC-001 | Modular monolith. | Accepted | Hackathon-feasible and avoids microservice overhead. |
| DEC-002 | Next.js TypeScript frontend. | Accepted | Fast typed web prototype. |
| DEC-003 | FastAPI Python backend. | Accepted | Strong fit for analytics and APIs. |
| DEC-004 | PostgreSQL, SQLAlchemy, Alembic. | Accepted | Relational auditability and migration path. |
| DEC-005 | Deterministic analytics for core decisions. | Accepted | Explainable and measurable. |
| DEC-006 | Vendor-neutral LLM explanation provider only for language/summaries. | Accepted | Resolves vendor conflicts. |
| DEC-007 | Deterministic template fallback. | Accepted | Safe degradation. |
| DEC-008 | One primary anomaly pattern for MVP. | Accepted | Prevents scope sprawl. |
| DEC-009 | Optional graph/network insight deferred. | Deferred | Not mandatory for golden flow. |
| DEC-010 | Redis/Upstash/Kafka/WebSockets not mandatory. | Deferred | Avoid excessive dependencies. |
| DEC-011 | CI and SonarQube before product code. | Accepted | Quality foundation. |
| DEC-012 | Prompt traceability per implementation/fix commit. | Accepted | Auditability. |

## Unresolved
- OPEN-001: Demo provider labels.
- OPEN-002: Hosting target.
- OPEN-003: Exact frontend test runner.
