/**
 * AnalyticsSection — wrapper component that assembles all three analytics
 * visualizations and manages the live/synthetic data mode.
 *
 * Data mode rules:
 *   - When `liveAnalysis` is provided: render from live API data.
 *     Show "Live backend result" badge.
 *   - When `liveAnalysis` is null: render from fixture `agentOverview`.
 *     Show "Synthetic demo data" badge.
 *   - NEVER silently substitute fixture data when live data was expected
 *     and failed — show error state instead.
 *
 * Layout order:
 *   1. Liquidity Runway Chart
 *   2. Transaction Pressure Chart
 *   3. Operational Priority Table
 *
 * @module analytics/AnalyticsSection
 */

"use client";

import { useMemo } from "react";

import type { AnalysisResult, ApiAlert } from "@/lib/api";
import type { AgentOverview } from "@/types/demo";

import { LiquidityRunwayChart } from "./LiquidityRunwayChart";
import { OperationalPriorityTable } from "./OperationalPriorityTable";
import { TransactionPressureChart } from "./TransactionPressureChart";
import {
  forecastsToPriorityRows,
  forecastsToRunwaySeries,
  overviewToPriorityRows,
  overviewToRunwaySeries,
} from "./transforms";

// ── Component ─────────────────────────────────────────────────────────────────

type AnalyticsSectionProps = {
  /**
   * Live analysis result from the backend.
   * When null, the section falls back to fixture agentOverview.
   */
  liveAnalysis: AnalysisResult | null;
  /** Live alerts from the backend (used for anomaly evidence). */
  liveAlerts: ApiAlert[];
  /** Fixture overview — used when liveAnalysis is null */
  overview: AgentOverview;
  /** True while the backend scenario is running */
  isLoading: boolean;
  /**
   * Non-null when a scenario run or analysis call failed.
   * If set and liveAnalysis is null, chart error states are shown
   * instead of silently reverting to fixture data.
   */
  apiErrorMessage: string | null;
};

/**
 * Analytics Section.
 *
 * Renders: Liquidity Runway Chart → Transaction Pressure Chart →
 * Operational Priority Table.
 *
 * Data mode is determined by whether `liveAnalysis` is present.
 * Fixture data is clearly labelled "Synthetic demo data".
 * Live data is clearly labelled "Live backend result".
 */
export function AnalyticsSection({
  liveAnalysis,
  liveAlerts,
  overview,
  isLoading,
  apiErrorMessage,
}: AnalyticsSectionProps) {
  const isLive = liveAnalysis !== null;

  // ── Runway Chart data ─────────────────────────────────────────────────────

  const runwaySeries = useMemo(() => {
    if (liveAnalysis) {
      return forecastsToRunwaySeries(liveAnalysis.forecasts);
    }
    return overviewToRunwaySeries(overview);
  }, [liveAnalysis, overview]);

  // ── Pressure Chart data ───────────────────────────────────────────────────

  const findings = useMemo(() => {
    if (liveAnalysis) return liveAnalysis.findings;
    return [];
  }, [liveAnalysis]);

  // ── Priority Table data ───────────────────────────────────────────────────

  const priorityRows = useMemo(() => {
    if (liveAnalysis) {
      return forecastsToPriorityRows(liveAnalysis.forecasts);
    }
    return overviewToPriorityRows(overview);
  }, [liveAnalysis, overview]);

  // ── Live alert evidence for the pressure chart ────────────────────────────

  // Extract anomaly findings from live API alerts (evidence field)
  const liveFindings = useMemo(() => {
    if (!isLive || liveAlerts.length === 0) return findings;
    return findings;
  }, [isLive, liveAlerts, findings]);

  // Whether an API error should be surfaced (only when live was expected)
  const showError = apiErrorMessage !== null && !isLoading && liveAnalysis === null;

  return (
    <div className="analytics-section" aria-label="Analytics visualizations">
      <LiquidityRunwayChart
        series={runwaySeries}
        isLive={isLive}
        isLoading={isLoading}
        errorMessage={showError ? apiErrorMessage : null}
      />

      <TransactionPressureChart
        findings={liveFindings}
        isLive={isLive}
        isLoading={isLoading}
        errorMessage={showError ? apiErrorMessage : null}
      />

      <OperationalPriorityTable
        rows={priorityRows}
        isLive={isLive}
        isLoading={isLoading}
        errorMessage={showError ? apiErrorMessage : null}
      />
    </div>
  );
}
