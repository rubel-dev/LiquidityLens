# LiquidityLens Docs Audit — vs. Hackathon Problem Statement

**Auditor:** Senior Software Engineer / Judge-perspective review  
**Date:** 2026-07-11  
**Source:** `hackathon.pdf` + `docs/00` through `docs/18` + `docs/commit-ledger.md`

**Overall verdict:** The documentation is impressively thorough — governance, traceability, DB schema, workflows, and API contracts are all well-structured. But there are **6 implementation blockers** and several smaller gaps that will cause friction if not resolved before writing a single line of product code.

---

## CRITICAL — Blockers Before Implementation

### 1. OPEN-001 is unresolved: Provider names/labels

`docs/01-requirements.md:78` and `docs/12-decision-log.md` DEC-013 leave provider naming open. This affects every UI string, every scenario narrative, and every alert summary. The hackathon PDF explicitly showcases "bKash, Nagad, Rocket" and judges will expect to recognize them in context.

**Fix needed:** Resolve this now. Use synthetic-but-contextual identifiers like `BKASH-SIM`, `NAGAD-SIM`, `ROCKET-SIM` in all data/code, but allow display names like "bKash (simulated)" in UI. Amend `docs/12-decision-log.md` with a DEC-017 closing OPEN-001.

---

### 2. No API response schemas defined

`docs/06-api-contracts.md` lists paths, methods, and high-level field names (e.g. "alert,evidence,confidence,uncertainty,next_step") but defines **zero JSON schema shapes**. You cannot build the frontend (Phases 12–14) independently from the backend (Phase 10) without this.

**Fix needed:** Add a `docs/06b-api-schemas.md` (or expand doc 06) with JSON shapes for at minimum:
- `AgentOverview`
- `Alert` and `AlertDetail` (with evidence fingerprint)
- `Case` and `CaseDetail`
- `LiquidityForecast`
- `AnomalyFinding`
- `MetricObservation`

Even rough TypeScript interfaces or OpenAPI snippets would unblock parallel work.

---

### 3. Anomaly rule parameters not defined

`FR-005` says "repeated or near-identical cash-out amounts combined with abnormal transaction velocity from a small synthetic account group" — but the `rule_versions.config jsonb` schema is never specified. Phase 6 has no spec to implement against.

Without concrete parameters:
- What counts as "near-identical"? (e.g., ±2% of amount?)
- What is "abnormal velocity"? (e.g., > 3× baseline in 15 minutes?)
- What is a "small group"? (e.g., ≤ 5 unique synthetic customer refs?)
- What time window? (e.g., rolling 30 minutes?)

Metrics MET-003 (precision ≥ 0.80) and MET-004 (recall ≥ 0.80) are unmeasurable without ground truth tied to these parameters.

**Fix needed:** Add a "Rule Configuration" section to `docs/10-data-and-simulation.md` defining the exact parameters and the `rule_versions.config` JSON schema.

---

### 4. LLM abstraction interface not specified

`FR-010` and DEC-006 say "vendor-neutral LLM provider abstraction" but no interface is defined. `LLM_EXPLANATION_PROVIDER` env var exists in `docs/09-deployment.md` but no mapping is documented. Phase 8 implementors will invent their own interface — inconsistently.

**Fix needed:** Add to `docs/04-architecture.md` or a new subsection:
- The `ExplanationProvider` abstract interface (input: structured evidence dict + language, output: text)
- Supported providers mapped to env value: `anthropic`, `openai`, `none` (deterministic only)
- Timeout and retry policy before triggering deterministic fallback (FR-011)

---

### 5. Demo session / auth mechanism undefined

`docs/06-api-contracts.md` says "demo session" for auth on every endpoint. Phase 11 is "RBAC/provider-scope auth" but it comes **after** Phase 10 (APIs). This means Phase 10 APIs will be written without knowing what the auth token structure is, making Phase 11 a full retrofit — high risk of missed provider scoping.

Additionally, the "demo session" concept has no spec. Is it a hardcoded bearer token per role? A simple login form with role selection? A URL parameter?

**Fix needed:**
1. Move Phase 11 before Phase 10 in `docs/17-implementation-plan.md` and update the mermaid diagram.
2. Add a "Demo Auth Specification" section to `docs/07-security-and-safety.md`: simple role-selection login page → backend issues a JWT with `{role, provider_id, area_id}` claims → middleware enforces scope on every provider-scoped endpoint.

---

### 6. Confidence fusion algorithm not documented

`docs/04-architecture.md` lists "Confidence and decision fusion" as a module and the DB has `confidence_assessments`. But Phase 7 has no algorithm spec. There is no definition of how missing, stale, or conflicting data mathematically reduces confidence, or how liquidity and anomaly signals are combined.

**Fix needed:** Add a "Confidence Fusion Algorithm" section to `docs/08-testing-and-metrics.md` or the architecture doc, for example:

| Signal | Confidence deduction |
|---|---|
| Missing feed | −0.40 |
| Stale feed (> N minutes) | −0.20 |
| Conflicting balance | −0.30 |
| Duplicate/invalid records | −0.10 |

- Clamped to [0.0, 1.0]
- Severity tiers: HIGH (≥ 0.75), MEDIUM (0.50–0.74), LOW (< 0.50)
- Show "Insufficient data — no confident forecast" banner when confidence < 0.40

---

## IMPORTANT — Should Fix Before Phases 3–6

### 7. Bengali/Banglish fallback templates not written

`FR-011` is **Mandatory** and requires deterministic Bengali/Banglish/English templates when the LLM is unavailable. The hackathon PDF includes two illustrative Bangla alerts (Scenarios A and B). The docs acknowledge this requirement but contain **zero actual template strings**.

**Fix needed:** Add a "Deterministic Template Registry" to `docs/07-security-and-safety.md` with the actual template strings for:
- Liquidity shortage alert (Bengali, Banglish, English)
- Unusual activity alert (Bengali, Banglish, English)
- Data quality degraded notice (Bengali, Banglish, English)

Each template must include placeholders for evidence fields (provider name, shortage time, velocity count, etc.) and must use safe advisory language (`"requires review"`, not `"fraud"`).

---

### 8. Alert status vs Case status lifecycle not distinguished

The case state diagram (`docs/03-workflows.md`) defines `Open → Assigned → Acknowledged → Escalated → RiskReview → Resolved → Closed`. But the `alerts` table in `docs/05-database-design.md` also has a `status` field — and its own lifecycle is never defined.

Alerts and cases are different entities but their relationship is underspecified. It is unclear:
- What alert statuses exist (`new`, `routed`, `acknowledged`, `closed`?)
- At what severity level does an alert create a case?
- Can an alert exist without a case? (DB allows it, but logic is unstated.)

**Fix needed:** Clarify in `docs/03-workflows.md` that alerts have their own status lifecycle, separate from cases. Define the severity threshold that promotes an alert to a case. The DB constraint `alerts ||--o| cases : may_create` needs a prose rule to back it.

---

### 9. Reset scope not defined

`FR-009` (mandatory) requires demo reset and replay. Phases 3 and 17 both depend on this. Nowhere in the docs is it specified **which database tables are wiped during a reset** and what "clean state" means.

**Fix needed:** Add a "Reset Scope" table to `docs/10-data-and-simulation.md`:

| Table | On reset |
|---|---|
| `scenario_runs`, `transactions`, `provider_balance_snapshots`, `shared_cash_snapshots`, `alerts`, `cases`, `case_notes`, `case_status_history`, `escalations`, `audit_events`, `anomaly_findings`, `liquidity_forecasts`, `evidence_items`, `explanation_records`, `human_feedback`, `metric_observations` | Delete rows for the run |
| `scenarios`, `providers`, `areas`, `agents`, `roles`, `rule_versions` | Preserve |

---

### 10. OPEN-002 (hosting) must be resolved before Phase 17

Local Docker Compose is the canonical dev target but the submission requires judges to access a live prototype. If this is in-person, local is fine. If remote access is required, a cloud target is needed before Phase 17.

**Fix needed:** Resolve and close OPEN-002 in `docs/12-decision-log.md` as DEC-018 with either "in-person only, local Docker Compose" or a named cloud target and update `docs/09-deployment.md` accordingly.

---

## MINOR — Clean Up Before Implementation

### 11. Phase ordering risk: Auth after APIs

In `docs/17-implementation-plan.md` and the mermaid diagram, Phase 11 (Auth/RBAC) comes after Phase 10 (APIs). Every endpoint that touches provider-scoped data needs auth context baked in from the start. Building APIs first and retrofitting auth is the highest execution risk in the entire plan.

**Recommended fix:** Swap P10 and P11 in the mermaid diagram, or at minimum implement a thin `AuthContext` stub in Phase 10 that Phase 11 fills in. Update the task board (`docs/18-task-board.md`) accordingly.

---

### 12. `SONAR_PROJECT_KEY` missing from env var list

`docs/09-deployment.md` "Environment Variable Names" section omits `SONAR_PROJECT_KEY` even though it is named in CI-002 as a required secret. The doc says "Project key is authoritative in `sonar-project.properties`" but the env var registry is inconsistent.

**Fix needed:** Add `SONAR_PROJECT_KEY` to the env var list in `docs/09-deployment.md` with a note that it is also set in `sonar-project.properties`.

---

### 13. Demo script steps not mapped to scenario IDs

`docs/16-demo-script.md` has 10 steps but none are tagged with `SCN-001` through `SCN-005`. During the live demo with judges, this makes it harder to explain which scenario is running and cross-reference evidence.

**Fix needed:** Annotate each step in `docs/16-demo-script.md` with the scenario ID it triggers, e.g.:
- Step 1 → SCN-001 (normal state baseline)
- Step 2–3 → SCN-001 (hidden provider shortage / deceptive total)
- Step 4–5 → SCN-002 (unusual activity)
- Step 5 (data quality) → SCN-003
- Step 6 → SCN-005 (Eid false-positive, no review)
- Steps 7–9 → SCN-004 (coordinated response and closure)

---

### 14. No final presentation outline

The hackathon Section 10 deliverable "Final presentation" requires: problem, users, story-driven demo, architecture, metrics, coordination flow, risks, limitations, and next steps. None of the docs include a slide structure or outline.

**Fix needed:** Add `docs/19-presentation-outline.md` with a slide structure aligned to the judging rubric:

| Slides | Topic | Rubric weight |
|---|---|---|
| 1–2 | Problem, users, stakeholders | 15% Problem understanding |
| 3–4 | Innovation — unified view, anomaly insight | 20% Innovation |
| 5–6 | Architecture, tech stack, alert routing | 25% Technical |
| 7–8 | Data design, metrics, precision/recall | 20% Data quality |
| 9 | UX walkthrough, role views | 10% UX |
| 10 | Safety, language, provider boundaries | 5% Security |
| 11 | Live demo (or video) | 5% Demo |
| 12 | Limitations and next steps | All |

---

### 15. No README specification

Section 10 of the hackathon requires "Source repository: README, setup steps, environment examples, and sample data." There is no doc specifying what the README must cover.

**Fix needed:** Add a README checklist to `docs/09-deployment.md` covering:
- Project overview (one paragraph)
- Prerequisites (Docker, Node, Python version)
- Environment setup (`cp .env.example .env`, fill in vars)
- `docker compose up` steps
- Alembic migration command
- Seed and scenario run commands
- Link to demo walkthrough / `docs/16-demo-script.md`

---

## Submission Checklist Audit (Hackathon Section 16)

| Checklist Item | Doc Coverage | Status |
|---|---|---|
| At least two provider contexts | FR-002 | Documented — OPEN-001 still unresolved |
| Shared cash + provider-specific balances | FR-001, DATA-003 | Documented |
| Forward-looking liquidity insight | FR-004, MET-001, MET-002 | Documented |
| At least one anomaly category with evidence | FR-005, FR-006 | Documented — **rule params missing (Issue 3)** |
| Human-review + careful risk language | SAFE-002, FR-011 | Documented — **template strings missing (Issue 7)** |
| One alert with routing, ownership, ack/escalation, status | FR-007, FR-008, WF-011..017 | Documented |
| Repository, data, README, architecture | doc 04, doc 10 | Architecture ✓ — **README spec missing (Issue 15)** |
| At least three metrics measured and explained | MET-001..MET-012 | 12 metrics documented — strong |
| Failure, uncertainty, false-positive | NFR-003, FAIL-001..007 | Documented |
| Safety, privacy, boundaries, limitations | doc 07 | Documented |
| Final presentation | — | **Missing (Issue 14)** |

---

## Priority Fix Order

| # | Fix | Blocks |
|---|---|---|
| 1 | Close OPEN-001 — decide provider display names | All UI, all scenario narrative |
| 2 | Define API response schemas | Frontend/backend parallel development |
| 3 | Define anomaly rule parameters | Phase 6, MET-003, MET-004 |
| 4 | Define LLM abstraction interface | Phase 8 |
| 5 | Define demo auth mechanism + move Phase 11 before Phase 10 | Phase 10, Phase 11 |
| 6 | Define confidence fusion algorithm | Phase 7 |
| 7 | Write Bangla/Banglish fallback templates | FR-011 (mandatory) |
| 8 | Clarify alert vs case status lifecycle | Phase 9, DB model |
| 9 | Define reset scope | Phase 3, Phase 17 |
| 10 | Resolve OPEN-002 (hosting) | Phase 17 demo packaging |
| 11 | Fix auth/API phase ordering in plan | Phase 10–11 execution |
| 12 | Add SONAR_PROJECT_KEY to env var list | Minor |
| 13 | Map demo steps to scenario IDs | Demo clarity for judges |
| 14 | Add final presentation outline | Submission deliverable |
| 15 | Add README specification | Submission deliverable |
