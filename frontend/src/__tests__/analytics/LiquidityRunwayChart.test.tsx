/**
 * Component render tests for LiquidityRunwayChart.
 *
 * Mock boundary: window.ResizeObserver (required by recharts in jsdom).
 * No mocking of transform functions — they run as normal.
 */

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeAll } from "vitest";

import type { ForecastSummary } from "@/lib/api";
import { LiquidityRunwayChart } from "@/features/analytics/LiquidityRunwayChart";
import { forecastsToRunwaySeries } from "@/features/analytics/transforms";

// Recharts uses ResizeObserver which jsdom doesn't provide
beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

const forecasts: ForecastSummary[] = [
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
];

const series = forecastsToRunwaySeries(forecasts);

describe("LiquidityRunwayChart — loading state", () => {
  it("T-CHART-012: shows loading state with aria-busy", () => {
    render(
      <LiquidityRunwayChart
        series={[]}
        isLive={false}
        isLoading={true}
        errorMessage={null}
      />,
    );
    const loadingBadge = screen.getByText("Loading…");
    expect(loadingBadge).toBeDefined();
    expect(document.querySelector("[aria-busy='true']")).not.toBeNull();
  });
});

describe("LiquidityRunwayChart — error state", () => {
  it("T-CHART-010: shows error state, not fixture data, when API fails", () => {
    render(
      <LiquidityRunwayChart
        series={[]}
        isLive={false}
        isLoading={false}
        errorMessage="API 500: Internal server error"
      />,
    );
    expect(screen.getByRole("alert")).toBeDefined();
    expect(screen.getByText(/Unable to load forecast data/i)).toBeDefined();
    expect(screen.getByText(/API 500/i)).toBeDefined();
  });

  it("T-CHART-010: error badge shown as API error", () => {
    render(
      <LiquidityRunwayChart
        series={[]}
        isLive={false}
        isLoading={false}
        errorMessage="Network error"
      />,
    );
    expect(screen.getByText("API error")).toBeDefined();
  });
});

describe("LiquidityRunwayChart — empty state", () => {
  it("T-CHART-013: renders empty state message", () => {
    render(
      <LiquidityRunwayChart
        series={[]}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText(/Run a scenario/i)).toBeDefined();
  });
});

describe("LiquidityRunwayChart — live vs synthetic badges", () => {
  it("T-CHART-008: shows Live backend result badge when isLive=true", () => {
    render(
      <LiquidityRunwayChart
        series={series}
        isLive={true}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Live backend result")).toBeDefined();
  });

  it("T-CHART-009: shows Synthetic demo data badge when isLive=false", () => {
    render(
      <LiquidityRunwayChart
        series={series}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Synthetic demo data")).toBeDefined();
  });
});

describe("LiquidityRunwayChart — accessibility", () => {
  it("T-CHART-015: chart panel has aria-label describing its purpose", () => {
    // Render with series data. If points are empty (jsdom), the empty state
    // div still carries the aria-label. Either way the panel is labelled.
    const { container } = render(
      <LiquidityRunwayChart
        series={series}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    // Find any element that has an aria-label containing 'Liquidity Runway Chart'
    const labelled = container.querySelector(
      "[aria-label*='Liquidity Runway Chart']",
    );
    expect(labelled).not.toBeNull();
    // Verify the element is present and visible (not hidden)
    expect((labelled as HTMLElement | null)?.tagName.toLowerCase()).toMatch(
      /^(section|div)$/,
    );
  });
});

describe("LiquidityRunwayChart — responsive rendering", () => {
  it("T-CHART-011: renders without crashing with multiple series", () => {
    const { container } = render(
      <LiquidityRunwayChart
        series={series}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(container.firstChild).not.toBeNull();
  });
});
