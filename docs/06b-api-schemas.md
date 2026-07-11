# API Response Schemas

These schemas are documentation contracts only. They define minimum shared response shapes so backend and frontend work can proceed in parallel.

## Shared Types
```typescript
type ISODateTime = string;
type ProviderCode = "BKASH-SIM" | "NAGAD-SIM" | "ROCKET-SIM";
type Severity = "low" | "medium" | "high";
type ConfidenceTier = "low" | "medium" | "high";
type AlertStatus = "new" | "routed" | "assigned" | "acknowledged" | "escalated" | "resolved" | "closed";
type CaseStatus = "open" | "assigned" | "acknowledged" | "escalated" | "risk_review" | "resolved" | "closed";

interface MoneyAmount {
  amount: string;
  currency: "BDT";
}

interface EvidenceItem {
  evidence_id: string;
  type: "repeated_amount" | "velocity" | "concentrated_group" | "time_window_deviation" | "baseline_deviation" | "data_quality";
  label: string;
  value: string | number | boolean;
  weight: number;
}

interface EvidenceFingerprint {
  repeated_or_near_identical_amounts: EvidenceItem[];
  abnormal_velocity: EvidenceItem[];
  concentrated_synthetic_group: EvidenceItem[];
  time_window_deviation: EvidenceItem[];
  baseline_deviation: EvidenceItem[];
}
```

## AgentOverview
```typescript
interface AgentOverview {
  agent_id: string;
  display_name: string;
  area_id: string;
  shared_cash: MoneyAmount;
  shared_cash_runway_minutes: number | null;
  provider_balances: Array<{
    provider_code: ProviderCode;
    display_name: string;
    balance: MoneyAmount;
    runway_minutes: number | null;
    status: "healthy" | "watch" | "shortage_risk" | "insufficient_data";
  }>;
  deceptive_total: {
    aggregate_balance: MoneyAmount;
    appears_healthy: boolean;
    provider_at_risk: ProviderCode | null;
  };
  active_alert_count: number;
  confidence: ConfidenceAssessment;
}
```

## Alert And AlertDetail
```typescript
interface Alert {
  alert_id: string;
  provider_code: ProviderCode | null;
  agent_id: string | null;
  severity: Severity;
  status: AlertStatus;
  reason: string;
  recommended_next_step: string;
  owner_user_id: string | null;
  created_at: ISODateTime;
  confidence: ConfidenceAssessment;
}

interface AlertDetail extends Alert {
  uncertainty: string[];
  evidence_fingerprint: EvidenceFingerprint;
  explanation: {
    language: "bn" | "banglish" | "en";
    text: string;
    generated_by: "llm" | "deterministic_template";
  };
  linked_case_id: string | null;
  audit_event_ids: string[];
}
```

## Case And CaseDetail
```typescript
interface Case {
  case_id: string;
  alert_id: string;
  provider_code: ProviderCode | null;
  status: CaseStatus;
  severity: Severity;
  owner_user_id: string | null;
  version: number;
  opened_at: ISODateTime;
  resolved_at: ISODateTime | null;
}

interface CaseDetail extends Case {
  notes: Array<{ note_id: string; author_user_id: string; body: string; created_at: ISODateTime }>;
  status_history: Array<{ from_status: CaseStatus | null; to_status: CaseStatus; actor_user_id: string; at: ISODateTime }>;
  escalations: Array<{ escalation_id: string; target_role: string; reason: string; created_at: ISODateTime }>;
  audit_event_ids: string[];
}
```

## LiquidityForecast
```typescript
interface LiquidityForecast {
  forecast_id: string;
  run_id: string;
  provider_code: ProviderCode | null;
  agent_id: string | null;
  subject: "provider_balance" | "shared_cash";
  current_amount: MoneyAmount;
  projected_shortage_at: ISODateTime | null;
  runway_minutes: number | null;
  confidence: ConfidenceAssessment;
  created_at: ISODateTime;
}
```

## AnomalyFinding
```typescript
interface AnomalyFinding {
  finding_id: string;
  run_id: string;
  provider_code: ProviderCode;
  agent_id: string | null;
  rule_version_id: string;
  pattern: "near_identical_cash_out_velocity";
  severity: Severity;
  score: number;
  evidence_fingerprint: EvidenceFingerprint;
  requires_review: boolean;
  created_at: ISODateTime;
}
```

## ConfidenceAssessment
```typescript
interface ConfidenceAssessment {
  confidence_id: string;
  score: number;
  tier: ConfidenceTier;
  deductions: Array<{ reason: string; amount: number }>;
  uncertainty: string[];
}
```

## MetricObservation
```typescript
interface MetricObservation {
  metric_id: string;
  run_id: string;
  name: string;
  value: number | string;
  target: string;
  passed: boolean | null;
  evidence_source: string;
  observed_at: ISODateTime;
}
```

## Error Shape
```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
    request_id: string;
    details?: Record<string, unknown>;
  };
}
```
