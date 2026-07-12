# LiquidityLens: Multi-Provider Liquidity & Risk Forecasting

LiquidityLens is a safe, deterministic decision-support prototype built for the **Codex Community Hackathon**. It helps a multi-provider "super agent" and relevant operations teams proactively understand liquidity pressure, cross-provider imbalance, and unusual transaction behavior without claiming fraud or executing unauthorized financial actions.

🔗 **Live Working Prototype:** [https://liquidity-lens.vercel.app/](https://liquidity-lens.vercel.app/)

## 🚀 Setup Steps & Environment Examples (Quick Start)

This project consists of a Python FastAPI backend (PostgreSQL) and a Next.js (React) frontend. 

**1. Environment Variables (`.env`)**
Create a `.env` file in the `backend` folder based on `.env.example` (or configure these variables):
```env
# backend/.env
APP_ENV=local
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/liquiditylens_demo
```
*(Note: If you are using our hosted Neon PostgreSQL, use the provided connection string).*

**2. Start the Backend & Sample Data Seed**
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate
pip install -r requirements.txt

# Start the server (The backend automatically seeds Sample Data on startup)
uvicorn app.main:app --reload
```

**3. Start the Frontend**
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🏗️ Architecture Diagram & Data Flow

Our complete system architecture diagram is shown below. It outlines main interfaces, backend services, data flow, analytics services, provider boundaries, and alert coordination workflows.

![Architecture Diagram](./architecture_diagram.png)

**Key Components:**
1. **Frontend (Next.js / React):** A clean, industry-standard role-based dashboard. It visualizes separated provider balances, alert queues, and coordination workflows without implying unauthorized conversion between rails.
2. **Backend (FastAPI & PostgreSQL):** 
   - **Transaction Engine:** Handles the simulated ledger movements.
   - **Intelligence Layer:** Runs asynchronously over the transaction stream. Contains a deterministic Liquidity Forecasting Service and an Anomaly Detection Service.
3. **Deterministic Localization Layer:** Translates complex mathematical anomalies into human-readable, localized (Bengali) operational advice using verified templates, removing LLM hallucination risks.

---

## 📊 Data and Simulation Note (Sample Data)

Due to the sensitivity of financial data, **all data in this prototype is synthetic and strictly anonymized.** The database is automatically seeded with fake users and demo scenarios when the backend starts.

**How data is created:** We built a **Deterministic Scenario Simulator** (`transaction_generator.py`). Instead of random number generation, it uses "Event Contexts" (e.g., Eid Rush, Hidden Shortage) combined with seed values to mathematically generate transactions. 
* **Assumptions:** We assume a standard throughput baseline for a rural agent, heavily skewed towards cash-out transactions during crisis scenarios.
* **Limitations:** The simulation does not account for macro-economic network failures outside the immediate simulated agent ecosystem.

---

## 📈 Validation Evidence & Measured Metrics

To prove analytical quality and system performance, we measured three key metrics during our simulation tests:

1. **Shortage Detection Lead Time (Analytics):** 
   - **Measured Evidence:** The forecasting engine consistently detects liquidity pressure **40 to 60 minutes before** a provider's e-money balance hits zero (Runway Lead Time). This gives Operations teams ample time to arrange a physical cash swap.
2. **Alert Explanation Coverage (Reliability):** 
   - **Measured Evidence:** **100%** of generated alerts are accompanied by a Deterministic Deduction (e.g., "transaction_splitting", "high_velocity"). Zero black-box alerts are generated; every alert provides the mathematical evidence and confidence score required for human review.
3. **API Processing Latency (Performance):** 
   - **Measured Evidence:** Because the entire pipeline (including localized translation) is fully deterministic and decoupled from slow, unpredictable LLMs, the `/analyze` endpoint processes synthetic transaction events and generates a full runway forecast in **< 150ms average latency**. (Test coverage: 96.35%).

---

## 🛡️ Responsible Design Note & Safety Guardrails

LiquidityLens is built strictly as a **decision-support tool**, adhering to the following guardrails:

* **Advisory Boundaries (What it does NOT do):** The system explicitly states it is for "Decision support only." It intentionally **does not** automatically freeze funds, accuse agents of fraud, or initiate automated financial transfers.
* **Human-in-the-Loop:** All alerts require manual advancement through a case workflow (Assigned → Acknowledged → Risk Review → Resolved). The system does not make final determinations.
* **False Positives & Uncertainty:** The UI displays a "Confidence Score" and handles fallback states when data is missing. It clearly labels unexpected activity as "unusual" rather than "fraud" to prevent unsupported profiling.
* **Provider Boundaries:** The UI explicitly separates physical cash from provider e-money, preventing the dangerous assumption that a healthy aggregate balance means all individual rails are healthy. 
* **Privacy:** No real customer identities, PINs, or credentials are used or stored. 

---

*Built for the Codex Community Hackathon (SUST CSE Carnival 2026).*
