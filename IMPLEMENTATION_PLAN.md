# Implementation Plan — Multi-Provider Agent Liquidity Dashboard
**Codex Community Hackathon — bKash x SUST CSE Carnival 2026**
**AI Provider: OpenAI API (GPT-4o / GPT-4o-mini) | Budget: $50**

---

## Tech Stack (Final)

| Layer | Technology | Model / Version |
|-------|-----------|----------------|
| Frontend | Next.js 14 + Tailwind CSS + shadcn/ui | App Router |
| Charts | Recharts + Tremor | — |
| Backend | FastAPI (Python 3.11) | — |
| Database | PostgreSQL 15 | — |
| Cache + Pub/Sub | Redis 7 | — |
| AI — Bengali Alerts | OpenAI API | `gpt-4o-mini` (fast, cheap) |
| AI — Anomaly Narratives | OpenAI API | `gpt-4o` (better reasoning) |
| Real-time | WebSocket (FastAPI native) | — |
| Containers | Docker + Docker Compose | — |
| Synthetic Data | Python + Faker | — |

### OpenAI Cost Estimate (well within $50)
| Use Case | Model | Est. Calls | Est. Cost |
|----------|-------|-----------|-----------|
| Bengali alert generation | gpt-4o-mini | ~500 | ~$0.10 |
| Anomaly narrative | gpt-4o | ~100 | ~$0.30 |
| What-if explanation | gpt-4o-mini | ~200 | ~$0.05 |
| Total demo + dev | — | — | **~$2–5** |

---

## Project Folder Structure

```
sust-hackathon/
│
├── frontend/                          # Next.js 14
│   ├── app/
│   │   ├── layout.tsx                 # Root layout, nav, language toggle
│   │   ├── page.tsx                   # Redirect to /agent
│   │   ├── agent/
│   │   │   └── page.tsx              # Agent Dashboard
│   │   ├── ops/
│   │   │   └── page.tsx              # Operations Dashboard
│   │   ├── cases/
│   │   │   ├── page.tsx              # Case list
│   │   │   └── [id]/page.tsx         # Case detail
│   │   └── simulate/
│   │       └── page.tsx              # What-If Simulator (unique feature)
│   │
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── DeceptiveTotal.tsx    # ★ Core: aggregate vs breakdown widget
│   │   │   ├── ProviderCard.tsx      # Per-provider balance card with confidence
│   │   │   ├── LiquidityRunway.tsx   # ★ Countdown clock per provider
│   │   │   ├── ConfidenceDecay.tsx   # ★ Visual confidence degradation bar
│   │   │   └── CashMeter.tsx         # Physical cash gauge
│   │   ├── alerts/
│   │   │   ├── AlertBanner.tsx       # Top alert strip
│   │   │   ├── AlertCard.tsx         # Alert with evidence panel
│   │   │   ├── EvidencePanel.tsx     # ★ Transaction evidence fingerprint
│   │   │   ├── BengaliAlert.tsx      # Bengali message display with loader
│   │   │   └── CoordinationTimeline.tsx # ★ Visual lifecycle gantt
│   │   ├── charts/
│   │   │   ├── TransactionChart.tsx  # Balance trend over time
│   │   │   ├── ProviderPressure.tsx  # Per-provider pressure bars
│   │   │   ├── AccountGraph.tsx      # ★ Cross-account network graph
│   │   │   └── AreaHeatmap.tsx       # ★ Geographic pressure heatmap
│   │   ├── simulator/
│   │   │   └── WhatIfSlider.tsx      # ★ Demand rate → ETA recalculator
│   │   └── ui/                       # shadcn/ui components
│   │
│   ├── lib/
│   │   ├── api.ts                    # API client (axios/fetch)
│   │   ├── websocket.ts              # WebSocket hook
│   │   └── i18n.ts                   # Bengali/Banglish/English toggle
│   │
│   └── public/
│       └── sounds/alert.mp3          # Optional: audio alert for ops
│
├── backend/                          # FastAPI
│   ├── main.py                       # App entry, router registration
│   ├── core/
│   │   ├── config.py                 # Env vars, settings
│   │   ├── database.py               # SQLAlchemy + async session
│   │   └── redis.py                  # Redis client + pub/sub
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── agent.py
│   │   ├── balance.py
│   │   ├── transaction.py
│   │   ├── alert.py
│   │   └── case.py
│   │
│   ├── api/                          # Route handlers
│   │   ├── agents.py                 # GET /agents, GET /agents/{id}
│   │   ├── balances.py               # GET /balances, GET /balances/{agent_id}
│   │   ├── alerts.py                 # GET/POST /alerts
│   │   ├── cases.py                  # GET/POST/PATCH /cases
│   │   ├── analytics.py              # GET /analytics/liquidity, /anomaly
│   │   ├── simulator.py              # POST /simulate/whatif
│   │   └── ws.py                     # WebSocket endpoint /ws
│   │
│   ├── engines/                      # Core analytical logic
│   │   ├── liquidity.py              # ★ Liquidity forecasting engine
│   │   ├── anomaly/
│   │   │   ├── velocity.py           # Detector 1: transaction velocity
│   │   │   ├── clustering.py         # Detector 2: amount clustering
│   │   │   ├── concentration.py      # Detector 3: account concentration
│   │   │   └── baseline.py           # ★ Eid/holiday baseline adjuster
│   │   └── coordinator.py            # Alert routing + ownership logic
│   │
│   ├── ai/
│   │   ├── explainer.py              # ★ OpenAI integration — alerts + narratives
│   │   ├── prompts.py                # All prompt templates
│   │   └── fallback.py               # Template fallback if OpenAI fails
│   │
│   ├── providers/                    # Mock provider API clients
│   │   ├── base.py                   # Abstract provider interface
│   │   ├── bkash.py                  # bKash mock (can simulate delay/failure)
│   │   ├── nagad.py                  # Nagad mock (Scenario C: can go stale)
│   │   └── rocket.py                 # Rocket mock
│   │
│   ├── data/
│   │   ├── seed.py                   # DB seeder (Karim Mia + demo agents)
│   │   ├── synthetic.py              # Transaction generator
│   │   └── scenarios/
│   │       ├── eid_rush.py           # Scenario A+B: Eid demand + anomaly
│   │       ├── data_conflict.py      # Scenario C: stale/missing feed
│   │       ├── coordination.py       # Scenario D: alert lifecycle
│   │       └── salary_day.py         # False positive: normal salary spike
│   │
│   └── scheduler/
│       └── poller.py                 # Background: polls providers every 30s
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Database Schema (PostgreSQL)

```sql
-- Agents
CREATE TABLE agents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    area        VARCHAR(100) NOT NULL,       -- e.g. "Mirpur-10, Dhaka"
    phone       VARCHAR(20),
    physical_cash NUMERIC(12,2) DEFAULT 0,
    status      VARCHAR(20) DEFAULT 'active', -- active | suspended | offline
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Provider Balances (snapshot per poll)
CREATE TABLE provider_balances (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID REFERENCES agents(id),
    provider    VARCHAR(20) NOT NULL,         -- bkash | nagad | rocket
    balance     NUMERIC(12,2),
    fetched_at  TIMESTAMPTZ DEFAULT NOW(),
    data_quality VARCHAR(20) DEFAULT 'ok',    -- ok | delayed | missing | conflict
    latency_ms  INTEGER                        -- how long the fetch took
);

-- Transactions (synthetic stream)
CREATE TABLE transactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID REFERENCES agents(id),
    provider    VARCHAR(20) NOT NULL,
    type        VARCHAR(20) NOT NULL,          -- cash_in | cash_out | send | receive
    amount      NUMERIC(10,2) NOT NULL,
    account_id  VARCHAR(50),                   -- masked synthetic ID
    timestamp   TIMESTAMPTZ DEFAULT NOW(),
    status      VARCHAR(20) DEFAULT 'completed' -- completed | failed | pending
);

-- Alerts
CREATE TABLE alerts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID REFERENCES agents(id),
    provider    VARCHAR(20),                   -- NULL means multi-provider / cash
    type        VARCHAR(30) NOT NULL,          -- liquidity | anomaly | data_quality
    severity    VARCHAR(10) NOT NULL,          -- low | medium | high | critical
    message_en  TEXT,
    message_bn  TEXT,                          -- OpenAI-generated Bengali
    evidence    JSONB,                         -- transaction list, ratios, etc.
    confidence  NUMERIC(4,3),                  -- 0.000 – 1.000
    uncertainty VARCHAR(10),                   -- low | medium | high
    eta_minutes INTEGER,                       -- for liquidity alerts
    owner_role  VARCHAR(50),                   -- field_officer | risk_analyst | ops_manager
    owner_name  VARCHAR(100),
    status      VARCHAR(20) DEFAULT 'open',   -- open | acknowledged | escalated | resolved
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Cases (coordination lifecycle)
CREATE TABLE cases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id        UUID REFERENCES alerts(id),
    assigned_to     VARCHAR(100),
    assigned_role   VARCHAR(50),
    acknowledged_at TIMESTAMPTZ,
    escalated_at    TIMESTAMPTZ,
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,
    false_positive  BOOLEAN DEFAULT FALSE,     -- ★ feedback loop
    notes           JSONB DEFAULT '[]',        -- array of {author, text, timestamp}
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Baseline (for false positive suppression)
CREATE TABLE transaction_baseline (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID REFERENCES agents(id),
    provider    VARCHAR(20),
    hour_of_day INTEGER,                       -- 0-23
    day_type    VARCHAR(20),                   -- weekday | weekend | eid | salary_day
    avg_count   NUMERIC(8,2),
    avg_amount  NUMERIC(10,2),
    stddev      NUMERIC(10,2),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
```

---

## API Endpoints

### Agent & Balance
```
GET  /api/agents                        → List all agents with summary
GET  /api/agents/{id}                   → Single agent detail
GET  /api/balances/{agent_id}           → All provider balances + physical cash
GET  /api/balances/{agent_id}/history   → Balance history (for charts)
```

### Analytics
```
GET  /api/analytics/liquidity/{agent_id}  → ETA, confidence, rate per provider
GET  /api/analytics/pressure              → Area-level aggregated pressure
POST /api/analytics/whatif                → ★ What-if: given new demand rate → new ETA
```

### Alerts
```
GET  /api/alerts                         → All alerts (filter: provider, severity, status)
GET  /api/alerts/{id}                    → Alert detail with evidence + Bengali message
POST /api/alerts/{id}/acknowledge        → Mark acknowledged
POST /api/alerts/{id}/escalate           → Escalate with note
POST /api/alerts/{id}/resolve            → Resolve with note
POST /api/alerts/{id}/false-positive     → ★ Flag as false positive (feedback loop)
```

### Cases
```
GET  /api/cases                          → All cases (filter: status, owner)
GET  /api/cases/{id}                     → Full case with audit trail
PATCH /api/cases/{id}                    → Update owner, add note
```

### Transactions
```
GET  /api/transactions/{agent_id}        → Recent transactions (filter: provider, type)
POST /api/simulate/scenario/{name}       → Trigger demo scenario manually
```

### WebSocket
```
WS   /ws                                 → Real-time: balance updates + new alerts push
```

---

## Core Engines

### 1. Liquidity Engine (`engines/liquidity.py`)

```python
# Algorithm
rate = avg(cash_out_amounts, last_30_minutes) / 30  # BDT per minute
eta_minutes = current_balance / rate if rate > 0 else infinity

# Confidence scoring
if data_age > 300:   confidence = 0.2  # >5 min stale
elif data_age > 120: confidence = 0.6  # >2 min stale
else:                confidence = 0.9

# Output per provider + cash
{
  "provider": "bkash",
  "balance": 1200,
  "rate_per_min": 31.5,
  "eta_minutes": 38,
  "confidence": 0.88,
  "data_quality": "ok",
  "recommended_topup": 20000
}
```

### 2. Anomaly Detectors (`engines/anomaly/`)

**Velocity Detector**
```python
window = transactions_last_N_minutes(agent, provider, N=15)
baseline = get_baseline(agent, provider, hour, day_type)
z_score = (len(window) - baseline.avg_count) / baseline.stddev
flagged = z_score > 2.5
```

**Amount Clustering Detector**
```python
amounts = [t.amount for t in window]
bins = histogram(amounts, bin_width=100)
top_bin_ratio = max(bin_counts) / len(amounts)
flagged = top_bin_ratio > 0.6 and len(amounts) >= 4
```

**Account Concentration Detector**
```python
unique_accounts = len(set(t.account_id for t in window))
concentration_ratio = unique_accounts / len(window)
flagged = concentration_ratio < 0.4 and len(window) >= 4
```

**★ Eid/Holiday Baseline Adjuster**
```python
# Calendar-aware — multiplies baseline thresholds on known high-demand days
DEMAND_MULTIPLIERS = {
    "eid_day_before": 2.5,
    "eid_day":        3.0,
    "salary_day":     1.8,  # 1st and 25-30th of month
    "friday":         1.3,
    "weekday":        1.0
}
adjusted_threshold = base_threshold * DEMAND_MULTIPLIERS[get_day_type(now)]
```

### 3. OpenAI Integration (`ai/explainer.py`)

**Bengali Alert Generation**
```python
# Model: gpt-4o-mini  (cheap, fast, great multilingual)
def generate_bengali_alert(alert_data: dict) -> str:
    prompt = f"""
    You are an assistant generating alerts for mobile money agents in Bangladesh.
    Write a SHORT, clear Bengali (বাংলা) alert message — 3-4 sentences maximum.
    Use careful, advisory language. NEVER say fraud or accusation.
    Always end with a safe next step.

    Situation:
    - Provider: {alert_data['provider']}
    - Type: {alert_data['type']}
    - ETA to shortage: {alert_data['eta_minutes']} minutes
    - Current balance: {alert_data['balance']} BDT
    - Evidence: {alert_data['evidence_summary']}
    - Confidence: {alert_data['confidence']*100:.0f}%
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content
```

**Anomaly Narrative Generation**
```python
# Model: gpt-4o  (better reasoning for nuanced explanations)
def generate_anomaly_narrative(anomaly_data: dict) -> str:
    prompt = f"""
    Write a 2-sentence explanation of unusual transaction activity for a field officer.
    Mention possible legitimate reasons (Eid demand, salary day) before flagging concern.
    Do not accuse. Use "may", "could", "requires review".

    Evidence: {anomaly_data}
    """
```

**Fallback (if OpenAI fails)**
```python
# Template-based fallback — always works offline
FALLBACK_TEMPLATES = {
    "liquidity_bn": "আনুমানিক {eta} মিনিটের মধ্যে {provider} ব্যালেন্স শেষ হতে পারে।",
    "anomaly_bn":   "অস্বাভাবিক লেনদেন শনাক্ত হয়েছে। মানব পর্যালোচনা প্রয়োজন।"
}
```

---

## Unique & Exceptional Features (Full List)

### ★ Feature 1 — Deceptive Total Widget
- Shows aggregate total in large number (GREEN if > threshold)
- Animated expand to show per-provider breakdown
- bKash card flips RED even though total is green
- **Impact:** Judges see the core problem solved in 10 seconds

### ★ Feature 2 — Liquidity Runway Clock
- Per-provider countdown timer (live, updates every 30s)
- Color: green > 2hr | yellow 30min–2hr | red < 30min | pulsing red < 10min
- Shows rate (BDT/min outflow) alongside ETA

### ★ Feature 3 — Confidence Decay Bar
- Visual bar that drains in real-time as data gets stale
- Tooltip: "Data last updated 4m 12s ago — confidence: LOW"
- When fully drained: recommendation hidden, badge shown instead

### ★ Feature 4 — Evidence Fingerprint Panel
- Visual timeline of the exact transactions that triggered anomaly
- Color-coded by account (same account = same color)
- Amount clustering shown as histogram overlay
- Field officer can click any transaction to expand detail

### ★ Feature 5 — Eid/Holiday Baseline Adjuster
- Calendar-aware anomaly detection
- Correctly suppresses alerts on Eid day, salary day, Friday peaks
- Shows: "Adjusted for Eid demand — threshold raised 2.5×"
- Prevents false positives that would undermine trust

### ★ Feature 6 — What-If Simulator
- Slider: adjust demand rate (+10% to +200%)
- Adjust: remove one provider feed
- Dashboard instantly recalculates ETA + risk level for all providers
- OpenAI generates updated advisory based on new scenario

### ★ Feature 7 — Cross-Account Network Graph
- D3.js or Recharts network graph
- Shows accounts that transacted with the same agent multiple times
- Edges = transactions, node size = total amount
- Helps risk analyst see account clusters visually

### ★ Feature 8 — Coordination Timeline (Gantt-style)
- Visual horizontal timeline of the full case lifecycle
- Milestones: Alert fired → Acknowledged → Assigned → Escalated → Resolved
- Shows time gaps between steps (e.g., "6 min to acknowledge")

### ★ Feature 9 — False Positive Feedback Loop
- Field officers can mark any alert as "False Positive — Eid demand"
- This adjusts the local baseline for that agent + provider + hour
- Next similar event: threshold automatically higher
- Shows: "Baseline updated based on 3 confirmed false positives"

### ★ Feature 10 — Multi-language Toggle
- Per-user preference: বাংলা | Banglish | English
- All alerts, labels, and recommendations switch
- OpenAI prompt changes language based on preference

### ★ Feature 11 — Scenario C: Graceful Data Degradation
- Kill Nagad feed → card goes yellow → confidence decays
- Aggregate hides Nagad's stale number from calculation
- Clear badge: "Nagad data unavailable — estimate excludes Nagad"
- Feed recovers → auto-refresh → confidence restores

### ★ Feature 12 — Area Pressure Heatmap
- Grid map of Dhaka zones (Mirpur, Dhanmondi, Uttara, etc.)
- Color intensity = aggregate liquidity risk score
- Click zone → drill down to agent list in that zone

### ★ Feature 13 — Audit Trail Export
- Every case has a full JSON/PDF-exportable audit trail
- Includes: all notes, all status changes, all timestamps, who did what
- Demonstrates auditability requirement from problem statement

### ★ Feature 14 — Provider Separation Visualizer
- Architecture diagram (interactive) shown in /about page
- Animated data flow: bKash API → aggregator → dashboard
- Shows visually that providers never touch each other's data

### ★ Feature 15 — Sound + Visual Alert for Critical Events
- Optional: audio ping when HIGH severity alert fires on Ops Dashboard
- Red pulsing border on affected provider card
- Browser tab title updates: "⚠️ CRITICAL — bKash | Dashboard"

---

## Data Generation Plan

### Synthetic Agents (seed.py)
```python
agents = [
    {"name": "Karim Mia",   "area": "Mirpur-10"},     # Main demo agent
    {"name": "Rina Begum",  "area": "Dhanmondi-15"},
    {"name": "Salam Ahmed", "area": "Uttara-Sector-7"},
    {"name": "Fatema Khatun","area": "Motijheel"},
    {"name": "Rubel Hossain","area": "Gulshan-2"},
]
```

### Transaction Patterns (synthetic.py)
| Pattern | Implementation |
|---------|---------------|
| Normal weekday | Poisson distribution, avg 8 tx/hr |
| Eid rush | 3× rate, random spike 2–5 PM |
| Salary day | 1.8× rate on 1st and 25–30th |
| Anomaly (velocity) | Inject 8 tx in 12 minutes |
| Anomaly (clustering) | Inject 6 tx within ±50 BDT range |
| Anomaly (concentration) | 2 accounts, 6 transactions |
| Stale feed | Nagad returns 304/delay after T minutes |

---

## OpenAI Prompt Engineering

### Prompt Design Principles
1. Always specify: "advisory only, not a fraud determination"
2. Always include: confidence level + uncertainty
3. Always end: safe recommended next step
4. Bengali prompts: specify script explicitly ("respond in Bengali script, not transliteration")
5. Token limits: 200 tokens for alerts, 150 for short messages

### Prompt Templates Location
All prompts in `backend/ai/prompts.py` — centralized for easy tuning.

---

## Real-Time Architecture (WebSocket)

```
Client connects to WS /ws
  ↓
Backend poller runs every 30s:
  → Fetches all provider balances
  → Runs liquidity engine
  → Runs anomaly detectors
  → If alert fires → publishes to Redis pub/sub
  ↓
WebSocket handler subscribes to Redis
  → Pushes to all connected clients:
      { type: "balance_update", data: {...} }
      { type: "new_alert", data: {...} }
      { type: "data_quality_change", data: {...} }
```

---

## Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL_FAST=gpt-4o-mini
OPENAI_MODEL_SMART=gpt-4o

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/hackathon

# Redis
REDIS_URL=redis://localhost:6379

# Provider mock delays (for Scenario C demo)
NAGAD_DELAY_SECONDS=0        # set to 300 to simulate stale
BKASH_FAILURE_MODE=false     # set to true to simulate outage
ROCKET_DELAY_SECONDS=0
```

---

## Docker Compose Setup

```yaml
version: '3.9'
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_WS_URL=ws://backend:8000/ws

  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
    env_file: .env

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: hackathon
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

**Start everything:** `docker compose up --build`
**Seed data:** `docker compose exec backend python -m data.seed`

---

## Validation & Metrics Plan

Run these before the demo and record actual numbers:

| Metric | How to Measure | Target |
|--------|---------------|--------|
| Shortage detection lead time | Inject scenario, measure alert time vs actual zero | > 30 min |
| Anomaly precision | 20 injected anomaly scenarios, count true positives | > 80% |
| False positive rate | 10 Eid/salary-day scenarios, count wrong flags | < 20% |
| Alert explanation coverage | Count HIGH alerts with Bengali + evidence | 100% |
| API p95 latency | `locust` or `k6` load test on `/balances` | < 300ms |
| Data degradation detection | Kill Nagad feed, measure time to yellow badge | < 90s |

---

## Presentation Slide Order

1. **Problem** — Karim Mia story, the deceptive total
2. **Solution Overview** — architecture diagram (Provider Separation Visualizer)
3. **Live Demo** — follow DEMO_SCRIPT.md
4. **How It Works** — liquidity engine, 3 anomaly detectors, OpenAI integration
5. **Metrics** — all 6 measured values with actual numbers
6. **Responsible AI** — what we flag, what we don't, false positive handling, human review
7. **Limitations & Next Steps** — honest, specific

---

*Implementation plan for Codex Community Hackathon — bKash x SUST CSE Carnival 2026*
