"use client";

import { useMemo, useState } from "react";

import { FoundationStatus } from "@/features/foundation/FoundationStatus";
import {
  agentOverview,
  alertDetail,
  caseDetail,
  demoScenarios,
  explanationCopy,
  metricObservations,
  scenarioFeedStates,
} from "@/lib/demoData";
import type {
  AgentOverview,
  CaseStatus,
  DemoRole,
  DemoScenarioCode,
  ExplanationLanguage,
  ProviderBalance,
} from "@/types/demo";

const roles: Array<{ id: DemoRole; label: string; short: string }> = [
  { id: "agent", label: "Agent outlet", short: "Agent" },
  { id: "operations", label: "Provider operations", short: "Operations" },
  { id: "field_officer", label: "Field officer", short: "Field" },
  { id: "risk_reviewer", label: "Risk reviewer", short: "Risk" },
  { id: "manager", label: "Manager & judge", short: "Manager" },
  { id: "demo_operator", label: "Demo operator", short: "Demo" },
];

const caseSteps: Array<{ status: CaseStatus; label: string }> = [
  { status: "open", label: "Open" },
  { status: "assigned", label: "Assigned" },
  { status: "acknowledged", label: "Acknowledged" },
  { status: "escalated", label: "Escalated" },
  { status: "risk_review", label: "Risk review" },
  { status: "resolved", label: "Resolved" },
  { status: "closed", label: "Closed" },
];

const statusRank = Object.fromEntries(
  caseSteps.map((step, index) => [step.status, index]),
) as Record<CaseStatus, number>;

const nextCaseAction: Partial<
  Record<CaseStatus, { label: string; next: CaseStatus }>
> = {
  open: { label: "Assign to field officer", next: "assigned" },
  assigned: { label: "Acknowledge", next: "acknowledged" },
  acknowledged: { label: "Escalate for review", next: "escalated" },
  escalated: { label: "Start risk review", next: "risk_review" },
  risk_review: { label: "Resolve with rationale", next: "resolved" },
  resolved: { label: "Close case", next: "closed" },
};

function formatMoney(amount: string) {
  return `৳${Number(amount).toLocaleString("en-BD", {
    maximumFractionDigits: 0,
  })}`;
}

function formatRunway(minutes: number | null) {
  if (minutes === null) return "No confident forecast";
  if (minutes < 60) return `${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  return remainder === 0 ? `${hours} hr` : `${hours} hr ${remainder} min`;
}

function titleCase(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function roleScope(role: DemoRole) {
  const scope: Record<DemoRole, string> = {
    agent: "Outlet liquidity only · shared cash remains separate",
    operations: "Provider-scoped routing, assignment, and ownership",
    field_officer: "Acknowledgement and approved coordination actions",
    risk_reviewer: "Evidence, uncertainty, and human review",
    manager: "Metrics, auditability, and delivery evidence",
    demo_operator: "Deterministic scenario controls and golden flow",
  };
  return scope[role];
}

function scenarioOverview(code: DemoScenarioCode): AgentOverview {
  if (code === "SCN-003") {
    return {
      ...agentOverview,
      provider_balances: agentOverview.provider_balances.map((provider) =>
        provider.provider_code === "NAGAD-SIM"
          ? { ...provider, runway_minutes: null, status: "insufficient_data" }
          : provider,
      ),
      confidence: {
        ...agentOverview.confidence,
        score: 0.3,
        tier: "low",
        uncertainty: ["Nagad feed is missing", "Rocket snapshots conflict"],
      },
    };
  }

  if (code === "SCN-005") {
    return {
      ...agentOverview,
      provider_balances: agentOverview.provider_balances.map((provider) => ({
        ...provider,
        runway_minutes:
          provider.runway_minutes === null ? 180 : provider.runway_minutes + 80,
        status: "healthy",
      })),
      deceptive_total: {
        ...agentOverview.deceptive_total,
        appears_healthy: true,
        provider_at_risk: null,
      },
      active_alert_count: 0,
      confidence: {
        ...agentOverview.confidence,
        score: 0.9,
        tier: "high",
        deductions: [],
        uncertainty: [
          "Demand remains elevated but matches the synthetic Eid baseline",
        ],
      },
    };
  }

  return agentOverview;
}

function ProviderBalanceCard({ provider }: { provider: ProviderBalance }) {
  const unavailable = provider.status === "insufficient_data";
  return (
    <article className={`provider-card provider-${provider.status}`}>
      <div className="provider-card-head">
        <div>
          <p className="provider-code">{provider.provider_code}</p>
          <h3>{provider.display_name}</h3>
        </div>
        <span className={`status-chip status-${provider.status}`}>
          {titleCase(provider.status)}
        </span>
      </div>
      <strong className="balance-value">
        {unavailable
          ? "Balance unavailable"
          : formatMoney(provider.balance.amount)}
      </strong>
      <div className="runway-line">
        <span>Estimated runway</span>
        <strong>{formatRunway(provider.runway_minutes)}</strong>
      </div>
      <div className="runway-track" aria-hidden="true">
        <span
          style={{
            width: unavailable
              ? "12%"
              : `${Math.min(100, Math.max(12, provider.runway_minutes ?? 0))}%`,
          }}
        />
      </div>
    </article>
  );
}

function AgentWorkspace({ overview }: { overview: AgentOverview }) {
  return (
    <>
      <section
        className="provider-grid"
        aria-label="Separate provider balances"
      >
        {overview.provider_balances.map((provider) => (
          <ProviderBalanceCard
            key={provider.provider_code}
            provider={provider}
          />
        ))}
      </section>
      <section className="split-grid">
        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Outlet guidance</p>
              <h2>What needs attention now</h2>
            </div>
            <span className="human-badge">Advisory only</span>
          </div>
          <p className="lead-copy">
            Keep provider e-money and physical cash decisions separate.
            Coordinate approved liquidity support through the responsible
            provider operations channel.
          </p>
          <div className="callout safe-callout">
            No transfer, wallet merge, freeze, or automatic financial action can
            be initiated from LiquidityLens.
          </div>
        </article>
        <DataQualityPanel overview={overview} />
      </section>
    </>
  );
}

function DataQualityPanel({ overview }: { overview: AgentOverview }) {
  return (
    <article className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Confidence</p>
          <h2>Data quality impact</h2>
        </div>
        <span
          className={`confidence-ring confidence-${overview.confidence.tier}`}
        >
          {Math.round(overview.confidence.score * 100)}%
        </span>
      </div>
      {overview.confidence.deductions.length > 0 ? (
        <ul className="deduction-list">
          {overview.confidence.deductions.map((deduction) => (
            <li key={deduction.reason}>
              <span>{titleCase(deduction.reason)}</span>
              <strong>-{Math.round(deduction.amount * 100)}%</strong>
            </li>
          ))}
        </ul>
      ) : (
        <p className="positive-copy">
          No active quality deduction for this scenario.
        </p>
      )}
      {overview.confidence.score < 0.4 && (
        <div className="callout danger-callout">
          Insufficient data — no confident forecast. Missing values remain
          unknown, not zero.
        </div>
      )}
    </article>
  );
}

type CaseWorkspaceProps = {
  status: CaseStatus;
  activeRole: DemoRole;
  onAdvance: () => void;
};

function CaseWorkspace({ status, activeRole, onAdvance }: CaseWorkspaceProps) {
  const action = nextCaseAction[status];
  const mayAct = ["operations", "field_officer", "risk_reviewer"].includes(
    activeRole,
  );
  return (
    <article className="panel case-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">
            {caseDetail.case_id} · version {caseDetail.version}
          </p>
          <h2>Case lifecycle</h2>
        </div>
        <span className="status-chip status-watch">{titleCase(status)}</span>
      </div>
      <ol className="case-timeline" aria-label="Case status progression">
        {caseSteps.map((step) => (
          <li
            className={
              statusRank[step.status] <= statusRank[status] ? "complete" : ""
            }
            key={step.status}
          >
            <span>{step.label}</span>
          </li>
        ))}
      </ol>
      <div className="case-note">
        <strong>Latest note</strong>
        <p>{caseDetail.notes[0]?.body}</p>
      </div>
      {action && mayAct && (
        <button
          className="primary-button full-button"
          onClick={onAdvance}
          type="button"
        >
          {action.label}
        </button>
      )}
      {!mayAct && (
        <p className="permission-note">Read-only in the selected demo role.</p>
      )}
    </article>
  );
}

function AlertWorkspace({
  language,
  setLanguage,
}: {
  language: ExplanationLanguage;
  setLanguage: (language: ExplanationLanguage) => void;
}) {
  const evidence = Object.values(alertDetail.evidence_fingerprint).flat();
  return (
    <article className="panel alert-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">
            {alertDetail.alert_id} · {alertDetail.provider_code}
          </p>
          <h2>Review-oriented alert</h2>
        </div>
        <span className="status-chip status-shortage_risk">High priority</span>
      </div>
      <p className="lead-copy">{alertDetail.reason}</p>
      <div className="alert-meta">
        <span>
          Owner <strong>{alertDetail.owner_user_id}</strong>
        </span>
        <span>
          Confidence <strong>81% · High</strong>
        </span>
        <span>
          Status <strong>{titleCase(alertDetail.status)}</strong>
        </span>
      </div>
      <div className="language-control" aria-label="Explanation language">
        {(["en", "banglish", "bn"] as ExplanationLanguage[]).map((item) => (
          <button
            className={language === item ? "selected" : ""}
            key={item}
            onClick={() => setLanguage(item)}
            type="button"
          >
            {item === "en"
              ? "English"
              : item === "banglish"
                ? "Banglish"
                : "বাংলা"}
          </button>
        ))}
      </div>
      <div className="explanation-box">
        <p>{explanationCopy[language]}</p>
        <small>
          Deterministic template fallback · safe if an LLM is unavailable
        </small>
      </div>
      <h3>Evidence fingerprint</h3>
      <div className="evidence-grid">
        {evidence.map((item) => (
          <div className="evidence-item" key={item.evidence_id}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            <div className="weight-track">
              <span style={{ width: `${item.weight * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
      <div className="callout safe-callout">
        Recommended next step: {alertDetail.recommended_next_step}
      </div>
    </article>
  );
}

function ManagerWorkspace() {
  return (
    <section className="split-grid">
      <article className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Evaluation evidence</p>
            <h2>Metrics</h2>
          </div>
          <span className="human-badge">Synthetic fixtures</span>
        </div>
        <div className="metric-list">
          {metricObservations.map((metric) => (
            <div className="metric-row" key={metric.metric_id}>
              <span className="metric-id">{metric.metric_id}</span>
              <div>
                <strong>{metric.name}</strong>
                <small>{metric.evidence_source}</small>
              </div>
              <div className="metric-result">
                <strong>{metric.value}</strong>
                <small>{metric.target}</small>
              </div>
            </div>
          ))}
        </div>
      </article>
      <article className="panel">
        <p className="eyebrow">Append-only evidence</p>
        <h2>Audit trail</h2>
        <ol className="audit-list">
          <li>
            <time>09:34</time>
            <div>
              <strong>Alert created</strong>
              <span>AUD-1021 · deterministic rule</span>
            </div>
          </li>
          <li>
            <time>09:38</time>
            <div>
              <strong>Owner assigned</strong>
              <span>AUD-1024 · provider scope checked</span>
            </div>
          </li>
          <li>
            <time>09:41</time>
            <div>
              <strong>Acknowledged</strong>
              <span>AUD-1025 · field officer</span>
            </div>
          </li>
          <li>
            <time>09:43</time>
            <div>
              <strong>Review requested</strong>
              <span>AUD-1026 · human decision</span>
            </div>
          </li>
        </ol>
      </article>
    </section>
  );
}

export function DemoDashboard() {
  const [activeRole, setActiveRole] = useState<DemoRole>("operations");
  const [activeScenario, setActiveScenario] =
    useState<DemoScenarioCode>("SCN-001");
  const [caseStatus, setCaseStatus] = useState<CaseStatus>("open");
  const [language, setLanguage] = useState<ExplanationLanguage>("en");
  const [runMessage, setRunMessage] = useState("Fixture loaded · ready to run");
  const [replayCount, setReplayCount] = useState(0);

  const selectedScenario = useMemo(
    () =>
      demoScenarios.find((scenario) => scenario.code === activeScenario) ??
      demoScenarios[0],
    [activeScenario],
  );
  const overview = useMemo(
    () => scenarioOverview(activeScenario),
    [activeScenario],
  );
  const feedStates = scenarioFeedStates[activeScenario] ?? [];

  function selectScenario(code: DemoScenarioCode) {
    setActiveScenario(code);
    setCaseStatus("open");
    setReplayCount(0);
    setRunMessage("Fixture loaded · ready to run");
  }

  function runScenario(action: "run" | "replay" | "reset") {
    if (action === "reset") {
      setCaseStatus("open");
      setReplayCount(0);
      setRunMessage("Selected run reset · reference data preserved");
      return;
    }
    if (action === "replay") {
      setReplayCount((count) => count + 1);
      setRunMessage("Replay matched original seed and fingerprint");
      return;
    }
    setRunMessage("Scenario complete · deterministic evidence ready");
  }

  function advanceCase() {
    const action = nextCaseAction[caseStatus];
    if (action) {
      setCaseStatus(action.next);
      setRunMessage(
        `${titleCase(action.next)} recorded in the local audit preview`,
      );
    }
  }

  const showAlert = activeScenario !== "SCN-005";

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            LL
          </span>
          <div>
            <p className="eyebrow">LiquidityLens</p>
            <h1>Liquidity command centre</h1>
          </div>
        </div>
        <div className="header-status">
          <span className="synthetic-badge">Synthetic data only</span>
          <FoundationStatus />
        </div>
      </header>

      <nav className="role-nav" aria-label="Demo role views">
        <div>
          <p className="eyebrow">View as</p>
          <div className="role-tabs" role="tablist" aria-label="Demo roles">
            {roles.map((role) => (
              <button
                aria-selected={activeRole === role.id}
                className={activeRole === role.id ? "selected" : ""}
                key={role.id}
                onClick={() => setActiveRole(role.id)}
                role="tab"
                title={role.label}
                type="button"
              >
                {role.short}
              </button>
            ))}
          </div>
        </div>
        <p className="scope-copy">
          <strong>{roles.find((role) => role.id === activeRole)?.label}</strong>
          <span>{roleScope(activeRole)}</span>
        </p>
      </nav>

      <section className="scenario-console" aria-label="Scenario controls">
        <div className="scenario-copy">
          <div className={`scenario-icon tone-${selectedScenario.tone}`}>
            {activeScenario.slice(-1)}
          </div>
          <div>
            <p className="eyebrow">{selectedScenario.catalog_code}</p>
            <h2>{selectedScenario.title}</h2>
            <p>{selectedScenario.summary}</p>
          </div>
        </div>
        <label className="scenario-select-label" htmlFor="scenario-select">
          <span>Scenario</span>
          <select
            id="scenario-select"
            onChange={(event) =>
              selectScenario(event.target.value as DemoScenarioCode)
            }
            value={activeScenario}
          >
            {demoScenarios.map((scenario) => (
              <option key={scenario.code} value={scenario.code}>
                {scenario.code} · {scenario.title}
              </option>
            ))}
          </select>
        </label>
        <div className="scenario-actions">
          <button
            className="primary-button"
            onClick={() => runScenario("run")}
            type="button"
          >
            Run scenario
          </button>
          <button
            className="secondary-button"
            onClick={() => runScenario("replay")}
            type="button"
          >
            Replay{replayCount > 0 ? ` · ${replayCount}` : ""}
          </button>
          <button
            className="ghost-button"
            onClick={() => runScenario("reset")}
            type="button"
          >
            Reset
          </button>
        </div>
      </section>

      <div className="run-toast" role="status">
        <span />
        {runMessage}
      </div>

      <section className="hero-grid" aria-label="Agent liquidity overview">
        <article className="liquidity-hero">
          <div className="hero-heading">
            <div>
              <p className="eyebrow">
                {overview.agent_id} · {overview.area_id}
              </p>
              <h2>{overview.display_name}</h2>
            </div>
            <span className="active-alerts">
              {overview.active_alert_count} active alerts
            </span>
          </div>
          <div className="hero-stats">
            <div>
              <span>Shared physical cash</span>
              <strong>{formatMoney(overview.shared_cash.amount)}</strong>
              <small>
                {formatRunway(overview.shared_cash_runway_minutes)} runway
              </small>
            </div>
            <div>
              <span>Provider e-money total</span>
              <strong>
                {formatMoney(
                  String(
                    Number(overview.deceptive_total.aggregate_balance.amount) -
                      Number(overview.shared_cash.amount),
                  ),
                )}
              </strong>
              <small>Never used to offset one provider</small>
            </div>
            <div>
              <span>Visible aggregate</span>
              <strong>
                {formatMoney(overview.deceptive_total.aggregate_balance.amount)}
              </strong>
              <small>Context only · not a liquidity decision</small>
            </div>
          </div>
        </article>
        <aside
          className={`deceptive-card ${overview.deceptive_total.provider_at_risk ? "is-risk" : "is-stable"}`}
        >
          <p className="eyebrow">Deceptive total check</p>
          <h2>
            {overview.deceptive_total.provider_at_risk
              ? "Aggregate healthy. One rail is not."
              : "Demand is elevated but expected."}
          </h2>
          <p>
            {overview.deceptive_total.provider_at_risk
              ? `${overview.deceptive_total.provider_at_risk} has only 24 minutes of estimated runway.`
              : "The pattern is consistent with expected demand; no additional review is currently recommended."}
          </p>
          <div className="comparison-line">
            <span>Aggregate signal</span>
            <strong>Healthy</strong>
          </div>
          <div className="comparison-line">
            <span>Provider signal</span>
            <strong>
              {overview.deceptive_total.provider_at_risk
                ? "Shortage risk"
                : "Healthy"}
            </strong>
          </div>
        </aside>
      </section>

      <section className="feed-strip" aria-label="Provider feed status">
        {feedStates.map((feed) => (
          <div key={feed.provider_code}>
            <span className={`feed-dot feed-${feed.status}`} />
            <div>
              <strong>{feed.label}</strong>
              <small>{feed.detail}</small>
            </div>
          </div>
        ))}
      </section>

      {activeRole === "agent" && <AgentWorkspace overview={overview} />}

      {(activeRole === "operations" || activeRole === "field_officer") &&
        (showAlert ? (
          <section className="workspace-grid">
            <AlertWorkspace language={language} setLanguage={setLanguage} />
            <CaseWorkspace
              activeRole={activeRole}
              onAdvance={advanceCase}
              status={caseStatus}
            />
          </section>
        ) : (
          <section className="panel expected-state">
            <span>✓</span>
            <div>
              <p className="eyebrow">No review case created</p>
              <h2>Expected demand correctly stays out of the case queue</h2>
              <p>
                The pattern is consistent with expected demand; no additional
                review is currently recommended.
              </p>
            </div>
          </section>
        ))}

      {activeRole === "risk_reviewer" && (
        <section className="workspace-grid risk-layout">
          <AlertWorkspace language={language} setLanguage={setLanguage} />
          <div className="stacked-panels">
            <DataQualityPanel overview={overview} />
            <CaseWorkspace
              activeRole={activeRole}
              onAdvance={advanceCase}
              status={caseStatus}
            />
          </div>
        </section>
      )}

      {activeRole === "manager" && <ManagerWorkspace />}

      {activeRole === "demo_operator" && (
        <section className="split-grid">
          <article className="panel">
            <p className="eyebrow">Golden flow</p>
            <h2>10 demo checkpoints</h2>
            <ol className="demo-checklist">
              {demoScenarios.map((scenario) => (
                <li
                  className={scenario.code === activeScenario ? "active" : ""}
                  key={scenario.code}
                >
                  <strong>{scenario.code}</strong>
                  <span>{scenario.checkpoint}</span>
                </li>
              ))}
            </ol>
          </article>
          <article className="panel">
            <p className="eyebrow">Determinism</p>
            <h2>Run provenance</h2>
            <dl className="provenance-list">
              <div>
                <dt>Run ID</dt>
                <dd>SIM-RUN-000001</dd>
              </div>
              <div>
                <dt>Seed</dt>
                <dd>5001</dd>
              </div>
              <div>
                <dt>Generator</dt>
                <dd>scenario-generator-v1</dd>
              </div>
              <div>
                <dt>Profile</dt>
                <dd>demo</dd>
              </div>
              <div>
                <dt>Fingerprint</dt>
                <dd>154bb67c…a5b33</dd>
              </div>
            </dl>
          </article>
        </section>
      )}

      <footer className="product-footer">
        <span>Decision support, not financial execution</span>
        <span>
          Feature data is a contract-aligned demo fixture until `/api/v1`
          feature endpoints ship
        </span>
      </footer>
    </main>
  );
}
