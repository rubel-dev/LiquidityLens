# Hackathon Championship Implementation Plan

## Current State

Your frontend IS connected — it calls `runScenario`, `resetScenarioRun`, `replayScenarioRun` via the backend API. However, the **critical missing piece** is:

> [!CAUTION]
> **Running a scenario only generates raw data (transactions, balances, feed statuses). It does NOT trigger the forecasting engine, anomaly detection, or alert generation.** There is no API endpoint that chains `Scenario → Forecast → Anomaly → Alert`. Each service (`LiquidityForecastingService`, `AnomalyDetectionService`, `AlertService`) exists in isolation — nothing calls them after a scenario run completes.

The dashboard then shows fixture data from `demoData.ts` for forecasts, alerts, and cases because no live data exists in the database to fetch.

---

## Priority 1: Analysis Pipeline API (CRITICAL — without this, the demo is dead)

**Problem**: After `POST /scenarios/{code}/run`, the database contains transactions/balances but zero forecasts, zero anomaly findings, and zero alerts. The frontend has no live data to display.

**Solution**: Create a single `POST /api/v1/analyze/{run_ref}` endpoint that:
1. Finds the scenario run and its agent
2. Calls `LiquidityForecastingService.forecast_agent()` → persists forecasts
3. Calls `AnomalyDetectionService.detect_agent()` → persists findings
4. For each forecast with actionable risk → calls `AlertService.create_liquidity_alert()`
5. For each anomaly finding → calls `AlertService.create_anomaly_alert()`
6. For each degraded feed → calls `AlertService.create_data_quality_alert()`
7. Returns a summary of what was generated

### Files to create/modify

#### [NEW] [analyze.py](file:///c:/Users/salman/Desktop/LiquidityLens/backend/app/api/routes/analyze.py)
New route file with the pipeline endpoint:
```
POST /analyze/{run_ref}
→ Returns: { forecasts_created, findings_created, alerts_created, details }
```

#### [MODIFY] [main.py](file:///c:/Users/salman/Desktop/LiquidityLens/backend/app/main.py)
Register the new `analyze_router` alongside existing routers.

**Estimated effort**: ~120 lines of Python

---

## Priority 2: Fix Backend Deployment (CRITICAL)

**Problem**: Alembic migrations hang on Neon's connection pooler during startup, preventing the server from ever accepting requests.

**Solution** (already partially done):
1. ✅ Remove automatic migrations from `lifespan()` — **done locally, needs push**
2. Update `DATABASE_SYNC_URL` in FastAPI Cloud env vars to use direct connection (remove `-pooler`)
3. Push code and verify logs show `Application startup complete`

**Estimated effort**: 5 minutes (env var change + git push)

---

## Priority 3: Wire Frontend to Live API Data (HIGH)

**Problem**: After scenario run, the dashboard renders hardcoded data from [demoData.ts](file:///c:/Users/salman/Desktop/LiquidityLens/frontend/src/lib/demoData.ts). It needs to call the analysis pipeline and then fetch live results.

### Files to modify

#### [MODIFY] [api.ts](file:///c:/Users/salman/Desktop/LiquidityLens/frontend/src/lib/api.ts)
Add `analyzeRun()` function that calls the new pipeline endpoint.

#### [MODIFY] [DemoDashboard.tsx](file:///c:/Users/salman/Desktop/LiquidityLens/frontend/src/features/demo/DemoDashboard.tsx)
After a successful `runScenario()` call:
1. Call `analyzeRun(runRef)` to trigger the pipeline
2. Call `listForecasts()` to get live forecast data
3. Call `listAlerts()` to get live alerts
4. Call `listFindings()` to get live anomaly findings
5. Replace the fixture-based `scenarioOverview()` / `alertDetail` / `caseDetail` with the API responses
6. Keep the existing fixture data as fallback when no scenario has been run

**Estimated effort**: ~80 lines of TypeScript changes

---

## Priority 4: Bangla Explanations (DIFFERENTIATOR)

**Problem**: The problem statement explicitly includes Bangla alert examples. Your `explanationCopy` fixture in `demoData.ts` already has Bangla text, but the backend has no explanation generation.

**Solution**: The Explanation Service (Phase 8) is marked "Not started" in your docs. Since you cannot use LLM in the liquidity module, and the problem says explanations should be "safe" and "advisory":

Create a simple **template-based explanation engine** that:
- Takes a `ForecastResult` or `AnomalyFindingResult`
- Fills a Bangla template with the actual numbers (runway, shortage time, provider name, confidence)
- Returns both English and Bangla text
- No LLM needed — just string templates with variable substitution

### Files to create

#### [NEW] [explanation_service.py](file:///c:/Users/salman/Desktop/LiquidityLens/backend/app/explanations/service.py)
Template-based explanation generator with Bangla support.

#### [MODIFY] [analyze.py](file:///c:/Users/salman/Desktop/LiquidityLens/backend/app/api/routes/analyze.py)
Include explanation text in the analysis pipeline response.

**Estimated effort**: ~80 lines of Python

---

## Priority 5: Polish for Judges (NICE TO HAVE)

These are lower priority but would increase your score:

| Item | Impact | Effort |
|---|---|---|
| Show data quality indicator per provider feed in the UI | Addresses Scenario C directly | Small |
| Show measured metrics (forecast error, anomaly precision) in the Manager view | Submission checklist requirement | Small |
| Add a second anomaly rule (high-value single transaction) | "Innovation" score boost | Medium |

---

## Execution Order

```
Step 1: Push the migration fix → verify backend starts (5 min)
Step 2: Build the analysis pipeline API endpoint (45 min)
Step 3: Wire frontend to call analyze + fetch live data (30 min)  
Step 4: Test end-to-end: Run scenario → see live forecasts/alerts (15 min)
Step 5: Add Bangla explanation templates (30 min)
Step 6: Final push + verify on deployed URLs (15 min)
```

**Total estimated time: ~2.5 hours**

---

## Submission Checklist Verification

| Requirement | Status |
|---|---|
| At least two provider contexts represented distinctly | ✅ bKash-SIM, Nagad-SIM, Rocket-SIM |
| Shared cash and provider-specific balances demonstrated | ✅ Separate forecast scopes |
| Forward-looking liquidity insight demonstrated | ⚠️ Engine exists, needs pipeline API to surface it |
| At least one anomaly category demonstrated with evidence | ⚠️ Engine exists, needs pipeline API to surface it |
| Human-review and careful risk language included | ✅ In code |
| At least one alert demonstrates routing, ownership, acknowledgement, escalation, resolution | ⚠️ Services exist, needs live flow |
| Repository, data, README, and architecture complete | ✅ Excellent docs |
| At least three metrics measured and explained | ✅ Forecast error, anomaly precision/recall, latency |
| Failure, uncertainty, and false-positive considerations shown | ✅ Confidence degradation, limitations |
| Safety, privacy, boundaries, and limitations stated | ✅ Docs + code |
| Final presentation ready | ❌ Need live demo flow first |

> [!IMPORTANT]
> **After Priority 1-3, every ⚠️ becomes ✅.** The engines are built — they just need to be called and surfaced. Shall I start with the analysis pipeline API?
