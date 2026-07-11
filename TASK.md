# Task Board — Multi-Provider Agent Liquidity Dashboard
**Codex Community Hackathon — bKash x SUST CSE Carnival 2026**

> **How to use this file:**
> - Mark tasks: `[ ]` pending → `[~]` in progress → `[x]` done
> - Owner codes: **B** = Backend | **F** = Frontend | **A** = AI/Analytics | **D** = Data | **ALL** = whole team
> - Priority: 🔴 Critical (demo breaks without it) | 🟡 High (judge impact) | 🟢 Nice to have

---

## Phase 0 — Project Setup
**Goal:** Everyone can run the project locally and all cloud services are connected.
**Target:** First 2–3 hours

### 0A — Repo & Scaffolding
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 0.1 | Create GitHub repo (public), add all team members | ALL | 🔴 | [ ] |
| 0.2 | Scaffold Next.js 14 frontend (`npx create-next-app@latest`) | F | 🔴 | [x] |
| 0.3 | Scaffold FastAPI backend with full folder structure from IMPLEMENTATION_PLAN.md | B | 🔴 | [x] |
| 0.4 | Write `docker-compose.yml` — **backend only** (no postgres, no redis) | B | 🔴 | [x] |
| 0.5 | Install frontend deps: Tailwind, shadcn/ui, Recharts, axios | F | 🔴 | [ ] |
| 0.6 | Install backend deps: `pip install "fastapi[standard]" sqlalchemy asyncpg alembic openai faker` | B | 🔴 | [x] |

### 0B — Cloud Services Setup
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 0.7 | Create **Neon** project at neon.tech — copy pooled + direct connection strings | B | 🔴 | [x] |
| 0.8 | ~~Upstash Redis~~ — removed, not needed (single instance = in-memory WS manager) | B | 🔴 | [x] |
| 0.9 | Write `.env` with all variables (Neon, OpenAI, CORS) | B | 🔴 | [x] |
| 0.10 | Configure **Alembic** — `DATABASE_SYNC_URL` in `alembic/env.py` | B | 🔴 | [x] |
| 0.11 | Verify backend connects to Neon — 5 agents confirmed in DB | B | 🔴 | [x] |
| 0.12 | ~~Upstash check~~ — N/A | B | 🔴 | [x] |
| 0.13 | Add **CORS middleware** to `main.py` | B | 🔴 | [x] |
| 0.14 | Verify server starts — `/api/health` returns ok, `/api/agents` returns 5 agents | ALL | 🔴 | [x] |
| 0.15 | Write base README with setup steps + env var list | ALL | 🟡 | [ ] |

---

## Phase 1 — Data Layer
**Goal:** Realistic synthetic data flowing through the system.
**Target:** Hours 3–8

### 1A — Database Schema
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 1.1 | Write SQLAlchemy models: Agent, ProviderBalance, Transaction | B | 🔴 | [x] |
| 1.2 | Write SQLAlchemy models: Alert, Case, TransactionBaseline | B | 🔴 | [x] |
| 1.3 | Write Alembic migrations for all tables | B | 🔴 | [x] |
| 1.4 | Run `alembic upgrade head` against **Neon** — 6 tables created | B | 🔴 | [x] |

### 1B — Synthetic Data Generator
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 1.5 | Write `seed.py` — 5 agents seeded (Karim Mia bKash=৳1,200 critical) | D | 🔴 | [x] |
| 1.6 | Write `synthetic.py` — normal weekday transactions (Poisson dist) | D | 🔴 | [x] |
| 1.7 | Write Eid rush pattern — 3× rate multiplier | D | 🔴 | [x] |
| 1.8 | Write salary-day pattern — 1.8× rate on 1st/25–30th | D | 🟡 | [x] |
| 1.9 | Write `scenarios/eid_rush.py` — Scenarios A+B injection | D | 🔴 | [x] |
| 1.10 | Write `scenarios/data_conflict.py` — Scenario C via env var | D | 🔴 | [x] |
| 1.11 | `scenarios/coordination.py` — handled via alert lifecycle in API | D | 🔴 | [x] |
| 1.12 | Write `scenarios/salary_day.py` — false positive scenario | D | 🟡 | [x] |
| 1.13 | Seed `transaction_baseline` table — per-hour/day_type baselines | D | 🟡 | [x] |
| 1.14 | Verify seeded data — 5 agents confirmed in Neon via query | D | 🔴 | [x] |

### 1C — Mock Provider APIs
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 1.15 | Write `providers/base.py` — abstract interface | B | 🔴 | [x] |
| 1.16 | Write `providers/bkash.py` | B | 🔴 | [x] |
| 1.17 | Write `providers/nagad.py` — supports `NAGAD_DELAY_SECONDS` | B | 🔴 | [x] |
| 1.18 | Write `providers/rocket.py` | B | 🔴 | [x] |
| 1.19 | Add `NAGAD_DELAY_SECONDS` env var support | B | 🔴 | [x] |
| 1.20 | Test: `/api/agents` returns per-provider balances correctly | B | 🔴 | [x] |

---

## Phase 2 — Core Backend Engines
**Goal:** Liquidity forecasting + anomaly detection working and returning results.
**Target:** Hours 6–14

### 2A — Liquidity Engine
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.1 | Write `engines/liquidity.py` — rate, ETA, confidence per provider | A | 🔴 | [x] |
| 2.2 | Physical cash calculation alongside e-money | A | 🔴 | [x] |
| 2.3 | Data quality → confidence degradation logic | A | 🔴 | [x] |
| 2.4 | Recommended top-up amount calculation | A | 🟡 | [x] |
| 2.5 | Verified via `/api/analytics/liquidity/{agent_id}` — ETA fires for Karim bKash | A | 🔴 | [x] |
| 2.6 | Data quality degrades confidence — tested via Nagad delay | A | 🔴 | [x] |

### 2B — Anomaly Detectors
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.7 | Write `engines/anomaly/velocity.py` | A | 🔴 | [x] |
| 2.8 | Write `engines/anomaly/clustering.py` | A | 🔴 | [x] |
| 2.9 | Write `engines/anomaly/concentration.py` | A | 🔴 | [x] |
| 2.10 | Write `engines/anomaly/baseline.py` — ★ Eid/holiday multiplier | A | 🟡 | [x] |
| 2.11 | Anomaly combiner in `analytics.py` + `poller.py` — fires when ≥2 detectors flag | A | 🔴 | [x] |
| 2.12 | Velocity test — anomaly seeded in Neon for Karim bKash | A | 🔴 | [x] |
| 2.13 | Clustering test — amounts clustered 4920–5010 BDT seeded | A | 🔴 | [x] |
| 2.14 | False positive — `scenarios/salary_day.py` written | A | 🟡 | [x] |

### 2C — Balance Aggregator + Poller
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.15 | Write `scheduler/poller.py` — APScheduler every 30s | B | 🔴 | [x] |
| 2.16 | Save poll results to `provider_balances` table | B | 🔴 | [x] |
| 2.17 | Run liquidity engine after each poll | B | 🔴 | [x] |
| 2.18 | Run anomaly detectors after each poll, fire alerts | B | 🔴 | [x] |
| 2.19 | ~~Redis pub/sub~~ — replaced with in-memory WebSocket broadcast | B | 🔴 | [x] |

### 2D — Alert Router + Case Manager
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 2.20 | Write `engines/coordinator.py` — routing table by type + severity | B | 🔴 | [x] |
| 2.21 | Alert CRUD API: GET /alerts, GET /alerts/{id} with filters | B | 🔴 | [x] |
| 2.22 | Alert actions: acknowledge, escalate, resolve, false-positive | B | 🔴 | [x] |
| 2.23 | Case CRUD API: GET /cases, PATCH /cases/{id}/assign | B | 🔴 | [x] |
| 2.24 | Case note append: POST /cases/{id}/notes | B | 🔴 | [x] |

---

## Phase 3 — OpenAI Integration
**Goal:** Live Bengali alerts + anomaly narratives generated by OpenAI.
**Target:** Hours 10–16

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 3.1 | Write `ai/prompts.py` — all prompt templates centralized | A | 🔴 | [x] |
| 3.2 | Write `ai/explainer.py` — `generate_liquidity_alert_bn()` using gpt-4o-mini | A | 🔴 | [x] |
| 3.3 | Write `ai/explainer.py` — `generate_anomaly_narrative_en()` using gpt-4o | A | 🔴 | [x] |
| 3.4 | Write `ai/explainer.py` — `generate_whatif_summary()` for simulator | A | 🟡 | [x] |
| 3.5 | Write `ai/fallback.py` — template-based fallback if OpenAI times out | A | 🔴 | [x] |
| 3.6 | Async OpenAI with 10s timeout — fallback fires on failure | A | 🔴 | [x] |
| 3.7 | Tested: liquidity Bengali — 167 chars, correct Bengali script, no fallback used | A | 🔴 | [x] |
| 3.8 | Tested: anomaly Bengali mentions Eid demand, ends with "মানব পর্যালোচনা" | A | 🟡 | [x] |
| 3.9 | Fallback templates written — auto-fires if OpenAI returns None | A | 🔴 | [x] |
| 3.10 | Banglish prompt variant | A | 🟢 | [ ] |

---

## Phase 4 — Frontend Core Views
**Goal:** All 3 dashboards functional with real data.
**Target:** Hours 12–22

### 4A — Agent Dashboard
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 4.1 | Build page layout: header, Nav.tsx (Agent / Ops / Cases), dark theme | F | 🔴 | [x] |
| 4.2 | Build `DeceptiveTotal.tsx` — aggregate + animated breakdown, deceptive warning | F | 🔴 | [x] |
| 4.3 | Build `ProviderCard.tsx` — balance, data quality badge, confidence bar, ETA, topup | F | 🔴 | [x] |
| 4.4 | ETA shown in ProviderCard with color states (green/yellow/red/pulse) | F | 🔴 | [x] |
| 4.5 | Confidence bar in ProviderCard — drains based on data quality | F | 🟡 | [x] |
| 4.6 | Physical cash shown in agent header + DeceptiveTotal breakdown | F | 🔴 | [x] |
| 4.7 | Build `BengaliAlert.tsx` — Bengali + English message, confidence, owner | F | 🔴 | [x] |
| 4.8 | Agent dashboard connected to `/api/analytics/liquidity/{id}` + `/api/alerts` | F | 🔴 | [x] |
| 4.9 | WebSocket connected — tab title updates on new alert | F | 🔴 | [x] |

### 4B — Operations Dashboard
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 4.10 | Agent grid — name, area, alert count, color-coded risk (green/yellow/red) | F | 🔴 | [x] |
| 4.11 | Filter bar — by provider, severity, status | F | 🟡 | [x] |
| 4.12 | Alert queue sorted by severity (critical first) | F | 🔴 | [x] |
| 4.13 | Build `AlertCard.tsx` — Bengali preview, ETA, confidence, acknowledge/escalate | F | 🔴 | [x] |
| 4.14 | Build `EvidencePanel.tsx` — velocity/clustering/concentration evidence display | F | 🔴 | [x] |
| 4.15 | Alert queue connected to `/api/alerts` with filter params | F | 🔴 | [x] |
| 4.16 | WebSocket: new alert → reload + tab title update for critical/high | F | 🔴 | [x] |

### 4C — Case Manager
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 4.17 | Case list with status badge + coordination timeline per row | F | 🔴 | [x] |
| 4.18 | Case detail page — Bengali alert + evidence panel + audit trail | F | 🔴 | [x] |
| 4.19 | Build `CoordinationTimeline.tsx` — 4-step visual lifecycle | F | 🟡 | [x] |
| 4.20 | Note input with Enter key submit + author selector | F | 🔴 | [x] |
| 4.21 | Action buttons: Acknowledge / Escalate / Resolve / False Positive | F | 🔴 | [x] |
| 4.22 | All case actions connected to backend API | F | 🔴 | [x] |
| 4.23 | Full audit trail with author + timestamp + resolution note | F | 🟡 | [x] |

---

## Phase 5 — Unique / Exceptional Features
**Goal:** The features that separate top 3 from the rest.
**Target:** Hours 18–28

| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 5.1 | ★ `WhatIfSlider.tsx` — demand multiplier slider → live ETA recalculation | F+A | 🟡 | [ ] |
| 5.2 | ★ `POST /api/analytics/whatif` — backend recalculates with adjusted rate | A | 🟡 | [x] |
| 5.3 | ★ OpenAI generates updated advisory for what-if scenario | A | 🟢 | [x] |
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

## Phase 9 — Production Deployment
**Goal:** Live URLs for frontend (Vercel) + backend (Railway/Render) + Neon + Upstash all working together.
**Target:** Hours 30–36 (before final polish)

### 9A — Backend Deployment (FastAPI Cloud)
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 9.1 | Install FastAPI Cloud CLI: `pip install "fastapi[standard]"` | B | 🔴 | [ ] |
| 9.2 | From `/backend` directory run: `fastapi deploy` — browser opens for login automatically | B | 🔴 | [ ] |
| 9.3 | Dashboard → App → Environment Variables → **Import** → paste full `.env` content | B | 🔴 | [ ] |
| 9.4 | Mark these as **Secret** (do at creation — cannot change later): `OPENAI_API_KEY`, `DATABASE_URL`, `DATABASE_SYNC_URL`, `REDIS_URL` | B | 🔴 | [ ] |
| 9.5 | Click "Save and Redeploy" — wait for deployment to complete | B | 🔴 | [ ] |
| 9.6 | Note live URL: `https://<appname>.fastapicloud.dev` — add to frontend `.env.local` | B | 🔴 | [ ] |
| 9.7 | Run `alembic upgrade head` against Neon (run locally pointing at Neon) | B | 🔴 | [ ] |
| 9.8 | Run seed: `curl -X POST https://<appname>.fastapicloud.dev/api/seed` | B | 🔴 | [ ] |
| 9.9 | Test: `GET https://<appname>.fastapicloud.dev/api/agents` returns data | B | 🔴 | [ ] |
| 9.10 | Test: WebSocket `wss://<appname>.fastapicloud.dev/ws` connects (use Postman or wscat) | B | 🔴 | [ ] |
| 9.11 | Check logs in FastAPI Cloud dashboard → Apps → [your app] → Logs tab | B | 🟡 | [ ] |

### 9B — Frontend Deployment (Vercel)
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 9.12 | Connect GitHub repo to Vercel — set root directory to `/frontend` | F | 🔴 | [ ] |
| 9.13 | Add env vars in Vercel dashboard: `NEXT_PUBLIC_API_URL=https://<appname>.fastapicloud.dev` | F | 🔴 | [ ] |
| 9.14 | Add env var in Vercel: `NEXT_PUBLIC_WS_URL=wss://<appname>.fastapicloud.dev/ws` | F | 🔴 | [ ] |
| 9.15 | Deploy frontend → note the live Vercel URL (e.g. `https://sust-hackathon.vercel.app`) | F | 🔴 | [ ] |
| 9.16 | Update `CORS_ORIGINS` on FastAPI Cloud to include the live Vercel URL | B | 🔴 | [ ] |
| 9.17 | Dashboard → App → Environment Variables → update `CORS_ORIGINS` → Save and Redeploy | B | 🔴 | [ ] |
| 9.18 | Test: open Vercel URL in browser → Agent Dashboard loads with real Neon data | ALL | 🔴 | [ ] |
| 9.19 | Test: trigger a demo scenario → alert appears on Ops Dashboard in real time | ALL | 🔴 | [ ] |
| 9.20 | Test: Bengali alert generates correctly via OpenAI on live deployment | A | 🔴 | [ ] |

### 9C — Production Smoke Test
| # | Task | Owner | Priority | Done |
|---|------|-------|----------|------|
| 9.21 | Run full demo script end-to-end on **live production URLs** (not localhost) | ALL | 🔴 | [ ] |
| 9.22 | Verify Scenario C on production: update `NAGAD_DELAY_SECONDS=300` via dashboard → yellow badge appears | B | 🔴 | [ ] |
| 9.23 | Reset `NAGAD_DELAY_SECONDS=0` after Scenario C test — Save and Redeploy | B | 🔴 | [ ] |
| 9.24 | Check FastAPI Cloud logs during demo run — confirm no errors | B | 🟡 | [ ] |
| 9.25 | Bookmark all live URLs for demo day: Vercel URL + `https://<appname>.fastapicloud.dev/docs` | ALL | 🔴 | [ ] |

> **No cold-start risk on FastAPI Cloud** — instances are always running. No need to pre-warm before demo.

---

## Parallel Work Map (Who Does What Simultaneously)

```
Hours 0–8:
  B: Phase 0 setup — Neon + Upstash + CORS + DB schema + mock providers
  F: Scaffold Next.js + install deps + component stubs + layouts
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

Hours 30–36 (overlaps with above):
  B+F: Phase 9 — deploy backend to Railway, frontend to Vercel
       Run full demo on live production URLs
       Fix any CORS / WebSocket / cold-start issues

Hours 36–40:
  ALL: Demo rehearsal on LIVE URLs, slide building, submission prep
```

---

*Task board for Codex Community Hackathon — bKash x SUST CSE Carnival 2026*
