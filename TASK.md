# Task Board — Multi-Provider Agent Liquidity Dashboard
**Codex Community Hackathon — bKash x SUST CSE Carnival 2026**

> **How to use this file:**
> - Mark tasks: `[ ]` pending → `[~]` in progress → `[x]` done
> - Owner codes: **B** = Backend | **F** = Frontend | **A** = AI/Analytics | **D** = Data | **ALL** = whole team
> - Priority: 🔴 Critical (demo breaks without it) | 🟡 High (judge impact) | 🟢 Nice to have

---

## Phase 0 — Project Setup
**Goal:** Everyone can run the project locally in one command.
**Target:** First 2–3 hours

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 0.1 | Create GitHub repo, add all team members | ALL | 🔴 | [ ] |
| 0.2 | Scaffold Next.js 14 frontend (`npx create-next-app`) | F | 🔴 | [ ] |
| 0.3 | Scaffold FastAPI backend with folder structure | B | 🔴 | [ ] |
| 0.4 | Write `docker-compose.yml` (frontend + backend + postgres + redis) | B | 🔴 | [ ] |
| 0.5 | Write `.env.example` with all required variables | B | 🔴 | [ ] |
| 0.6 | Install frontend deps: Tailwind, shadcn/ui, Recharts, axios | F | 🔴 | [ ] |
| 0.7 | Install backend deps: fastapi, sqlalchemy, asyncpg, redis, openai, faker | B | 🔴 | [ ] |
| 0.8 | Verify `docker compose up` starts all 4 services cleanly | ALL | 🔴 | [ ] |
| 0.9 | Write base README with setup instructions | ALL | 🟡 | [ ] |

---

## Phase 1 — Data Layer
**Goal:** Realistic synthetic data flowing through the system.
**Target:** Hours 3–8

### 1A — Database Schema
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 1.1 | Write SQLAlchemy models: Agent, ProviderBalance, Transaction | B | 🔴 | [ ] |
| 1.2 | Write SQLAlchemy models: Alert, Case, TransactionBaseline | B | 🔴 | [ ] |
| 1.3 | Write Alembic migrations for all tables | B | 🔴 | [ ] |
| 1.4 | Run migrations, verify schema in postgres | B | 🔴 | [ ] |

### 1B — Synthetic Data Generator
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 1.5 | Write `seed.py` — create 5 agents (Karim Mia as demo agent) | D | 🔴 | [ ] |
| 1.6 | Write `synthetic.py` — generate normal weekday transactions (Poisson dist) | D | 🔴 | [ ] |
| 1.7 | Write Eid rush pattern — 3× rate, spike 2–5 PM | D | 🔴 | [ ] |
| 1.8 | Write salary-day pattern — 1.8× rate on 1st/25–30th of month | D | 🟡 | [ ] |
| 1.9 | Write `scenarios/eid_rush.py` — Scenarios A+B injection script | D | 🔴 | [ ] |
| 1.10 | Write `scenarios/data_conflict.py` — Scenario C stale feed injection | D | 🔴 | [ ] |
| 1.11 | Write `scenarios/coordination.py` — Scenario D full lifecycle data | D | 🔴 | [ ] |
| 1.12 | Write `scenarios/salary_day.py` — false positive scenario data | D | 🟡 | [ ] |
| 1.13 | Seed `transaction_baseline` table with per-hour/day_type baselines | D | 🟡 | [ ] |
| 1.14 | Verify seeded data looks realistic — review 50 sample rows | D | 🔴 | [ ] |

### 1C — Mock Provider APIs
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 1.15 | Write `providers/base.py` — abstract interface with `get_balance()`, `get_transactions()` | B | 🔴 | [ ] |
| 1.16 | Write `providers/bkash.py` — reads from DB, returns bKash data | B | 🔴 | [ ] |
| 1.17 | Write `providers/nagad.py` — reads from DB, supports simulated delay/stale | B | 🔴 | [ ] |
| 1.18 | Write `providers/rocket.py` — reads from DB | B | 🔴 | [ ] |
| 1.19 | Add `NAGAD_DELAY_SECONDS` env var support to Nagad provider | B | 🔴 | [ ] |
| 1.20 | Test: confirm each provider returns only its own data | B | 🔴 | [ ] |

---

## Phase 2 — Core Backend Engines
**Goal:** Liquidity forecasting + anomaly detection working and returning results.
**Target:** Hours 6–14

### 2A — Liquidity Engine
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.1 | Write `engines/liquidity.py` — calculate rate, ETA, confidence per provider | A | 🔴 | [ ] |
| 2.2 | Add physical cash calculation alongside e-money | A | 🔴 | [ ] |
| 2.3 | Add data quality → confidence degradation logic | A | 🔴 | [ ] |
| 2.4 | Add recommended top-up amount calculation | A | 🟡 | [ ] |
| 2.5 | Unit test: inject known balance + rate → verify ETA | A | 🔴 | [ ] |
| 2.6 | Unit test: stale data → verify confidence drops correctly | A | 🔴 | [ ] |

### 2B — Anomaly Detectors
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.7 | Write `engines/anomaly/velocity.py` — z-score vs baseline | A | 🔴 | [ ] |
| 2.8 | Write `engines/anomaly/clustering.py` — histogram bin concentration | A | 🔴 | [ ] |
| 2.9 | Write `engines/anomaly/concentration.py` — unique account ratio | A | 🔴 | [ ] |
| 2.10 | Write `engines/anomaly/baseline.py` — ★ Eid/holiday multiplier adjuster | A | 🟡 | [ ] |
| 2.11 | Write anomaly combiner — merge results from all 3 detectors into one alert | A | 🔴 | [ ] |
| 2.12 | Unit test velocity: inject 8 txn in 12 min → verify flag fires | A | 🔴 | [ ] |
| 2.13 | Unit test clustering: inject 6 near-identical amounts → verify flag fires | A | 🔴 | [ ] |
| 2.14 | Unit test false positive: inject salary-day spike → verify NO flag | A | 🟡 | [ ] |

### 2C — Balance Aggregator + Poller
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.15 | Write `scheduler/poller.py` — polls all 3 providers every 30s | B | 🔴 | [ ] |
| 2.16 | Save each poll result to `provider_balances` table | B | 🔴 | [ ] |
| 2.17 | Run liquidity engine after each poll, store results | B | 🔴 | [ ] |
| 2.18 | Run anomaly detectors after each poll, fire alerts if needed | B | 🔴 | [ ] |
| 2.19 | Publish new alerts to Redis pub/sub channel | B | 🔴 | [ ] |

### 2D — Alert Router + Case Manager
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.20 | Write `engines/coordinator.py` — assign owner based on alert type + severity | B | 🔴 | [ ] |
| 2.21 | Write alert CRUD API: GET /alerts, GET /alerts/{id} | B | 🔴 | [ ] |
| 2.22 | Write alert action APIs: acknowledge, escalate, resolve, false-positive | B | 🔴 | [ ] |
| 2.23 | Write case CRUD API: GET /cases, PATCH /cases/{id} | B | 🔴 | [ ] |
| 2.24 | Write case note append: PATCH /cases/{id} adds to notes JSONB array | B | 🔴 | [ ] |

---

## Phase 3 — OpenAI Integration
**Goal:** Live Bengali alerts + anomaly narratives generated by OpenAI.
**Target:** Hours 10–16

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 3.1 | Write `ai/prompts.py` — all prompt templates centralized | A | 🔴 | [ ] |
| 3.2 | Write `ai/explainer.py` — `generate_bengali_alert()` using gpt-4o-mini | A | 🔴 | [ ] |
| 3.3 | Write `ai/explainer.py` — `generate_anomaly_narrative()` using gpt-4o | A | 🔴 | [ ] |
| 3.4 | Write `ai/explainer.py` — `generate_whatif_summary()` for simulator | A | 🟡 | [ ] |
| 3.5 | Write `ai/fallback.py` — template-based fallback if OpenAI times out | A | 🔴 | [ ] |
| 3.6 | Add async OpenAI call — alert generation runs in background, not blocking | A | 🔴 | [ ] |
| 3.7 | Test: trigger liquidity alert → verify Bengali message generated + saved | A | 🔴 | [ ] |
| 3.8 | Test: trigger anomaly alert → verify narrative mentions Eid as possible reason | A | 🟡 | [ ] |
| 3.9 | Test: simulate OpenAI failure → verify fallback template fires | A | 🔴 | [ ] |
| 3.10 | Add Banglish prompt variant (romanized Bengali) | A | 🟢 | [ ] |

---

## Phase 4 — Frontend Core Views
**Goal:** All 3 dashboards functional with real data.
**Target:** Hours 12–22

### 4A — Agent Dashboard
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 4.1 | Build page layout: header, nav (Agent / Ops / Cases), language toggle | F | 🔴 | [ ] |
| 4.2 | Build `DeceptiveTotal.tsx` — aggregate number + animated provider breakdown | F | 🔴 | [ ] |
| 4.3 | Build `ProviderCard.tsx` — balance, data quality badge, confidence bar | F | 🔴 | [ ] |
| 4.4 | Build `LiquidityRunway.tsx` — countdown clock with color states | F | 🔴 | [ ] |
| 4.5 | Build `ConfidenceDecay.tsx` — real-time draining bar tied to data age | F | 🟡 | [ ] |
| 4.6 | Build `CashMeter.tsx` — physical cash gauge (radial or progress bar) | F | 🔴 | [ ] |
| 4.7 | Build `BengaliAlert.tsx` — shows Bengali message with loader animation | F | 🔴 | [ ] |
| 4.8 | Connect agent dashboard to `/api/balances/{agent_id}` | F | 🔴 | [ ] |
| 4.9 | Connect to WebSocket — live balance updates without page refresh | F | 🔴 | [ ] |

### 4B — Operations Dashboard
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 4.10 | Build agent list table — name, area, risk level (color-coded) | F | 🔴 | [ ] |
| 4.11 | Build filter bar — by provider, severity, area, status | F | 🟡 | [ ] |
| 4.12 | Build alert queue panel — sorted by severity, newest first | F | 🔴 | [ ] |
| 4.13 | Build `AlertCard.tsx` — alert summary with acknowledge button | F | 🔴 | [ ] |
| 4.14 | Build `EvidencePanel.tsx` — transaction list, amounts, account IDs, histogram | F | 🔴 | [ ] |
| 4.15 | Connect alert queue to `/api/alerts` | F | 🔴 | [ ] |
| 4.16 | WebSocket: new alert fires → ops dashboard updates without refresh | F | 🔴 | [ ] |

### 4C — Case Manager
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 4.17 | Build case list — id, agent, severity, owner, status, time open | F | 🔴 | [ ] |
| 4.18 | Build case detail page — full evidence + history + Bengali message | F | 🔴 | [ ] |
| 4.19 | Build `CoordinationTimeline.tsx` — visual lifecycle (open → ack → escalate → resolve) | F | 🟡 | [ ] |
| 4.20 | Build note input — add case note, submit, appears in history | F | 🔴 | [ ] |
| 4.21 | Build action buttons: Acknowledge / Assign / Escalate / Resolve / False Positive | F | 🔴 | [ ] |
| 4.22 | Connect all case actions to backend API | F | 🔴 | [ ] |
| 4.23 | Show audit trail: all status changes with timestamps + actors | F | 🟡 | [ ] |

---

## Phase 5 — Unique / Exceptional Features
**Goal:** The features that separate top 3 from the rest.
**Target:** Hours 18–28

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 5.1 | ★ `WhatIfSlider.tsx` — demand multiplier slider → live ETA recalculation | F+A | 🟡 | [ ] |
| 5.2 | ★ `POST /api/simulate/whatif` — backend recalculates with adjusted rate | A | 🟡 | [ ] |
| 5.3 | ★ OpenAI generates updated advisory for what-if scenario | A | 🟢 | [ ] |
| 5.4 | ★ `AccountGraph.tsx` — D3/Recharts network: accounts ↔ transactions ↔ agent | F | 🟡 | [ ] |
| 5.5 | ★ `AreaHeatmap.tsx` — Dhaka zone grid, color = risk level | F | 🟢 | [ ] |
| 5.6 | ★ False positive feedback: button → updates baseline table in DB | B+F | 🟡 | [ ] |
| 5.7 | ★ Multi-language toggle (Bengali / Banglish / English) — switches all UI text | F | 🟡 | [ ] |
| 5.8 | ★ Scenario C UI: Nagad card yellow → confidence decay → withheld recommendation | F | 🔴 | [ ] |
| 5.9 | ★ Audio alert ping on CRITICAL severity (Ops Dashboard only) | F | 🟢 | [ ] |
| 5.10 | ★ Browser tab title update on new critical alert | F | 🟢 | [ ] |
| 5.11 | ★ Audit trail PDF/JSON export button | B+F | 🟢 | [ ] |
| 5.12 | ★ Provider Separation Visualizer page (/about) — animated data flow diagram | F | 🟢 | [ ] |

---

## Phase 6 — Scenario Wiring (Demo Readiness)
**Goal:** Every demo scenario triggerable with one button or one command.
**Target:** Hours 24–30

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 6.1 | Wire Scenario A — hidden bKash shortage trigger button in dev mode | D+B | 🔴 | [ ] |
| 6.2 | Wire Scenario B — simultaneous low cash + anomaly injection | D+B | 🔴 | [ ] |
| 6.3 | Wire Scenario C — set `NAGAD_DELAY_SECONDS=300` → verify yellow badge | D+B | 🔴 | [ ] |
| 6.4 | Wire Scenario D — pre-seed coordination case for Karim Mia | D+B | 🔴 | [ ] |
| 6.5 | Wire salary-day false positive — trigger normal spike → verify no alert | D+A | 🟡 | [ ] |
| 6.6 | Add `POST /api/simulate/scenario/{name}` endpoint (dev only) | B | 🟡 | [ ] |
| 6.7 | Run full demo script end-to-end → fix all visual glitches | ALL | 🔴 | [ ] |
| 6.8 | Confirm Bengali messages generate correctly for each scenario | A | 🔴 | [ ] |
| 6.9 | Seed demo database with Karim Mia's pre-set state (exactly as in demo script) | D | 🔴 | [ ] |

---

## Phase 7 — Metrics & Validation
**Goal:** Actual numbers to show on metrics slide.
**Target:** Hours 28–34

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 7.1 | Run 50 liquidity scenarios → measure detection lead time → record avg | A | 🔴 | [ ] |
| 7.2 | Run 20 injected anomaly scenarios → measure precision/recall | A | 🔴 | [ ] |
| 7.3 | Run 10 Eid/salary-day scenarios → measure false positive rate | A | 🔴 | [ ] |
| 7.4 | Count alert explanation coverage — % with Bengali + evidence | A | 🔴 | [ ] |
| 7.5 | Load test `/api/balances` endpoint → measure p95 latency | B | 🟡 | [ ] |
| 7.6 | Test data degradation detection — measure time to yellow badge | B | 🔴 | [ ] |
| 7.7 | Record all 6 metric values → add to metrics slide | ALL | 🔴 | [ ] |

---

## Phase 8 — Polish & Presentation
**Goal:** Demo-ready, judge-ready.
**Target:** Hours 32–40 (final stretch)

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 8.1 | Full demo run-through × 3 — with time measurement | ALL | 🔴 | [ ] |
| 8.2 | Fix all visual inconsistencies, color-code badges properly | F | 🔴 | [ ] |
| 8.3 | Verify all Bengali text renders correctly (not boxes/squares) | F | 🔴 | [ ] |
| 8.4 | Write architecture diagram (draw.io or Excalidraw) with provider boundaries | ALL | 🟡 | [ ] |
| 8.5 | Write `data_simulation_note.md` — how data was created, assumptions, limits | D | 🔴 | [ ] |
| 8.6 | Write `responsible_design_note.md` — what system does NOT do | ALL | 🔴 | [ ] |
| 8.7 | Build presentation slides (7 slides — see IMPLEMENTATION_PLAN.md) | ALL | 🔴 | [ ] |
| 8.8 | Memorize the Eid story hook (speaker rehearses 5× out loud) | ALL | 🔴 | [ ] |
| 8.9 | Prepare recovery lines for each possible demo failure | ALL | 🟡 | [ ] |
| 8.10 | Submission checklist review — verify every item is checked | ALL | 🔴 | [ ] |
| 8.11 | Push final code, tag release `v1.0.0-hackathon` | ALL | 🔴 | [ ] |
| 8.12 | Optional: record short demo video as backup | ALL | 🟢 | [ ] |

---

## Submission Checklist (Final Gate)

- [ ] Two providers (bKash, Nagad, Rocket) represented distinctly
- [ ] Shared cash + provider balances both shown
- [ ] Forward-looking liquidity ETA with confidence shown
- [ ] At least one anomaly with evidence panel
- [ ] Human review language — no "fraud" word anywhere in UI
- [ ] One alert: routing → ownership → acknowledgement → resolution all clickable
- [ ] Repository public with README + setup steps + sample data
- [ ] Architecture diagram included
- [ ] `data_simulation_note.md` included
- [ ] `responsible_design_note.md` included
- [ ] 3+ metrics measured with actual numbers
- [ ] Scenario C (data degradation) demonstrated
- [ ] False positive handling shown
- [ ] Bengali alerts working via OpenAI
- [ ] Demo script rehearsed ×3 end-to-end

---

## Parallel Work Map (Who Does What Simultaneously)

```
Hours 0–8:
  B: Setup + DB schema + mock providers
  F: Setup + component stubs + layouts
  A: Liquidity engine + anomaly detectors (unit tests)
  D: Synthetic data + seed scripts

Hours 8–16:
  B: Poller + alert router + case APIs
  F: Agent dashboard + provider cards
  A: OpenAI integration + prompts
  D: Scenario injection scripts

Hours 16–24:
  B: WebSocket + simulator endpoint
  F: Ops dashboard + case manager
  A: Metrics measurement scripts
  D: Wire all 4 demo scenarios

Hours 24–32:
  ALL: Unique features (5.x tasks), polish, full demo run
  A: Collect + record all metrics

Hours 32–40:
  ALL: Demo rehearsal, slide building, submission prep
```

---

*Task board for Codex Community Hackathon — bKash x SUST CSE Carnival 2026*
