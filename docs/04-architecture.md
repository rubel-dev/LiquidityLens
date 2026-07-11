# Architecture

## Decision
Use a modular monolith. Microservices, Kafka, Redis/Upstash, separate provider deployments, and mandatory WebSockets are deferred.

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
