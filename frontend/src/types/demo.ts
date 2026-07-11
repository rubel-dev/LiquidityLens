export type ProviderCode = "BKASH-SIM" | "NAGAD-SIM" | "ROCKET-SIM";
export type Severity = "low" | "medium" | "high";
export type ConfidenceTier = "low" | "medium" | "high";
export type AlertStatus =
  | "new"
  | "routed"
  | "assigned"
  | "acknowledged"
  | "escalated"
  | "resolved"
  | "closed";
export type CaseStatus =
  | "open"
  | "assigned"
  | "acknowledged"
  | "escalated"
  | "risk_review"
  | "resolved"
  | "closed";
export type DemoRole =
  | "agent"
  | "operations"
  | "field_officer"
  | "risk_reviewer"
  | "manager"
  | "demo_operator";
export type ExplanationLanguage = "bn" | "banglish" | "en";
export type DemoScenarioCode =
  | "SCN-001"
  | "SCN-002"
  | "SCN-003"
  | "SCN-004"
  | "SCN-005";

export type MoneyAmount = { amount: string; currency: "BDT" };

export type ConfidenceAssessment = {
  confidence_id: string;
  score: number;
  tier: ConfidenceTier;
  deductions: Array<{ reason: string; amount: number }>;
  uncertainty: string[];
};

export type EvidenceItem = {
  evidence_id: string;
  type:
    | "repeated_amount"
    | "velocity"
    | "concentrated_group"
    | "time_window_deviation"
    | "baseline_deviation"
    | "data_quality";
  label: string;
  value: string | number | boolean;
  weight: number;
};

export type EvidenceFingerprint = {
  repeated_or_near_identical_amounts: EvidenceItem[];
  abnormal_velocity: EvidenceItem[];
  concentrated_synthetic_group: EvidenceItem[];
  time_window_deviation: EvidenceItem[];
  baseline_deviation: EvidenceItem[];
};

export type ProviderBalance = {
  provider_code: ProviderCode;
  display_name: string;
  balance: MoneyAmount;
  runway_minutes: number | null;
  status: "healthy" | "watch" | "shortage_risk" | "insufficient_data";
};

export type AgentOverview = {
  agent_id: string;
  display_name: string;
  area_id: string;
  shared_cash: MoneyAmount;
  shared_cash_runway_minutes: number | null;
  provider_balances: ProviderBalance[];
  deceptive_total: {
    aggregate_balance: MoneyAmount;
    appears_healthy: boolean;
    provider_at_risk: ProviderCode | null;
  };
  active_alert_count: number;
  confidence: ConfidenceAssessment;
};

export type AlertDetail = {
  alert_id: string;
  provider_code: ProviderCode | null;
  agent_id: string | null;
  severity: Severity;
  status: AlertStatus;
  reason: string;
  recommended_next_step: string;
  owner_user_id: string | null;
  created_at: string;
  confidence: ConfidenceAssessment;
  uncertainty: string[];
  evidence_fingerprint: EvidenceFingerprint;
  explanation: {
    language: "bn" | "banglish" | "en";
    text: string;
    generated_by: "llm" | "deterministic_template";
  };
  linked_case_id: string | null;
  audit_event_ids: string[];
};

export type CaseDetail = {
  case_id: string;
  alert_id: string;
  provider_code: ProviderCode | null;
  status: CaseStatus;
  severity: Severity;
  owner_user_id: string | null;
  version: number;
  opened_at: string;
  resolved_at: string | null;
  notes: Array<{
    note_id: string;
    author_user_id: string;
    body: string;
    created_at: string;
  }>;
  status_history: Array<{
    from_status: CaseStatus | null;
    to_status: CaseStatus;
    actor_user_id: string;
    at: string;
  }>;
  escalations: Array<{
    escalation_id: string;
    target_role: string;
    reason: string;
    created_at: string;
  }>;
  audit_event_ids: string[];
};

export type MetricObservation = {
  metric_id: string;
  run_id: string;
  name: string;
  value: number | string;
  target: string;
  passed: boolean | null;
  evidence_source: string;
  observed_at: string;
};

export type DemoScenario = {
  code: DemoScenarioCode;
  title: string;
  summary: string;
  catalog_code: string;
  checkpoint: string;
  tone: "stable" | "warning" | "critical" | "degraded";
};

export type FeedState = {
  provider_code: ProviderCode;
  label: string;
  status: "live" | "delayed" | "missing" | "conflicting";
  detail: string;
};
