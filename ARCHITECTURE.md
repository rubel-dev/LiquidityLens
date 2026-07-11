# System Architecture — Multi-Provider Agent Liquidity Dashboard
**Codex Community Hackathon — bKash x SUST CSE Carnival 2026**

---

## High-Level Overview

```
┌──────────────────────────────────────────────────────┐
│                   FRONTEND (Next.js)                 │
│   Agent View │ Ops Dashboard │ Alert Manager         │
└──────────────────────┬───────────────────────────────┘
                       │  REST API + WebSocket
┌──────────────────────▼───────────────────────────────┐
│              API GATEWAY (FastAPI / Python)           │
│   /agents  /balances  /alerts  /cases  /analytics    │
└─────┬──────────────┬────────────────┬────────────────┘
      │              │                │
┌─────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
│   Mock     │ │ Analytics  │ │  AI Service │
│  Provider  │ │  Engine    │ │  (Claude)   │
│    APIs    │ │ (Python)   │ │             │
└─────┬──────┘ └─────┬──────┘ └──────┬──────┘
      │              │                │
┌─────▼──────────────▼────────────────▼──────┐
│         PostgreSQL  +  Redis               │
└─────────────────────────────────────────────┘
```

---

## Layer-by-Layer Breakdown

### 1. Mock Provider APIs (Simulated Data Layer)

Three separate mock services — one per provider — each with its own data boundary.

```
/provider/bkash/balance
/provider/bkash/transactions
/provider/nagad/balance
/provider/nagad/transactions
/provider/rocket/balance
/provider/rocket/transactions
```

- Written in FastAPI (in-memory or seeded from synthetic dataset)
- Simulate delayed/missing/conflicting data for **Scenario C**
- Each provider returns only its own data — no cross-provider leakage
- Synthetic data generator seeds realistic patterns: Eid spikes, velocity anomalies, normal salary-day demand

---

### 2. Core Backend (FastAPI)

| Module | Responsibility |
|--------|----------------|
| `balance_aggregator` | Polls all 3 mock providers every 30s, stores snapshots, preserves provider boundaries |
| `liquidity_engine` | Forecasts time-to-empty for physical cash and each provider e-money balance |
| `anomaly_detector` | Runs detection rules on the transaction stream |
| `alert_router` | Creates alerts, assigns owner based on alert type, provider, and severity |
| `case_manager` | Tracks alert lifecycle: open → acknowledged → escalated → resolved |
| `ai_explainer` | Calls Claude API to generate Bengali/Banglish/English alert descriptions |

---

### 3. Analytics Engine (Python — inside backend)

#### Liquidity Forecasting

```
depletion_time = current_balance / avg_outflow_rate_last_30min
confidence     = "low"  if data_age > 5 minutes
               = "medium" if data_age > 2 minutes
               = "high" otherwise
```

Outputs per provider and for shared physical cash:
- Estimated time to shortage (minutes)
- Confidence level
- Recommended minimum top-up amount

#### Anomaly Detection — 3 Detectors

| Detector | What It Catches | Signal |
|----------|----------------|--------|
| **Velocity Check** | Too many transactions in a short window (e.g. >10 cash-outs in 12 min) | Count per time window vs. rolling baseline |
| **Amount Clustering** | Multiple transactions with near-identical amounts (within ±50 BDT) | Histogram bin concentration |
| **Account Concentration** | Same 2–3 account IDs appearing repeatedly in a short period | Unique-account ratio per window |

Each detector returns:
```json
{
  "flagged": true,
  "reason": "8 near-identical cash-out amounts in 12 minutes",
  "evidence": [...],
  "confidence": 0.73,
  "suggested_action": "Human review before next rebalance"
}
```

> **Important:** Anomaly flags use careful language — "unusual", "requires review" — never "fraud" or "blocked".

---

### 4. AI Service (Claude API)

Used as the **mandatory AI component** for:
- Generating Bengali / Banglish / English alert messages from structured data
- Explaining anomaly evidence in plain, stakeholder-appropriate language
- Suggesting safe next steps per role (agent vs. field officer vs. risk analyst)

**Model:** `claude-haiku-4-5-20251001` (fast, low-cost, sufficient for alert generation)

**Example prompt:**
```
An agent has 4,200 BDT in bKash e-money balance.
Average cash-out rate is 1,800 BDT/hour.
Predicted shortage in 38 minutes.
Generate a short Bengali alert for the agent.
Use careful, advisory language. Do not make financial decisions.
```

**Example output (Bengali):**
> বর্তমান লেনদেনের ধারা অনুযায়ী আনুমানিক ৩৮ মিনিটের মধ্যে আপনার বিকাশ ব্যালেন্স শেষ হয়ে যেতে পারে। নিরাপদভাবে সেবা চালু রাখতে প্রয়োজনীয় ব্যবস্থা নিন।

---

### 5. Database Schema (PostgreSQL)

```sql
-- Core entities
agents (
  id, name, area, physical_cash, last_updated
)

provider_balances (
  id, agent_id, provider,       -- "bkash" | "nagad" | "rocket"
  balance, fetched_at,
  data_quality                  -- "ok" | "delayed" | "missing" | "conflict"
)

transactions (
  id, agent_id, provider,
  type,                         -- "cash_in" | "cash_out" | "send" | "receive"
  amount, account_id,
  timestamp, status
)

-- Alert and coordination
alerts (
  id, agent_id, provider,
  type,                         -- "liquidity" | "anomaly" | "data_quality"
  severity,                     -- "low" | "medium" | "high"
  message_en, message_bn,
  evidence_json, confidence,
  owner_role, status,           -- "open" | "acknowledged" | "escalated" | "resolved"
  created_at
)

cases (
  id, alert_id,
  assigned_to,
  acknowledged_at,
  escalated_at,
  resolved_at,
  notes
)
```

**Cache (Redis):**
- Latest balance snapshots per agent/provider (fast dashboard reads)
- Alert pub/sub channel for WebSocket push

---

### 6. Frontend (Next.js + Tailwind + shadcn/ui)

#### Three Views

| View | Users | Key Components |
|------|-------|---------------|
| **Agent Dashboard** | Agent / outlet | Cash meter, 3 provider balance bars, shortage countdown, active alerts in Bengali |
| **Operations Dashboard** | Field Officer / Ops Team | Agent list with risk color-coding, alert queue, filter by provider / area / time |
| **Case Manager** | Ops + Risk Analyst | Alert detail, evidence panel, alert history, assign / escalate / resolve buttons, Bengali explanation |

#### Real-Time Updates
- WebSocket push for new alerts (primary)
- 30-second polling fallback if WebSocket unavailable

#### Data Quality Indicators
- Green badge: data fresh
- Yellow badge: data delayed (>2 min)
- Red badge: data missing — confidence downgraded, no confident recommendation shown

---

### 7. Complete Alert Data Flow

```
1.  Synthetic transactions stream in via mock provider APIs
2.  balance_aggregator polls providers every 30 seconds
3.  liquidity_engine detects: bKash balance → empty in ~38 min
4.  anomaly_detector flags: 8 near-identical cash-outs in 12 min from 2 accounts
5.  alert_router creates alert → severity = HIGH → assigns to "bKash Field Officer"
6.  ai_explainer calls Claude API → generates Bengali + English messages
7.  Redis pub/sub pushes alert → WebSocket delivers to Operations Dashboard
8.  Field Officer sees alert, clicks Acknowledge → case_manager logs timestamp
9.  Officer decides to escalate to Risk Analyst → case updated, new owner set
10. Risk Analyst reviews evidence, adds case note, resolves or escalates further
11. Resolution recorded → alert status = resolved → visible on all dashboards
```

---

### 8. Four Demo Scenarios Coverage

| Scenario | How It's Demonstrated |
|----------|----------------------|
| **A — Hidden provider shortage** | bKash balance low while aggregate looks fine; liquidity_engine shows ETA + confidence |
| **B — Liquidity + unusual activity** | Simultaneous low-cash alert + velocity anomaly flag with evidence panel |
| **C — Data inconsistency** | Mock Nagad API returns stale/missing data; dashboard shows degraded confidence badge, no misleading recommendation |
| **D — Coordinated response** | Full alert lifecycle: open → assigned → acknowledged → escalated → resolved, visible in Case Manager |

---

### 9. Tech Stack Summary

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js + Tailwind + shadcn/ui | Fast to build, clean UI, good charting ecosystem |
| Backend | FastAPI (Python) | Seamless ML/analytics integration |
| Database | PostgreSQL | Relational, good for case lifecycle tracking |
| Cache / Real-time | Redis | Alert pub/sub, fast balance snapshot reads |
| AI | Claude API (`claude-haiku-4-5-20251001`) | Bengali generation, alert explanation, fast + cost-effective |
| Synthetic Data | Python (Faker + custom scripts) | Realistic MFS transaction patterns with injected anomalies |
| Charts | Recharts | Balance trends, transaction timelines |
| Containerization | Docker + Docker Compose | One-command local setup for judges |

---

### 10. Non-Functional Requirements Coverage

| Requirement | How Covered |
|-------------|------------|
| **Usability** | Role-based views; Bengali alerts; clear ownership labels |
| **Explainability** | Every alert has reason + evidence JSON + Claude-generated explanation |
| **Reliability** | Data quality field; confidence downgrade on stale/missing feeds |
| **Security & Privacy** | Synthetic identifiers only; no real credentials; no automatic financial actions |
| **Fairness** | Human review required for all anomaly flags; no automatic blocking |
| **Auditability** | Cases table records all ownership changes, acknowledgements, escalations, resolutions |
| **Provider Separation** | Each mock API is an isolated service; UI never implies cross-provider balance merging |

---

### 11. Metrics to Measure (3 Required)

| Metric | How to Measure |
|--------|---------------|
| **Shortage detection lead time** | Time between alert firing and actual balance hitting zero in simulation |
| **Anomaly precision / recall** | Evaluate detector against intentionally injected anomaly scenarios vs. normal Eid-spike scenarios |
| **Alert explanation coverage** | % of HIGH-severity alerts that have reason + evidence + Bengali message populated |

Optional additional metrics:
- API p95 latency for `/balances` endpoint under simulated load
- False-positive rate on normal salary-day / Eid demand scenarios
- Data quality degradation detection time (Scenario C)

---

### 12. Suggested Team Split

| Person | Owns |
|--------|------|
| **1** | Backend: FastAPI, DB schema, mock provider APIs, synthetic data generator |
| **2** | Analytics: liquidity engine, anomaly detectors, Claude API integration |
| **3** | Frontend: all 3 dashboards, charts, WebSocket, Bengali alert display |
| **4** *(optional)* | Data generation, metrics/validation, architecture diagram, presentation |

---

### 13. Submission Checklist Coverage

- [x] At least two provider contexts represented distinctly (bKash, Nagad, Rocket)
- [x] Shared cash and provider-specific balances demonstrated
- [x] Forward-looking liquidity insight (ETA with confidence)
- [x] At least one anomaly category with evidence (velocity / amount clustering / account concentration)
- [x] Human-review language and no automatic fraud decisions
- [x] At least one alert shows routing → ownership → acknowledgement → resolution
- [x] Repository, data, README, architecture complete
- [x] At least three metrics measured and explained
- [x] Failure, uncertainty, and false-positive handling shown (Scenario C + confidence badges)
- [x] Safety, privacy, boundaries, and limitations stated (responsible-design note)
- [x] Final presentation ready

---

*Architecture designed for Codex Community Hackathon — SUST CSE Carnival 2026*
