const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json();
}

async function patch<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`PATCH ${path} → ${res.status}`);
  return res.json();
}

export const api = {
  agents: {
    list: () => get<Agent[]>("/api/agents"),
    get: (id: string) => get<Agent>(`/api/agents/${id}`),
  },
  analytics: {
    liquidity: (agentId: string) => get<LiquidityData>(`/api/analytics/liquidity/${agentId}`),
    anomaly: (agentId: string, provider: string) =>
      get<AnomalyData>(`/api/analytics/anomaly/${agentId}/${provider}`),
    whatif: (body: WhatIfBody) => post<WhatIfResult>("/api/analytics/whatif", body),
  },
  alerts: {
    list: (params?: { status?: string; provider?: string; severity?: string }) => {
      const q = new URLSearchParams(params as Record<string, string>).toString();
      return get<Alert[]>(`/api/alerts${q ? "?" + q : ""}`);
    },
    get: (id: string) => get<Alert>(`/api/alerts/${id}`),
    acknowledge: (id: string, note: string, author?: string) =>
      post(`/api/alerts/${id}/acknowledge`, { note, author }),
    escalate: (id: string, note: string, author?: string) =>
      post(`/api/alerts/${id}/escalate`, { note, author }),
    resolve: (id: string, note: string, author?: string) =>
      post(`/api/alerts/${id}/resolve`, { note, author }),
    falsePositive: (id: string, note: string, author?: string) =>
      post(`/api/alerts/${id}/false-positive`, { note, author }),
  },
  cases: {
    list: () => get<Case[]>("/api/cases"),
    get: (id: string) => get<Case>(`/api/cases/${id}`),
    addNote: (id: string, text: string, author: string) =>
      post(`/api/cases/${id}/notes`, { text, author }),
    assign: (id: string, body: { assigned_to: string; assigned_role: string; note?: string }) =>
      patch(`/api/cases/${id}/assign`, body),
  },
  simulate: {
    eidRush: (agentName?: string) =>
      post("/api/simulate/scenario/eid_rush", undefined),
    salaryDay: () => post("/api/simulate/scenario/salary_day", undefined),
  },
};

// ── Types ──────────────────────────────────────────────────────────────────

export interface Agent {
  id: string;
  name: string;
  area: string;
  physical_cash: number;
  total_emoney: number;
  total_balance: number;
  open_alerts: number;
  status: string;
  providers: Record<string, { balance: number | null; data_quality: string }>;
}

export interface LiquidityProvider {
  provider: string;
  balance: number | null;
  rate_per_minute: number;
  eta_minutes: number | null;
  confidence: number;
  uncertainty: string;
  data_quality: string;
  recommended_topup: number | null;
}

export interface LiquidityData {
  agent_id: string;
  physical_cash: number;
  providers: LiquidityProvider[];
  aggregate_emoney: number;
}

export interface AnomalyData {
  agent_id: string;
  provider: string;
  flagged: boolean;
  confidence: number;
  detectors: {
    velocity: { flagged: boolean; count: number; threshold: number; note: string };
    clustering: { flagged: boolean; cluster_ratio: number; dominant_range: string; clustered_amounts: number[] };
    concentration: { flagged: boolean; unique_accounts: number; total_transactions: number; concentration_ratio: number; top_accounts: { account_id: string; count: number; total_amount: number }[] };
  };
}

export interface Alert {
  id: string;
  agent_id: string;
  provider: string | null;
  type: string;
  severity: string;
  message_en: string | null;
  message_bn: string | null;
  evidence: Record<string, unknown> | null;
  confidence: number | null;
  uncertainty: string | null;
  eta_minutes: number | null;
  owner_role: string | null;
  owner_name: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Case {
  id: string;
  alert_id: string;
  assigned_to: string | null;
  assigned_role: string | null;
  acknowledged_at: string | null;
  escalated_at: string | null;
  resolved_at: string | null;
  resolution_note: string | null;
  false_positive: boolean;
  notes: { author: string; text: string; timestamp: string }[];
  created_at: string;
}

export interface WhatIfBody { agent_id: string; provider: string; demand_multiplier: number }
export interface WhatIfResult {
  provider: string;
  demand_multiplier: number;
  original_eta_minutes: number | null;
  new_eta_minutes: number;
  original_rate_per_minute: number;
  new_rate_per_minute: number;
  advisory: string;
}
