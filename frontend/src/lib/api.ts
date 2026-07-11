import type { HealthResponse } from "@/types/health";
import type {
  AlertStatus,
  CaseStatus,
} from "@/types/demo";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

// Demo user IDs — these exist as seeded users in the reference data.
// In a real system these would come from an identity provider.
export const DEMO_USERS: Record<string, string> = {
  ops: "00000000-0000-0000-0000-000000000001",
  field: "00000000-0000-0000-0000-000000000002",
  risk: "00000000-0000-0000-0000-000000000003",
  manager: "00000000-0000-0000-0000-000000000004",
  demo: "00000000-0000-0000-0000-000000000005",
  agent: "00000000-0000-0000-0000-000000000006",
};

export type DemoUserRole = keyof typeof DEMO_USERS;

function headers(userId?: string): HeadersInit {
  const base: Record<string, string> = { "Content-Type": "application/json" };
  if (userId) base["X-User-ID"] = userId;
  return base;
}

async function apiFetch<T>(
  path: string,
  opts: RequestInit & { userId?: string } = {},
): Promise<T> {
  const { userId, ...fetchOpts } = opts;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOpts,
    headers: { ...headers(userId), ...(fetchOpts.headers ?? {}) },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(`API ${response.status}: ${body || response.statusText}`);
  }

  return response.json() as Promise<T>;
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function getApiHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

// ── Session ───────────────────────────────────────────────────────────────────

export type SessionInfo = {
  user_id: string;
  display_name: string;
  roles: string[];
  provider_ids: string[];
  area_ids: string[];
  global_access: boolean;
};

export async function getSession(userId: string): Promise<SessionInfo> {
  return apiFetch<SessionInfo>("/session", { userId });
}

// ── Analysis Pipeline ─────────────────────────────────────────────────────────

export type ForecastSummary = {
  forecast_id: string;
  provider_id: string | null;
  scope: string;
  risk_level: string;
  runway_minutes: number | null;
  confidence: number;
  explanation_en: string;
  explanation_bn: string;
};

export type FindingSummary = {
  finding_id: string;
  provider_id: string;
  severity: string;
  pattern: string;
  confidence: number;
  explanation_en: string;
  explanation_bn: string;
};

export type AnalysisResult = {
  run_ref: string;
  agent_id: string;
  forecasts_created: number;
  findings_created: number;
  alerts_created: number;
  forecasts: ForecastSummary[];
  findings: FindingSummary[];
  alert_ids: string[];
};

export async function analyzeRun(
  runRef: string,
  userId: string,
): Promise<AnalysisResult> {
  return apiFetch<AnalysisResult>(`/analyze/${runRef}`, {
    method: "POST",
    userId,
  });
}

// ── Scenarios ─────────────────────────────────────────────────────────────────

export type ScenarioSummary = {
  scenario_id: string;
  code: string;
  name: string;
  description: string;
};

export type ScenarioRunResult = {
  run_ref: string;
  scenario_code: string;
  status: string;
  seed: string;
  fingerprint: string;
  generated_counts: Record<string, number>;
};

export async function listScenarios(userId: string): Promise<ScenarioSummary[]> {
  return apiFetch<ScenarioSummary[]>("/scenarios", { userId });
}

export async function runScenario(
  scenarioCode: string,
  seed: number,
  userId: string,
): Promise<ScenarioRunResult> {
  return apiFetch<ScenarioRunResult>(`/scenarios/${scenarioCode}/run`, {
    method: "POST",
    userId,
    body: JSON.stringify({ seed, profile: "demo" }),
  });
}

export async function resetScenarioRun(
  runId: string,
  userId: string,
): Promise<ScenarioRunResult> {
  return apiFetch<ScenarioRunResult>(`/scenario-runs/${runId}/reset`, {
    method: "POST",
    userId,
  });
}

export async function replayScenarioRun(
  runId: string,
  userId: string,
): Promise<ScenarioRunResult> {
  return apiFetch<ScenarioRunResult>(`/scenario-runs/${runId}/replay`, {
    method: "POST",
    userId,
  });
}

// ── Alerts ────────────────────────────────────────────────────────────────────

export type AlertEvidence = {
  evidence_type: string;
  payload: Record<string, unknown>;
};

export type AlertAudit = {
  action: string;
  actor_user_id: string | null;
  previous_state: Record<string, unknown> | null;
  new_state: Record<string, unknown> | null;
  created_at: string;
};

export type ApiAlert = {
  alert_id: string;
  alert_type: string;
  severity: string;
  provider_id: string | null;
  agent_id: string;
  evidence: AlertEvidence[];
  confidence: string;
  recommended_next_step: string;
  owner_user_id: string | null;
  status: AlertStatus;
  summary: string;
  human_review_required: boolean;
  created_at: string;
  audit_trail: AlertAudit[];
};

export async function listAlerts(
  userId: string,
  params?: { provider_id?: string; status?: AlertStatus; severity?: string },
): Promise<ApiAlert[]> {
  const query = new URLSearchParams();
  if (params?.provider_id) query.set("provider_id", params.provider_id);
  if (params?.status) query.set("status", params.status);
  if (params?.severity) query.set("severity", params.severity);
  const qs = query.toString() ? `?${query}` : "";
  return apiFetch<ApiAlert[]>(`/alerts${qs}`, { userId });
}

export async function getAlert(alertId: string, userId: string): Promise<ApiAlert> {
  return apiFetch<ApiAlert>(`/alerts/${alertId}`, { userId });
}

export async function assignAlert(
  alertId: string,
  assigneeUserId: string,
  userId: string,
): Promise<ApiAlert> {
  return apiFetch<ApiAlert>(`/alerts/${alertId}/assign`, {
    method: "POST",
    userId,
    body: JSON.stringify({ assignee_user_id: assigneeUserId }),
  });
}

export async function acknowledgeAlert(
  alertId: string,
  userId: string,
  note?: string,
): Promise<ApiAlert> {
  return apiFetch<ApiAlert>(`/alerts/${alertId}/acknowledge`, {
    method: "POST",
    userId,
    body: JSON.stringify({ note: note ?? null }),
  });
}

// ── Cases ─────────────────────────────────────────────────────────────────────

export type CaseNote = {
  note_id: string;
  author_user_id: string;
  body: string;
  created_at: string;
};

export type CaseHistoryEntry = {
  from_status: CaseStatus | null;
  to_status: CaseStatus;
  actor_user_id: string;
  reason: string | null;
  created_at: string;
};

export type CaseEscalation = {
  escalation_id: string;
  from_role: string;
  to_role: string;
  reason: string;
  created_at: string;
};

export type ApiCase = {
  case_id: string;
  origin_alert_id: string | null;
  provider_id: string | null;
  agent_id: string;
  owner_user_id: string | null;
  status: CaseStatus;
  title: string;
  version: number;
  created_at: string;
  updated_at: string;
  notes: CaseNote[];
  status_history: CaseHistoryEntry[];
  escalation_history: CaseEscalation[];
  resolution_information: string | null;
  audit_event_ids: string[];
};

export async function listCases(
  userId: string,
  params?: { provider_id?: string; status?: CaseStatus },
): Promise<ApiCase[]> {
  const query = new URLSearchParams();
  if (params?.provider_id) query.set("provider_id", params.provider_id);
  if (params?.status) query.set("status", params.status);
  const qs = query.toString() ? `?${query}` : "";
  return apiFetch<ApiCase[]>(`/cases${qs}`, { userId });
}

export async function getCase(caseId: string, userId: string): Promise<ApiCase> {
  return apiFetch<ApiCase>(`/cases/${caseId}`, { userId });
}

export async function createCase(
  alertId: string,
  userId: string,
  title?: string,
): Promise<ApiCase> {
  return apiFetch<ApiCase>(`/cases`, {
    method: "POST",
    userId,
    body: JSON.stringify({ alert_id: alertId, title: title ?? null }),
  });
}

export async function addCaseNote(
  caseId: string,
  body: string,
  userId: string,
): Promise<CaseNote> {
  return apiFetch<CaseNote>(`/cases/${caseId}/notes`, {
    method: "POST",
    userId,
    body: JSON.stringify({ body }),
  });
}

export async function escalateCase(
  caseId: string,
  toRole: string,
  reason: string,
  userId: string,
  expectedVersion?: number,
): Promise<ApiCase> {
  return apiFetch<ApiCase>(`/cases/${caseId}/escalate`, {
    method: "POST",
    userId,
    body: JSON.stringify({
      to_role: toRole,
      reason,
      expected_version: expectedVersion ?? null,
    }),
  });
}

export async function resolveCase(
  caseId: string,
  rationale: string,
  userId: string,
  expectedVersion?: number,
): Promise<ApiCase> {
  return apiFetch<ApiCase>(`/cases/${caseId}/resolve`, {
    method: "POST",
    userId,
    body: JSON.stringify({
      rationale,
      expected_version: expectedVersion ?? null,
    }),
  });
}

// ── Liquidity Forecasts ───────────────────────────────────────────────────────

export type LiquidityForecast = {
  forecast_id: string;
  agent_id: string;
  provider_id: string | null;
  forecast_type: string;
  forecast_time: string;
  shortage_at: string | null;
  confidence: string;
  created_at: string;
};

export async function listForecasts(
  userId: string,
  params?: { provider_id?: string; agent_id?: string },
): Promise<LiquidityForecast[]> {
  const query = new URLSearchParams();
  if (params?.provider_id) query.set("provider_id", params.provider_id);
  if (params?.agent_id) query.set("agent_id", params.agent_id);
  const qs = query.toString() ? `?${query}` : "";
  return apiFetch<LiquidityForecast[]>(`/liquidity-forecasts${qs}`, { userId });
}

// ── Anomaly Findings ──────────────────────────────────────────────────────────

export type AnomalyFinding = {
  finding_id: string;
  provider_id: string;
  agent_id: string;
  finding_type: string;
  severity: string;
  score: string;
  detected_at: string;
  human_review_required: boolean;
  created_at: string;
};

export async function listFindings(
  userId: string,
  params?: { provider_id?: string; agent_id?: string },
): Promise<AnomalyFinding[]> {
  const query = new URLSearchParams();
  if (params?.provider_id) query.set("provider_id", params.provider_id);
  if (params?.agent_id) query.set("agent_id", params.agent_id);
  const qs = query.toString() ? `?${query}` : "";
  return apiFetch<AnomalyFinding[]>(`/anomaly-findings${qs}`, { userId });
}

// ── Audit Events ──────────────────────────────────────────────────────────────

export type AuditEventApi = {
  event_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  actor_user_id: string | null;
  provider_id: string | null;
  previous_state: Record<string, unknown> | null;
  new_state: Record<string, unknown> | null;
  created_at: string;
};

export async function listAuditEvents(
  userId: string,
  params?: { entity_type?: string; entity_id?: string; provider_id?: string },
): Promise<AuditEventApi[]> {
  const query = new URLSearchParams();
  if (params?.entity_type) query.set("entity_type", params.entity_type);
  if (params?.entity_id) query.set("entity_id", params.entity_id);
  if (params?.provider_id) query.set("provider_id", params.provider_id);
  const qs = query.toString() ? `?${query}` : "";
  return apiFetch<AuditEventApi[]>(`/audit-events${qs}`, { userId });
}
