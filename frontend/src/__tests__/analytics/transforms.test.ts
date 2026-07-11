/**
 * Unit tests for analytics/transforms.ts
 *
 * Tests pure data transformation functions.
 * No React, no mocking of transform functions,
 * only network-boundary types are imported.
 */

import { describe, expect, it } from "vitest";

import type { ForecastSummary } from "@/lib/api";
import type { AgentOverview } from "@/types/demo";

import {
  MIN_CONFIDENCE_TO_RENDER,
  buildPressureBaseline,
  confidenceTier,
  evidenceToPressurePoints,
  forecastsToPriorityRows,
  forecastsToRunwaySeries,
  formatBdt,
  formatRunwayMinutes,
  overviewToPriorityRows,
  overviewToRunwaySeries,
  riskLevelToUrgency,
} from "@/features/analytics/transforms";

// ── Fixtures ──────────────────────────────────────────────────────────────────

const sharedCashForecast: ForecastSummary = {
  forecast_id: "F-001",
  provider_id: null,
  scope: "shared_cash",
  risk_level: "stable",
  runway_minutes: 160,
  confidence: 0.82,
  explanation_en: "Stable",
  explanation_bn: "",
};

const bkashForecast: ForecastSummary = {
  forecast_id: "F-002",
  provider_id: "provider-bk-uuid",
  scope: "provider",
  risk_level: "critical",
  runway_minutes: 24,
  confidence: 0.81,
  explanation_en: "Short runway",
  explanation_bn: "",
};

const nagadForecast: ForecastSummary = {
  forecast_id: "F-003",
  provider_id: "provider-ng-uuid",
  scope: "provider",
  risk_level: "stable",
  runway_minutes: 220,
  confidence: 0.9,
  explanation_en: "Healthy",
  explanation_bn: "",
};

const lowConfidenceForecast: ForecastSummary = {
  forecast_id: "F-004",
  provider_id: "provider-rk-uuid",
  scope: "provider",
  risk_level: "watch",
  runway_minutes: null,
  confidence: 0.25, // below threshold
  explanation_en: "Missing feed",
  explanation_bn: "",
};

const fixtureOverview: AgentOverview = {
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
      runway_minutes: null,
      status: "insufficient_data",
    },
  ],
  deceptive_total: {
    aggregate_balance: { amount: "399500.00", currency: "BDT" },
    appears_healthy: true,
    provider_at_risk: "BKASH-SIM",
  },
  active_alert_count: 3,
  confidence: {
    confidence_id: "CONF-001",
    score: 0.72,
    tier: "medium",
    deductions: [],
    uncertainty: [],
  },
};

// ── formatBdt ────────────────────────────────────────────────────────────────

describe("formatBdt", () => {
  it("formats zero as ৳0", () => {
    expect(formatBdt(0)).toBe("৳0");
  });

  it("formats large values with commas", () => {
    const result = formatBdt(184000);
    expect(result).toContain("৳");
    expect(result).toContain("184");
  });
});

// ── formatRunwayMinutes ───────────────────────────────────────────────────────

describe("formatRunwayMinutes", () => {
  it("returns unknown message for null — never treats null as zero", () => {
    const result = formatRunwayMinutes(null);
    expect(result).toBe("Unknown (data unavailable)");
    expect(result).not.toBe("0");
    expect(result).not.toContain("min");
  });

  it("returns shortage now for zero or negative", () => {
    expect(formatRunwayMinutes(0)).toBe("Shortage now");
    expect(formatRunwayMinutes(-5)).toBe("Shortage now");
  });

  it("returns minutes for < 60 minutes", () => {
    expect(formatRunwayMinutes(24)).toBe("24 min");
  });

  it("returns hours for >= 60 minutes", () => {
    expect(formatRunwayMinutes(120)).toBe("2 hr");
  });

  it("returns hours and minutes for non-round hours", () => {
    expect(formatRunwayMinutes(90)).toBe("1 hr 30 min");
  });
});

// ── confidenceTier ────────────────────────────────────────────────────────────

describe("confidenceTier", () => {
  it("returns high for >= 0.75", () => {
    expect(confidenceTier(0.75)).toBe("high");
    expect(confidenceTier(1.0)).toBe("high");
  });

  it("returns medium for 0.50–0.74", () => {
    expect(confidenceTier(0.50)).toBe("medium");
    expect(confidenceTier(0.74)).toBe("medium");
  });

  it("returns low for < 0.50", () => {
    expect(confidenceTier(0.49)).toBe("low");
    expect(confidenceTier(0.0)).toBe("low");
  });
});

// ── riskLevelToUrgency ────────────────────────────────────────────────────────

describe("riskLevelToUrgency", () => {
  it("critical has lowest urgency score (most urgent)", () => {
    expect(riskLevelToUrgency("critical")).toBeLessThan(
      riskLevelToUrgency("warning"),
    );
  });

  it("stable is less urgent than warning", () => {
    expect(riskLevelToUrgency("stable")).toBeGreaterThan(
      riskLevelToUrgency("warning"),
    );
  });
});

// ── forecastsToRunwaySeries ───────────────────────────────────────────────────

describe("forecastsToRunwaySeries", () => {
  const forecasts = [sharedCashForecast, bkashForecast, nagadForecast, lowConfidenceForecast];
  const series = forecastsToRunwaySeries(forecasts);

  it("T-CHART-001: produces a separate series for each forecast (provider isolation)", () => {
    expect(series).toHaveLength(4);
    const names = series.map((s) => s.providerName);
    // All names must be distinct — no merging of providers
    const uniqueNames = new Set(names);
    expect(uniqueNames.size).toBe(4);
  });

  it("T-CHART-002: shared cash series has isSharedCash=true and providerCode=null", () => {
    const shared = series.find((s) => s.isSharedCash);
    expect(shared).toBeDefined();
    expect(shared!.providerCode).toBeNull();
    expect(shared!.providerName).toBe("Shared physical cash");
    // Must not be merged with any e-money series
    const emoneySeries = series.filter((s) => !s.isSharedCash);
    expect(emoneySeries.length).toBeGreaterThan(0);
    emoneySeries.forEach((s) => expect(s.providerCode).not.toBeNull());
  });

  it("T-CHART-003: missing runway_minutes does not produce zero balances", () => {
    const lowConf = series.find(
      (s) => s.providerCode === "provider-rk-uuid",
    );
    // Low confidence → no points (not zero points)
    lowConf?.points.forEach((p) => {
      expect(p.balanceBdt).not.toBe(0);
    });
  });

  it("T-CHART-005: confidence is tracked per series", () => {
    const bkash = series.find((s) => s.providerCode === "provider-bk-uuid");
    expect(bkash?.confidence).toBeCloseTo(0.81);
  });

  it("marks low-confidence series as insufficient", () => {
    const lowConf = series.find(
      (s) => s.providerCode === "provider-rk-uuid",
    );
    expect(lowConf?.sufficientConfidence).toBe(false);
    expect(lowConf?.confidence).toBeLessThan(MIN_CONFIDENCE_TO_RENDER);
  });

  it("T-CHART-004: runwayMinutes from API is preserved in series", () => {
    const bkash = series.find((s) => s.providerCode === "provider-bk-uuid");
    expect(bkash?.runwayMinutes).toBe(24);
  });
});

// ── overviewToRunwaySeries ────────────────────────────────────────────────────

describe("overviewToRunwaySeries", () => {
  const series = overviewToRunwaySeries(fixtureOverview);

  it("T-CHART-001: each provider has its own isolated series", () => {
    // 1 shared cash + 3 providers = 4 total
    expect(series).toHaveLength(4);
  });

  it("T-CHART-002: first series is shared physical cash, not e-money", () => {
    const shared = series[0];
    expect(shared.isSharedCash).toBe(true);
    expect(shared.providerCode).toBeNull();
    // Shared cash is never flagged as any provider
    const others = series.slice(1);
    others.forEach((s) => {
      expect(s.isSharedCash).toBe(false);
      expect(s.providerCode).not.toBeNull();
    });
  });

  it("T-CHART-003: insufficient_data status produces null runway, not zero", () => {
    const rocket = series.find(
      (s) => s.providerCode === "ROCKET-SIM",
    );
    expect(rocket).toBeDefined();
    expect(rocket!.runwayMinutes).toBeNull();
    expect(rocket!.sufficientConfidence).toBe(false);
  });

  it("does not merge bKash and Nagad e-money into one series", () => {
    const bkash = series.find((s) => s.providerCode === "BKASH-SIM");
    const nagad = series.find((s) => s.providerCode === "NAGAD-SIM");
    expect(bkash).toBeDefined();
    expect(nagad).toBeDefined();
    expect(bkash?.providerName).not.toBe(nagad?.providerName);
  });
});

// ── evidenceToPressurePoints ──────────────────────────────────────────────────

describe("evidenceToPressurePoints", () => {
  it("T-CHART-006: anomaly description uses safe language only", () => {
    const findings = [
      {
        finding_id: "FND-001",
        provider_id: "provider-bk-uuid",
        severity: "high",
        pattern: "near_identical_cash_out_velocity",
        confidence: 0.81,
        explanation_en: "Unusual activity",
        explanation_bn: "",
      },
    ];
    const points = evidenceToPressurePoints(findings, 4);
    const anomalyPoints = points.filter((p) => p.hasAnomaly);
    expect(anomalyPoints.length).toBeGreaterThan(0);

    anomalyPoints.forEach((p) => {
      const desc = p.anomalyDescription ?? "";
      // T-CHART-007: no fraud language
      expect(desc.toLowerCase()).not.toContain("fraud");
      expect(desc.toLowerCase()).not.toContain("criminal");
      // Safe language present
      expect(
        desc.includes("review") ||
          desc.includes("unusual") ||
          desc.includes("higher"),
      ).toBe(true);
    });
  });

  it("T-CHART-007: no fraud detected language in any point", () => {
    const points = evidenceToPressurePoints([], 4);
    points.forEach((p) => {
      const desc = (p.anomalyDescription ?? "").toLowerCase();
      expect(desc).not.toContain("fraud detected");
      expect(desc).not.toContain("fraud probability");
      expect(desc).not.toContain("criminal activity");
    });
  });

  it("returns 7 buckets (0 to 30 minutes in 5-minute steps)", () => {
    const points = evidenceToPressurePoints([], 4);
    expect(points).toHaveLength(7);
  });
});

// ── buildPressureBaseline ─────────────────────────────────────────────────────

describe("buildPressureBaseline", () => {
  it("returns null ratio when baseline is zero", () => {
    const b = buildPressureBaseline(0, 10);
    expect(b.ratioVsNormal).toBeNull();
    expect(b.ratioLabel).toBeNull();
  });

  it("labels high ratio as Higher than normal", () => {
    const b = buildPressureBaseline(4, 12);
    expect(b.ratioLabel).toBe("Higher than normal");
  });

  it("labels normal ratio as Within normal range", () => {
    const b = buildPressureBaseline(4, 4);
    expect(b.ratioLabel).toBe("Within normal range");
  });
});

// ── forecastsToPriorityRows ───────────────────────────────────────────────────

describe("forecastsToPriorityRows", () => {
  const forecasts = [nagadForecast, sharedCashForecast, bkashForecast];
  const rows = forecastsToPriorityRows(forecasts);

  it("T-CHART-014: rows are sorted by urgency — critical first", () => {
    // bKash is critical, should be first
    expect(rows[0]!.riskLevel).toBe("critical");
  });

  it("each provider is a separate row (not aggregated)", () => {
    expect(rows).toHaveLength(3);
    const codes = rows.map((r) => r.providerCode);
    const unique = new Set(codes);
    expect(unique.size).toBe(3);
  });

  it("shared cash row has isSharedCash=true and providerCode=null", () => {
    const shared = rows.find((r) => r.isSharedCash);
    expect(shared).toBeDefined();
    expect(shared!.providerCode).toBeNull();
  });

  it("formatRunwayMinutes for null runway shows unknown message", () => {
    const lowRow = forecastsToPriorityRows([lowConfidenceForecast])[0];
    expect(lowRow!.runwayLabel).toBe("Unknown (data unavailable)");
    expect(lowRow!.runwayLabel).not.toBe("0");
  });
});

// ── overviewToPriorityRows ────────────────────────────────────────────────────

describe("overviewToPriorityRows", () => {
  const rows = overviewToPriorityRows(fixtureOverview);

  it("produces 4 rows (1 shared + 3 providers)", () => {
    expect(rows).toHaveLength(4);
  });

  it("T-CHART-014: most urgent provider is first", () => {
    // bKash shortage_risk → critical
    expect(rows[0]!.riskLevel).toBe("critical");
  });

  it("insufficient_data provider has null runway in the row", () => {
    const rocket = rows.find((r) => r.providerCode === "ROCKET-SIM");
    expect(rocket!.runwayMinutes).toBeNull();
    expect(rocket!.runwayLabel).toBe("Unknown (data unavailable)");
  });
});
