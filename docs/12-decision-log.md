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
| DEC-013 | Demo providers use synthetic labels representing three logically separate providers; real-style names may appear only in narrative if legally appropriate. | Accepted | Preserves provider separation and avoids unsupported affiliation claims. |
| DEC-014 | Frontend test runner target is Vitest with React Testing Library after Next.js scaffold. | Accepted | Common TypeScript/Next.js testing path. |
| DEC-015 | Canonical development/demo deployment is local Docker Compose. | Accepted | Removes cloud dependency from MVP readiness. |
| DEC-016 | Optional cloud deployment target may be selected later; it is not mandatory for MVP. | Accepted | Keeps implementation feasible. |

## Remaining Open Item
- Final public demo hosting provider remains open; local Docker Compose is canonical until this is decided.
