import type {
  AgentOverview,
  AlertDetail,
  CaseDetail,
  DemoScenario,
  ExplanationLanguage,
  FeedState,
  MetricObservation,
} from "@/types/demo";

export const demoScenarios: DemoScenario[] = [
  {
    code: "SCN-001",
    catalog_code: "hidden_provider_shortage",
    title: "Hidden provider shortage",
    summary:
      "Aggregate value appears healthy while one provider runway is short.",
    checkpoint: "Deceptive total + runway",
    tone: "critical",
  },
  {
    code: "SCN-002",
    catalog_code: "liquidity_pressure_unusual_activity",
    title: "Liquidity pressure + unusual activity",
    summary: "Near-identical cash-out velocity requires human review.",
    checkpoint: "Evidence fingerprint",
    tone: "warning",
  },
  {
    code: "SCN-003",
    catalog_code: "missing_feed",
    title: "Degraded data quality",
    summary: "Missing, stale, and conflicting feed states reduce confidence.",
    checkpoint: "Graceful degradation",
    tone: "degraded",
  },
  {
    code: "SCN-004",
    catalog_code: "coordinated_response",
    title: "Coordinated response",
    summary: "Alert ownership, escalation, review, and closure are auditable.",
    checkpoint: "Human workflow",
    tone: "warning",
  },
  {
    code: "SCN-005",
    catalog_code: "eid_rush",
    title: "Expected Eid demand",
    summary:
      "Demand spike is expected and does not automatically become a review case.",
    checkpoint: "False-positive control",
    tone: "stable",
  },
];

export const scenarioFeedStates: Record<string, FeedState[]> = {
  "SCN-001": [
    {
      provider_code: "BKASH-SIM",
      label: "bKash (simulated)",
      status: "live",
      detail: "Updated 1 min ago",
    },
    {
      provider_code: "NAGAD-SIM",
      label: "Nagad (simulated)",
      status: "live",
      detail: "Updated 2 min ago",
    },
    {
      provider_code: "ROCKET-SIM",
      label: "Rocket (simulated)",
      status: "delayed",
      detail: "Updated 14 min ago",
    },
  ],
  "SCN-002": [
    {
      provider_code: "BKASH-SIM",
      label: "bKash (simulated)",
      status: "live",
      detail: "40 events in active window",
    },
    {
      provider_code: "NAGAD-SIM",
      label: "Nagad (simulated)",
      status: "live",
      detail: "Baseline available",
    },
    {
      provider_code: "ROCKET-SIM",
      label: "Rocket (simulated)",
      status: "live",
      detail: "No unusual pattern",
    },
  ],
  "SCN-003": [
    {
      provider_code: "BKASH-SIM",
      label: "bKash (simulated)",
      status: "delayed",
      detail: "Feed is 14 min old",
    },
    {
      provider_code: "NAGAD-SIM",
      label: "Nagad (simulated)",
      status: "missing",
      detail: "Balance is unknown, never zero",
    },
    {
      provider_code: "ROCKET-SIM",
      label: "Rocket (simulated)",
      status: "conflicting",
      detail: "Two snapshots disagree",
    },
  ],
  "SCN-004": [
    {
      provider_code: "BKASH-SIM",
      label: "bKash (simulated)",
      status: "live",
      detail: "Case evidence current",
    },
    {
      provider_code: "NAGAD-SIM",
      label: "Nagad (simulated)",
      status: "live",
      detail: "Within provider scope",
    },
    {
      provider_code: "ROCKET-SIM",
      label: "Rocket (simulated)",
      status: "live",
      detail: "Within provider scope",
    },
  ],
  "SCN-005": [
    {
      provider_code: "BKASH-SIM",
      label: "bKash (simulated)",
      status: "live",
      detail: "Expected demand profile",
    },
    {
      provider_code: "NAGAD-SIM",
      label: "Nagad (simulated)",
      status: "live",
      detail: "Expected demand profile",
    },
    {
      provider_code: "ROCKET-SIM",
      label: "Rocket (simulated)",
      status: "live",
      detail: "Expected demand profile",
    },
  ],
};

export const explanationCopy: Record<ExplanationLanguage, string> = {
  en: "bKash (simulated) shows repeated or near-identical cash-out events in a 30 minute window from 4 synthetic references. Confidence is 81%. This requires review and is not proof of wrongdoing.",
  banglish:
    "bKash (simulated) provider e 30 minute window te repeated cash-out pattern dekha geche 4 synthetic ref theke. Confidence 81%. Pattern ta review dorkar; eta wrongdoing-er proof na.",
  bn: "বিকাশ (সিমুলেটেড) প্রোভাইডারে ৩০ মিনিটে ৪টি সিনথেটিক রেফারেন্স থেকে কাছাকাছি অঙ্কের ক্যাশ-আউট দেখা গেছে। আস্থা ৮১%। মানব পর্যালোচনা প্রয়োজন; এটি অনিয়মের প্রমাণ নয়।",
};

export const agentOverview: AgentOverview = {
  agent_id: "SIM-AGENT-0001",
  display_name: "Sylhet Market Outlet",
  area_id: "AREA-SYL-01",
  shared_cash: { amount: "184000.00", currency: "BDT" },
  shared_cash_runway_minutes: 160,
  provider_balances: [
    {
      provider_code: "BKASH-SIM",
      display_name: "bKash (simulated)",
      balance: { amount: "18500.00", currency: "BDT" },
      runway_minutes: 24,
      status: "shortage_risk",
    },
    {
      provider_code: "NAGAD-SIM",
      display_name: "Nagad (simulated)",
      balance: { amount: "121000.00", currency: "BDT" },
      runway_minutes: 220,
      status: "healthy",
    },
    {
      provider_code: "ROCKET-SIM",
      display_name: "Rocket (simulated)",
      balance: { amount: "76000.00", currency: "BDT" },
      runway_minutes: 135,
      status: "watch",
    },
  ],
  deceptive_total: {
    aggregate_balance: { amount: "399500.00", currency: "BDT" },
    appears_healthy: true,
    provider_at_risk: "BKASH-SIM",
  },
  active_alert_count: 3,
  confidence: {
    confidence_id: "CONF-OVERVIEW-001",
    score: 0.72,
    tier: "medium",
    deductions: [
      { reason: "stale provider feed older than 10 minutes", amount: 0.2 },
      { reason: "duplicate records in active window", amount: 0.1 },
    ],
    uncertainty: [
      "bKash feed is 14 minutes old",
      "One duplicate event ignored",
    ],
  },
};

export const alertDetail: AlertDetail = {
  alert_id: "ALERT-0007",
  provider_code: "BKASH-SIM",
  agent_id: "SIM-AGENT-0001",
  severity: "high",
  status: "routed",
  reason:
    "bKash simulated balance runway is short while aggregate value still looks healthy.",
  recommended_next_step:
    "Coordinate approved liquidity support through the responsible provider operations channel.",
  owner_user_id: "USER-OPS-002",
  created_at: "2026-07-11T09:34:00Z",
  confidence: {
    confidence_id: "CONF-ALERT-0007",
    score: 0.81,
    tier: "high",
    deductions: [
      {
        reason: "baseline available but feed is slightly delayed",
        amount: 0.1,
      },
    ],
    uncertainty: ["Short-term demand may change during Eid-eve traffic"],
  },
  uncertainty: ["Feed delay may shift the precise shortage time"],
  evidence_fingerprint: {
    repeated_or_near_identical_amounts: [
      {
        evidence_id: "EVD-001",
        type: "repeated_amount",
        label: "Repeated amount cluster",
        value: "BDT 4,950 to 5,050",
        weight: 0.22,
      },
    ],
    abnormal_velocity: [
      {
        evidence_id: "EVD-002",
        type: "velocity",
        label: "Cash-out velocity",
        value: "3.4x baseline in 30 minutes",
        weight: 0.3,
      },
    ],
    concentrated_synthetic_group: [
      {
        evidence_id: "EVD-003",
        type: "concentrated_group",
        label: "Synthetic reference group",
        value: "4 SIM-CUST refs",
        weight: 0.18,
      },
    ],
    time_window_deviation: [
      {
        evidence_id: "EVD-004",
        type: "time_window_deviation",
        label: "Time-window deviation",
        value: "30 minute rolling window",
        weight: 0.14,
      },
    ],
    baseline_deviation: [
      {
        evidence_id: "EVD-005",
        type: "baseline_deviation",
        label: "Baseline deviation",
        value: "7 day synthetic baseline",
        weight: 0.16,
      },
    ],
  },
  explanation: {
    language: "en",
    generated_by: "deterministic_template",
    text: "bKash (simulated) liquidity pressure is visible for Sylhet Market Outlet. Estimated runway is 24 minutes. This requires review and is not proof of wrongdoing.",
  },
  linked_case_id: "CASE-0004",
  audit_event_ids: ["AUD-1021", "AUD-1022", "AUD-1023"],
};

export const caseDetail: CaseDetail = {
  case_id: "CASE-0004",
  alert_id: "ALERT-0007",
  provider_code: "BKASH-SIM",
  status: "acknowledged",
  severity: "high",
  owner_user_id: "USER-OPS-002",
  version: 3,
  opened_at: "2026-07-11T09:36:00Z",
  resolved_at: null,
  notes: [
    {
      note_id: "NOTE-010",
      author_user_id: "USER-FIELD-001",
      body: "Field officer acknowledged and is coordinating through approved provider operations.",
      created_at: "2026-07-11T09:41:00Z",
    },
  ],
  status_history: [
    {
      from_status: null,
      to_status: "open",
      actor_user_id: "SYSTEM",
      at: "2026-07-11T09:36:00Z",
    },
    {
      from_status: "open",
      to_status: "assigned",
      actor_user_id: "USER-OPS-001",
      at: "2026-07-11T09:38:00Z",
    },
    {
      from_status: "assigned",
      to_status: "acknowledged",
      actor_user_id: "USER-FIELD-001",
      at: "2026-07-11T09:41:00Z",
    },
  ],
  escalations: [
    {
      escalation_id: "ESC-003",
      target_role: "risk_reviewer",
      reason: "Unusual cash-out pattern needs review before closure.",
      created_at: "2026-07-11T09:43:00Z",
    },
  ],
  audit_event_ids: ["AUD-1024", "AUD-1025", "AUD-1026"],
};

export const metricObservations: MetricObservation[] = [
  {
    metric_id: "MET-001",
    run_id: "SIM-RUN-000001",
    name: "Shortage detection lead time",
    value: "42 min",
    target: ">= 30 min",
    passed: true,
    evidence_source: "SCN-001 synthetic ground truth",
    observed_at: "2026-07-11T10:00:00Z",
  },
  {
    metric_id: "MET-003",
    run_id: "SIM-RUN-000001",
    name: "Anomaly precision",
    value: 0.84,
    target: ">= 0.80",
    passed: true,
    evidence_source: "SCN-002 and SCN-005 labels",
    observed_at: "2026-07-11T10:00:00Z",
  },
  {
    metric_id: "MET-008",
    run_id: "SIM-RUN-000001",
    name: "Missing-feed fallback correctness",
    value: "100%",
    target: "100%",
    passed: true,
    evidence_source: "SCN-003 fallback checks",
    observed_at: "2026-07-11T10:00:00Z",
  },
  {
    metric_id: "MET-012",
    run_id: "SIM-RUN-000001",
    name: "SonarQube Quality Gate",
    value: "Pending remote CI",
    target: "Record honestly",
    passed: null,
    evidence_source: "DEC-019 best-effort policy",
    observed_at: "2026-07-11T10:00:00Z",
  },
];
