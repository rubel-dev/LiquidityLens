# Hackathon Summary — Codex Community Hackathon
**bKash presents SUST CSE Carnival 2026**

---

## What Is the Problem?

A mobile money agent shop (bKash / Nagad / Rocket counter) serves customers from multiple providers.

- They use **one shared physical cash drawer**
- But each provider has its own **separate e-money balance**
- The agent cannot easily see the **full combined picture**
- They may run out of cash for one provider even if the total looks fine

**Your job:** Build a smart prototype that solves this visibility, prediction, and coordination problem.

---

## 3 Core Problems to Solve

| # | Problem | What to Build |
|---|---------|---------------|
| 1 | **Liquidity Shortage** | Predict *when* cash or a provider balance will run out and warn early |
| 2 | **Unusual Activity** | Detect suspicious patterns — but **never call it fraud**, say "requires review" |
| 3 | **Coordination** | Show *who* should handle an alert, assign ownership, track resolution |

---

## Who Uses This System?

| User | Need |
|------|------|
| **Agent** | See all balances in one place, know if trouble is coming |
| **Field Officer / Ops Team** | Monitor agents, route alerts, coordinate fixes |
| **Risk Analyst** | Review flagged activity with evidence (does NOT make final fraud call) |
| **Management** | See area-level risk overview |
| **Customers** | Get more reliable service |

---

## What You MUST Build (Mandatory)

1. Show **shared physical cash + each provider's e-money balance** separately
2. Predict **which provider will face a shortage and roughly when**
3. Detect **at least one type of unusual transaction** and explain why it was flagged
4. Use **careful language** — "unusual", "requires review" — never "fraud"
5. For one alert, show: **who gets it → who owns it → recommended action → final status**
6. Show **lower confidence** when data is missing or delayed
7. Use **AI / analytics** as a meaningful component (mandatory)

---

## What You Must NOT Do

- No real wallets, real transactions, or real customer data
- No automatic blocking, freezing, or fraud accusations
- No merging balances between providers
- No collecting PINs / OTPs / passwords
- No claiming regulatory or production fraud-detection approval

---

## 4 Key Demo Scenarios

| Scenario | Situation |
|----------|-----------|
| **A — Hidden provider shortage** | One provider's e-money is almost out even though the total looks fine |
| **B — Liquidity + unusual activity** | Cash dropping fast AND suspicious repeated transactions at the same time |
| **C — Data inconsistency** | Provider data arrives late or conflicts — show degraded confidence, don't mislead |
| **D — Coordinated response** | Alert fires → assigned → acknowledged → resolved / escalated (full workflow) |

---

## Example Bengali Alerts

**Liquidity Alert:**
> বর্তমান লেনদেনের ধারা অনুযায়ী বিকেল ৫টা ২০ মিনিটের মধ্যে আপনার নগদ টাকা শেষ হয়ে যেতে পারে। সবচেয়ে বেশি চাপ আসছে বিকাশ ক্যাশ-আউট থেকে।

**Unusual Activity Alert:**
> গত ১২ মিনিটে স্বাভাবিকের তুলনায় অনেক বেশি ক্যাশ-আউট হয়েছে। কয়েকটি লেনদেনের পরিমাণ প্রায় একই এবং অল্প কয়েকটি অ্যাকাউন্ট থেকে বারবার অনুরোধ এসেছে।

---

## Evaluation Weights

| Category | Weight |
|----------|--------|
| Technical Implementation & Integration | 25% |
| Innovation & Decision Value | 20% |
| Data & Analytical Quality | 20% |
| Problem Understanding | 15% |
| UX & Explainability | 10% |
| Security & Responsible AI | 5% |
| Presentation & Demo | 5% |

---

## Required Deliverables

| Deliverable | What Judges Expect |
|-------------|-------------------|
| **Working Prototype** | Live flow: balances → alert → coordination → resolution |
| **Source Repository** | Code, README, setup steps, sample data |
| **Architecture Diagram** | Interfaces, backend, data flow, provider boundaries, alert flow |
| **Data & Simulation Note** | How synthetic data and anomaly scenarios were created |
| **Validation Evidence** | At least **3 measured metrics** |
| **Responsible-Design Note** | Privacy, human review, false positives, what the system won't do |
| **Final Presentation** | Problem, demo, architecture, metrics, limitations, next steps |

---

## Submission Checklist

- [ ] At least two providers represented distinctly
- [ ] Shared cash and provider-specific balances demonstrated
- [ ] Forward-looking liquidity insight shown
- [ ] At least one anomaly with evidence
- [ ] Human-review language used (no fraud accusations)
- [ ] One alert shows routing → ownership → acknowledgement → resolution
- [ ] Repository, data, README, and architecture complete
- [ ] At least three metrics measured and explained
- [ ] Failure, uncertainty, and false-positive handling shown
- [ ] Safety, privacy, and limitations stated
- [ ] Final presentation ready

---

## One-Line Summary

> Build a **smart dashboard** for mobile money agents that shows a unified cash + balance view across providers, predicts shortages, flags suspicious activity with evidence, and routes alerts to the right person — using **simulated data** and **AI**, without making real financial decisions.

---

*Hackathon: Codex Community Hackathon — bKash x SUST CSE Carnival 2026*
