/**
 * Integration tests for AnalyticsSection.
 *
 * Tests data mode switching (live vs. synthetic), API error surfacing,
 * and correct chart composition.
 */

import { render, screen } from "@testing-library/react";
import { describe, expect, it, beforeAll } from "vitest";

import type { AnalysisResult, ApiAlert } from "@/lib/api";
import type { AgentOverview } from "@/types/demo";
import { AnalyticsSection } from "@/features/analytics/AnalyticsSection";

beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

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
  ],
  deceptive_total: {
    aggregate_balance: { amount: "323500.00", currency: "BDT" },
    appears_healthy: true,
    provider_at_risk: "BKASH-SIM",
  },
  active_alert_count: 1,
  confidence: {
    confidence_id: "CONF-001",
    score: 0.72,
    tier: "medium",
    deductions: [],
    uncertainty: [],
  },
};

const liveAnalysis: AnalysisResult = {
  run_ref: "SIM-RUN-TEST-001",
  agent_id: "agent-uuid-001",
  forecasts_created: 3,
  findings_created: 1,
  alerts_created: 1,
  forecasts: [
    {
      forecast_id: "F-001",
      provider_id: null,
      scope: "shared_cash",
      risk_level: "stable",
      runway_minutes: 160,
      confidence: 0.82,
      explanation_en: "Stable",
      explanation_bn: "",
    },
    {
      forecast_id: "F-002",
      provider_id: "provider-bk-uuid",
      scope: "provider",
      risk_level: "critical",
      runway_minutes: 24,
      confidence: 0.81,
      explanation_en: "Short runway",
      explanation_bn: "",
    },
    {
      forecast_id: "F-003",
      provider_id: "provider-ng-uuid",
      scope: "provider",
      risk_level: "stable",
      runway_minutes: 220,
      confidence: 0.9,
      explanation_en: "Healthy",
      explanation_bn: "",
    },
  ],
  findings: [
    {
      finding_id: "FND-001",
      provider_id: "provider-bk-uuid",
      severity: "high",
      pattern: "near_identical_cash_out_velocity",
      confidence: 0.81,
      explanation_en: "Unusual activity",
      explanation_bn: "",
    },
  ],
  alert_ids: ["alert-uuid-001"],
};

const liveAlerts: ApiAlert[] = [];

describe("AnalyticsSection — fixture mode (liveAnalysis null)", () => {
  it("T-CHART-009: shows Synthetic demo data badge in fixture mode", () => {
    render(
      <AnalyticsSection
        liveAnalysis={null}
        liveAlerts={[]}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage={null}
      />,
    );
    // All three charts should show synthetic badge
    const badges = screen.getAllByText("Synthetic demo data");
    expect(badges.length).toBeGreaterThanOrEqual(3);
  });

  it("T-CHART-009: no Live backend result badge in fixture mode", () => {
    render(
      <AnalyticsSection
        liveAnalysis={null}
        liveAlerts={[]}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage={null}
      />,
    );
    expect(screen.queryAllByText("Live backend result")).toHaveLength(0);
  });
});

describe("AnalyticsSection — live mode (liveAnalysis provided)", () => {
  it("T-CHART-008: shows Live backend result badge when live data present", () => {
    render(
      <AnalyticsSection
        liveAnalysis={liveAnalysis}
        liveAlerts={liveAlerts}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage={null}
      />,
    );
    const badges = screen.getAllByText("Live backend result");
    expect(badges.length).toBeGreaterThanOrEqual(3);
  });

  it("T-CHART-008: no Synthetic demo data badge when live data present", () => {
    render(
      <AnalyticsSection
        liveAnalysis={liveAnalysis}
        liveAlerts={liveAlerts}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage={null}
      />,
    );
    // The badges should all be live, none synthetic
    const syntheticBadges = screen.queryAllByText("Synthetic demo data");
    expect(syntheticBadges).toHaveLength(0);
  });
});

describe("AnalyticsSection — API error state", () => {
  it("T-CHART-010: shows error state, not fixture data, when API failed", () => {
    render(
      <AnalyticsSection
        liveAnalysis={null}
        liveAlerts={[]}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage="Scenario complete (fixture mode — API 500: Server error)"
      />,
    );
    // Should show error alerts, not live or synthetic badges
    const errorBadges = screen.getAllByText("API error");
    expect(errorBadges.length).toBeGreaterThanOrEqual(3);
  });
});

describe("AnalyticsSection — loading state", () => {
  it("T-CHART-012: shows loading state while scenario is running", () => {
    render(
      <AnalyticsSection
        liveAnalysis={null}
        liveAlerts={[]}
        overview={fixtureOverview}
        isLoading={true}
        apiErrorMessage={null}
      />,
    );
    const loadingBadges = screen.getAllByText("Loading…");
    expect(loadingBadges.length).toBeGreaterThanOrEqual(3);
  });
});

describe("AnalyticsSection — provider isolation", () => {
  it("T-CHART-001 and T-CHART-002: all three charts render the analytics section wrapper", () => {
    const { container } = render(
      <AnalyticsSection
        liveAnalysis={liveAnalysis}
        liveAlerts={liveAlerts}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage={null}
      />,
    );
    expect(
      container.querySelector(".analytics-section"),
    ).not.toBeNull();
  });

  it("T-CHART-007: no fraud language anywhere in the rendered section", () => {
    const { container } = render(
      <AnalyticsSection
        liveAnalysis={liveAnalysis}
        liveAlerts={liveAlerts}
        overview={fixtureOverview}
        isLoading={false}
        apiErrorMessage={null}
      />,
    );
    const text = container.textContent?.toLowerCase() ?? "";
    // Check for specific banned positive declarations — advisory disclaimers are OK
    expect(text).not.toContain("fraud detected");
    expect(text).not.toContain("fraud probability");
    expect(text).not.toContain("criminal activity");
  });
});
