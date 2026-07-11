/**
 * Analytics transforms — pure data transformation helpers.
 *
 * This module converts raw API types into chart-ready data structures.
 * It contains NO React, NO side-effects, and NO business logic.
 * Business logic (forecasting, anomaly detection, confidence fusion)
 * lives exclusively in the backend.
 *
 * Provider isolation rules enforced here:
 *   - provider_id === null → "Shared physical cash" (never merged with e-money)
 *   - Missing runway_minutes → null (never treated as zero)
 *   - Confidence < 0.40 → marked as insufficient; charts suppress the line
 *
 * @module analytics/transforms
 */

import type { ForecastSummary, FindingSummary } from "@/lib/api";
import type { AgentOverview, ProviderBalance } from "@/types/demo";

// ── Constants ────────────────────────────────────────────────────────────────

/** Minutes ahead of "now" represented by each synthetic time point. */
const FIXTURE_HORIZON_MINUTES = 180;
/** Step size in minutes for synthetic time series. */
const FIXTURE_STEP_MINUTES = 15;
/** Minimum confidence score to render a chart line. Below this, show "Insufficient data". */
export const MIN_CONFIDENCE_TO_RENDER = 0.40;

// ── Shared types ─────────────────────────────────────────────────────────────

/**
 * A single point on the Liquidity Runway Chart.
 * `balanceBdt` is null when the balance is unknown — never treat as zero.
 */
export type RunwayPoint = {
  /** ISO timestamp for X-axis */
  timestampIso: string;
  /** Minutes from "now" for axis labels */
  minutesFromNow: number;
  /** Balance in BDT, or null when unknown */
  balanceBdt: number | null;
};

/**
 * A single provider series for the Liquidity Runway Chart.
 * Each series maps to exactly one provider or to shared physical cash.
 */
export type RunwaySeries = {
  /** Human-readable provider name, e.g. "bKash (simulated)" */
  providerName: string;
  /** Original provider code, e.g. "BKASH-SIM". Null for shared physical cash. */
  providerCode: string | null;
  /** True when provider_id is null — shared cash, never e-money */
  isSharedCash: boolean;
  /** Confidence score 0–1; affects visual treatment */
  confidence: number;
  /** Whether confidence is high enough to render the forecast line */
  sufficientConfidence: boolean;
  /** Estimated shortage time in minutes from now, or null */
  runwayMinutes: number | null;
  /** Risk level from the backend */
  riskLevel: string;
  /** Data points for this line */
  points: RunwayPoint[];
};

/**
 * A single bar in the Transaction Pressure Chart.
 */
export type PressurePoint = {
  /** Label for the X-axis bucket */
  label: string;
  /** Minutes from "now" (negative = past, 0 = current) */
  minutesFromNow: number;
  /** Transaction count in this bucket */
  count: number;
  /** BDT amount in this bucket, or null if unknown */
  amountBdt: number | null;
  /** Whether this bucket contains anomalous evidence */
  hasAnomaly: boolean;
  /** Safe description of anomalous activity, or null */
  anomalyDescription: string | null;
};

/**
 * Baseline vs. actual summary for the pressure chart header.
 */
export type PressureBaseline = {
  /** Normal baseline count per interval */
  normalCount: number;
  /** Current observed count */
  currentCount: number;
  /** Ratio current/normal, or null if baseline unavailable */
  ratioVsNormal: number | null;
  /** Safe label for the ratio, e.g. "Higher than normal" */
  ratioLabel: string | null;
};

/**
 * A row in the Operational Priority Table.
 */
export type PriorityRow = {
  /** Provider name */
  providerName: string;
  /** Provider code or null for shared cash */
  providerCode: string | null;
  /** Whether this is shared physical cash */
  isSharedCash: boolean;
  /** Risk level: "critical" | "warning" | "watch" | "stable" | "healthy" */
  riskLevel: string;
  /** Estimated runway in minutes, or null */
  runwayMinutes: number | null;
  /** Formatted runway string for display */
  runwayLabel: string;
  /** Confidence score 0–1 */
  confidence: number;
  /** Confidence tier: "high" | "medium" | "low" */
  confidenceTier: "high" | "medium" | "low";
  /** Alert status if an alert is linked, e.g. "open" */
  alertStatus: string | null;
  /** Case status if a case is linked, e.g. "assigned" */
  caseStatus: string | null;
  /** Recommended next step (safe advisory language only) */
  recommendedNextStep: string;
  /** Sort key: lower = more urgent */
  urgencyScore: number;
};

// ── Helper utilities ─────────────────────────────────────────────────────────

/** Format a BDT amount as ৳1,23,456 (Bangladeshi format). */
export function formatBdt(amount: number): string {
  return `৳${amount.toLocaleString("en-BD", { maximumFractionDigits: 0 })}`;
}

/** Format a runway in minutes as a human-readable string. */
export function formatRunwayMinutes(minutes: number | null): string {
  if (minutes === null) return "Unknown (data unavailable)";
  if (minutes <= 0) return "Shortage now";
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const hours = Math.floor(minutes / 60);
  const remainder = Math.round(minutes % 60);
  return remainder === 0 ? `${hours} hr` : `${hours} hr ${remainder} min`;
}

/** Map a confidence score to a display tier. */
export function confidenceTier(score: number): "high" | "medium" | "low" {
  if (score >= 0.75) return "high";
  if (score >= 0.50) return "medium";
  return "low";
}

/**
 * Convert a risk level string to a numeric urgency score.
 * Lower number = more urgent.
 */
export function riskLevelToUrgency(riskLevel: string): number {
  const map: Record<string, number> = {
    critical: 0,
    warning: 1,
    watch: 2,
    stable: 3,
    healthy: 4,
  };
  return map[riskLevel.toLowerCase()] ?? 5;
}

// ── Runway Chart transforms ──────────────────────────────────────────────────

/**
 * Build synthetic runway points for a provider balance that has no live
 * time-series from the backend. Uses the current balance and runway_minutes
 * to construct a linear decay curve.
 *
 * Returns an empty array when balance or runway is unavailable.
 */
function buildSyntheticPoints(
  balanceAmount: string | null,
  runwayMinutes: number | null,
): RunwayPoint[] {
  if (balanceAmount === null || runwayMinutes === null) return [];

  const balance = parseFloat(balanceAmount);
  if (isNaN(balance) || balance < 0) return [];

  const now = Date.now();
  const points: RunwayPoint[] = [];

  for (
    let t = 0;
    t <= FIXTURE_HORIZON_MINUTES;
    t += FIXTURE_STEP_MINUTES
  ) {
    const fraction = runwayMinutes > 0 ? 1 - t / runwayMinutes : 0;
    const projected = Math.max(0, balance * fraction);
    points.push({
      timestampIso: new Date(now + t * 60_000).toISOString(),
      minutesFromNow: t,
      balanceBdt: projected,
    });
  }

  return points;
}

/**
 * Convert a `ForecastSummary[]` from the analysis API into `RunwaySeries[]`
 * for the Liquidity Runway Chart.
 *
 * Provider isolation guarantee: each series maps to exactly one provider.
 * `provider_id === null` is always "Shared physical cash".
 * Lines with confidence < MIN_CONFIDENCE_TO_RENDER are flagged as insufficient.
 */
export function forecastsToRunwaySeries(
  forecasts: ForecastSummary[],
): RunwaySeries[] {
  return forecasts.map((f) => {
    const providerName =
      f.scope === "shared_cash"
        ? "Shared physical cash"
        : ((f as ForecastSummary & { provider_name?: string }).provider_name ??
          `Provider ${f.provider_id ?? f.scope}`);

    const points = buildSyntheticPoints(null, f.runway_minutes);

    return {
      providerName,
      providerCode: f.provider_id,
      isSharedCash: f.provider_id === null,
      confidence: f.confidence,
      sufficientConfidence: f.confidence >= MIN_CONFIDENCE_TO_RENDER,
      runwayMinutes: f.runway_minutes,
      riskLevel: f.risk_level,
      points,
    };
  });
}

/**
 * Convert fixture `AgentOverview` data into `RunwaySeries[]` when no live
 * analysis is available.
 *
 * Provider isolation guarantee: shared cash is always its own series with
 * `isSharedCash = true` and never merged with any e-money provider.
 */
export function overviewToRunwaySeries(overview: AgentOverview): RunwaySeries[] {
  const series: RunwaySeries[] = [];

  // Shared physical cash — always provider-independent
  series.push({
    providerName: "Shared physical cash",
    providerCode: null,
    isSharedCash: true,
    confidence: overview.confidence.score,
    sufficientConfidence: overview.confidence.score >= MIN_CONFIDENCE_TO_RENDER,
    runwayMinutes: overview.shared_cash_runway_minutes,
    riskLevel:
      (overview.shared_cash_runway_minutes ?? 999) < 60
        ? "warning"
        : "stable",
    points: buildSyntheticPoints(
      overview.shared_cash.amount,
      overview.shared_cash_runway_minutes,
    ),
  });

  // Provider e-money — each is a separate, isolated series
  for (const pb of overview.provider_balances) {
    const confidence = overview.confidence.score;
    series.push({
      providerName: pb.display_name,
      providerCode: pb.provider_code,
      isSharedCash: false,
      confidence,
      sufficientConfidence:
        pb.status !== "insufficient_data" &&
        confidence >= MIN_CONFIDENCE_TO_RENDER,
      runwayMinutes:
        pb.status === "insufficient_data" ? null : pb.runway_minutes,
      riskLevel:
        pb.status === "shortage_risk"
          ? "critical"
          : pb.status === "watch"
            ? "warning"
            : pb.status === "insufficient_data"
              ? "unknown"
              : "stable",
      points:
        pb.status === "insufficient_data"
          ? []
          : buildSyntheticPoints(
              pb.balance.amount,
              pb.runway_minutes,
            ),
    });
  }

  return series;
}

// ── Pressure Chart transforms ────────────────────────────────────────────────

/** Safe anomaly descriptions. Never mentions fraud. */
const SAFE_ANOMALY_LABELS: Record<string, string> = {
  near_identical_cash_out_velocity:
    "Unusual activity — requires review. May have a legitimate explanation.",
  high_velocity: "Higher than normal transaction rate — requires review.",
  repeated_amount: "Repeated amounts detected — requires human review.",
  concentrated_group: "Concentrated account activity — requires review.",
  baseline_deviation: "Higher than normal — requires review.",
};

function safeAnomaly(evidenceType: string): string {
  return (
    SAFE_ANOMALY_LABELS[evidenceType] ??
    "Unusual activity — requires review. May have a legitimate explanation."
  );
}

/**
 * Convert alert evidence from the API into pressure chart points.
 * Uses the current 30-minute window divided into 5-minute buckets.
 *
 * Anomaly evidence is mapped to the most recent bucket as that is where
 * patterns were detected.
 */
export function evidenceToPressurePoints(
  findings: FindingSummary[],
  baselineCount: number,
): PressurePoint[] {
  const buckets: PressurePoint[] = [];
  const bucketCount = 6; // 30-minute window, 5-minute buckets

  for (let i = bucketCount; i >= 0; i--) {
    const minutesFromNow = -(i * 5);
    const label = i === 0 ? "Now" : `-${i * 5}m`;

    // Apply variance to baseline counts for realistic fixture shape
    const variance = 1 + (Math.sin(i * 1.2) * 0.3);
    const count = Math.round(baselineCount * variance);

    buckets.push({
      label,
      minutesFromNow,
      count,
      amountBdt: null,
      hasAnomaly: false,
      anomalyDescription: null,
    });
  }

  // Mark the most recent buckets that overlap with detected anomalies
  if (findings.length > 0) {
    const anomalyBucket = buckets[buckets.length - 1];
    if (anomalyBucket) {
      anomalyBucket.hasAnomaly = true;
      anomalyBucket.anomalyDescription = safeAnomaly(
        findings[0]?.pattern ?? "unusual_activity",
      );
      // Spike the count to show the anomalous pressure
      anomalyBucket.count = Math.round(baselineCount * 3.4);
    }
    const prevBucket = buckets[buckets.length - 2];
    if (prevBucket) {
      prevBucket.hasAnomaly = true;
      prevBucket.count = Math.round(baselineCount * 2.1);
      prevBucket.anomalyDescription = anomalyBucket?.anomalyDescription ?? null;
    }
  }

  return buckets;
}

/**
 * Produce pressure baseline summary from overview or live findings.
 */
export function buildPressureBaseline(
  baselineCount: number,
  currentCount: number,
): PressureBaseline {
  if (baselineCount <= 0) {
    return {
      normalCount: 0,
      currentCount,
      ratioVsNormal: null,
      ratioLabel: null,
    };
  }

  const ratio = currentCount / baselineCount;

  let label: string | null = null;
  if (ratio > 2.0) label = "Higher than normal";
  else if (ratio > 1.3) label = "Slightly elevated";
  else if (ratio < 0.5) label = "Lower than normal";
  else label = "Within normal range";

  return {
    normalCount: baselineCount,
    currentCount,
    ratioVsNormal: ratio,
    ratioLabel: label,
  };
}

// ── Priority Table transforms ────────────────────────────────────────────────

const DEFAULT_NEXT_STEP =
  "Coordinate approved liquidity support through the responsible provider operations channel.";

/**
 * Build `PriorityRow[]` from live forecast summaries, sorted by urgency.
 * Rows with lower runway (or higher risk) appear first.
 *
 * Provider isolation: shared cash and each provider appear as distinct rows.
 */
export function forecastsToPriorityRows(
  forecasts: ForecastSummary[],
): PriorityRow[] {
  const rows: PriorityRow[] = forecasts.map((f) => {
    const providerName =
      f.scope === "shared_cash"
        ? "Shared physical cash"
        : ((f as ForecastSummary & { provider_name?: string }).provider_name ??
          `Provider ${f.provider_id ?? f.scope}`);

    const conf = f.confidence;

    return {
      providerName,
      providerCode: f.provider_id,
      isSharedCash: f.provider_id === null,
      riskLevel: f.risk_level,
      runwayMinutes: f.runway_minutes,
      runwayLabel: formatRunwayMinutes(f.runway_minutes),
      confidence: conf,
      confidenceTier: confidenceTier(conf),
      alertStatus: null,
      caseStatus: null,
      recommendedNextStep: DEFAULT_NEXT_STEP,
      urgencyScore:
        riskLevelToUrgency(f.risk_level) * 1000 +
        (f.runway_minutes ?? 9999),
    };
  });

  return rows.sort((a, b) => a.urgencyScore - b.urgencyScore);
}

/**
 * Build `PriorityRow[]` from fixture `AgentOverview` when no live data
 * is available. Each provider remains its own isolated row.
 */
export function overviewToPriorityRows(
  overview: AgentOverview,
): PriorityRow[] {
  const conf = overview.confidence.score;
  const rows: PriorityRow[] = [];

  // Shared physical cash row
  rows.push({
    providerName: "Shared physical cash",
    providerCode: null,
    isSharedCash: true,
    riskLevel:
      (overview.shared_cash_runway_minutes ?? 999) < 60 ? "warning" : "stable",
    runwayMinutes: overview.shared_cash_runway_minutes,
    runwayLabel: formatRunwayMinutes(overview.shared_cash_runway_minutes),
    confidence: conf,
    confidenceTier: confidenceTier(conf),
    alertStatus: null,
    caseStatus: null,
    recommendedNextStep: DEFAULT_NEXT_STEP,
    urgencyScore:
      riskLevelToUrgency(
        (overview.shared_cash_runway_minutes ?? 999) < 60 ? "warning" : "stable",
      ) *
        1000 +
      (overview.shared_cash_runway_minutes ?? 9999),
  });

  // One row per provider (isolated)
  for (const pb of overview.provider_balances) {
    const rl =
      pb.status === "shortage_risk"
        ? "critical"
        : pb.status === "watch"
          ? "warning"
          : pb.status === "insufficient_data"
            ? "unknown"
            : "stable";

    rows.push({
      providerName: pb.display_name,
      providerCode: pb.provider_code,
      isSharedCash: false,
      riskLevel: rl,
      runwayMinutes:
        pb.status === "insufficient_data" ? null : pb.runway_minutes,
      runwayLabel: formatRunwayMinutes(
        pb.status === "insufficient_data" ? null : pb.runway_minutes,
      ),
      confidence: conf,
      confidenceTier: confidenceTier(conf),
      alertStatus: pb.status === "shortage_risk" ? "open" : null,
      caseStatus: pb.status === "shortage_risk" ? "open" : null,
      recommendedNextStep: DEFAULT_NEXT_STEP,
      urgencyScore:
        riskLevelToUrgency(rl) * 1000 + (pb.runway_minutes ?? 9999),
    });
  }

  return rows.sort((a, b) => a.urgencyScore - b.urgencyScore);
}
