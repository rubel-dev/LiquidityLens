# Architecture

## Decision
Use a modular monolith. Microservices, Kafka, Redis/Upstash, separate provider deployments, and mandatory WebSockets are deferred.

## Package Layout
```text
backend/
  app/
    core/
    auth/
    providers/
    scenarios/
    validation/
    liquidity/
    anomaly/
    confidence/
    explanations/
    alerts/
    cases/
    audit/
    metrics/
    api/
    persistence/

frontend/
  src/
    app/
    features/
    components/
    lib/
    types/
```

## Dependency Rules
- API may call application services.
- Application services may call domain logic and repository interfaces.
- Domain logic must not depend on FastAPI, SQLAlchemy, or LLM vendors.
- Persistence implementations may depend on SQLAlchemy.
- UI must not implement financial decision logic.
- Explanation provider must not create or modify core risk decisions.
- Provider-scoped queries must receive an authorization context.

## Transaction Boundaries
| Service | Transaction Owner |
|---|---|
| Scenario execution | Scenario service owns scenario_run, generated synthetic records, and reset/replay state. |
| Alert creation | Alert service owns alert, evidence links, confidence snapshot, explanation record, and audit event. |
| Assignment | Case service owns assignment update, version increment, and audit event. |
| Acknowledgement | Case service owns idempotency check, acknowledgement event, version increment, and audit event. |
| Escalation | Case service owns escalation record, owner/status update, version increment, and audit event. |
| Case resolution | Case service owns final status, rationale, history event, version increment, and audit event. |
| Audit event creation | Audit service appends events in the same transaction as the triggering state change where possible. |

## Concurrency Policy
- Mutating case and alert actions require an idempotency key.
- Cases carry optimistic concurrency/version fields.
- Duplicate acknowledgement returns the existing acknowledgement result without appending duplicate history.
- Concurrent assignment with a stale version returns conflict and requires refresh.
- Case notes, status history, escalations, and audit events are append-only.

## Sync/Async Policy
- Core MVP request processing may be synchronous.
- Long scenario generation or explanation may use a simple in-process background task only if necessary.
- No Kafka, distributed queue, or mandatory WebSocket architecture for MVP.
- Explanation timeout or malformed output must use deterministic fallback.

## Domain Event Policy
Initial domain events are in-process records:
- FeedValidated
- LiquidityForecastCreated
- AnomalyFindingCreated
- AlertCreated
- AlertAcknowledged
- CaseEscalated
- CaseResolved

## High-Level Diagram
```mermaid
flowchart LR
  Browser["Browser"] --> FE["Next.js TypeScript frontend"]
  FE --> API["FastAPI modular monolith"]
  API --> PG[("PostgreSQL")]
  CI["GitHub Actions"] --> SQ["SonarQube"]
```

## Component Diagram
```mermaid
flowchart TB
  subgraph FE["Frontend"]
    AgentUI["Agent UI"]
    OpsUI["Operations UI"]
    RiskUI["Risk UI"]
  end
  subgraph BE["FastAPI modular monolith"]
    AuthN["Authentication"]
    AuthZ["RBAC + provider authorization"]
    Scenario["Scenario engine"]
    Providers["Provider adapters"]
    Validation["Validation"]
    Liquidity["Liquidity"]
    Anomaly["Anomaly"]
    Fusion["Confidence and decision fusion"]
    Explain["LLM explanation provider + fallback"]
    Alerts["Alerts"]
    Cases["Cases"]
    Audit["Audit"]
    Metrics["Metrics"]
    Logging["Logging"]
    Persistence["Persistence repositories"]
  end
  FE --> AuthN --> AuthZ
  AuthZ --> Scenario --> Providers --> Validation
  Validation --> Liquidity --> Fusion
  Validation --> Anomaly --> Fusion
  Fusion --> Explain --> Alerts --> Cases --> Audit
  Metrics --> Audit
  Persistence --> DB[("PostgreSQL")]
```

## Data Flow
```mermaid
flowchart TD
  Seed["Synthetic scenario seed"] --> Ingest["Provider ingestion"]
  Ingest --> Validate["Validation and quality"]
  Validate --> Forecast["Liquidity forecast"]
  Validate --> Finding["Anomaly finding"]
  Forecast --> Confidence["Confidence fusion"]
  Finding --> Confidence
  Confidence --> Explanation["Explanation or template fallback"]
  Explanation --> Alert["Advisory alert"]
  Alert --> Case["Case workflow"]
  Case --> Audit["Append-only audit"]
```

## Deployment Diagram
```mermaid
flowchart LR
  User["Judge/User browser"] --> Web["Next.js app"]
  Web --> App["FastAPI app"]
  App --> DB[("PostgreSQL")]
  GH["GitHub Actions"] --> SQ["SonarQube"]
```

## Authorization Flow
```mermaid
sequenceDiagram
  participant UI
  participant API
  participant AuthZ
  participant Service
  participant Repo
  UI->>API: Request with demo session
  API->>AuthZ: Resolve role and provider scope
  AuthZ->>Service: Authorized context
  Service->>Repo: Provider-scoped query
  Repo-->>Service: Scoped records
  Service-->>UI: Response or 403
```

## Alert/Case Sequence
```mermaid
sequenceDiagram
  participant Engine
  participant Alert
  participant Router
  participant Case
  participant Audit
  Engine->>Alert: Insight + evidence + confidence
  Alert->>Router: provider/area/severity
  Router->>Case: assign owner
  Case->>Audit: assignment
  Case->>Audit: acknowledgement/escalation/resolution
```

## Provider Isolation Enforcement
| Layer | Enforcement |
|---|---|
| API | Validate provider_id against user scope; return 403 on mismatch. |
| Service | Require authorized context for every provider-scoped operation. |
| Repository/query | Always filter by provider_id or parent provider scope. |
| UI | Hide out-of-scope provider records and actions; never rely on UI alone. |

## Safe LLM Boundary
The LLM explanation provider is vendor-neutral and cannot make core decisions. Deterministic rules produce forecasts/findings; deterministic templates handle LLM failure.

## Explanation Provider Interface
The explanation provider cannot create or modify forecasts, anomaly findings, severity, confidence, owner, or case state. It receives structured evidence after deterministic engines finish and returns advisory text only.

```python
class ExplanationProvider:
    def explain(self, request: ExplanationRequest) -> ExplanationResult: ...

class ExplanationRequest(TypedDict):
    language: Literal["bn", "banglish", "en"]
    alert_type: Literal["liquidity_shortage", "unusual_activity", "data_quality_degraded"]
    provider_code: str
    provider_display_name: str
    structured_evidence: dict[str, object]
    confidence_score: float
    uncertainty: list[str]
    safe_next_step: str

class ExplanationResult(TypedDict):
    text: str
    generated_by: Literal["llm", "deterministic_template"]
    provider_name: str
    timed_out: bool
```

Provider selection is controlled by `LLM_EXPLANATION_PROVIDER`:
- `none`: deterministic templates only.
- `openai`: OpenAI-compatible adapter, if a future secret is explicitly approved.
- `anthropic`: Anthropic-compatible adapter, if a future secret is explicitly approved.

MVP timeout policy: one attempt, maximum 3 seconds. No retry is required for MVP. Timeout, malformed output, unsafe wording, unsupported language, or disabled provider must trigger deterministic fallback (FR-011).
