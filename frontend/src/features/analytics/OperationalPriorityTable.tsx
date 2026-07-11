/**
 * OperationalPriorityTable — compact sortable table for operations teams
 * showing providers ranked by operational urgency.
 *
 * Uses a table (not a pie chart) to allow precise comparison and prioritisation
 * as required by the specification.
 *
 * @module analytics/OperationalPriorityTable
 */

"use client";

import { useMemo } from "react";
import type { PriorityRow } from "./transforms";

// ── Helper renderers ──────────────────────────────────────────────────────────

function riskChip(riskLevel: string) {
  const map: Record<string, string> = {
    critical: "status-shortage_risk",
    warning: "status-watch",
    watch: "status-watch",
    stable: "status-healthy",
    healthy: "status-healthy",
    unknown: "status-insufficient_data",
  };
  const cls = map[riskLevel.toLowerCase()] ?? "status-watch";
  return (
    <span className={`status-chip ${cls}`} aria-label={`Risk level: ${riskLevel}`}>
      {riskLevel}
    </span>
  );
}

function confidenceChip(tier: "high" | "medium" | "low", score: number) {
  const cls =
    tier === "high"
      ? "confidence-high"
      : tier === "medium"
        ? "confidence-medium"
        : "confidence-low";
  return (
    <span className={`priority-confidence ${cls}`}>
      {Math.round(score * 100)}%
    </span>
  );
}

function statusText(status: string | null): string {
  if (!status) return "—";
  return status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, " ");
}

// ── Component ─────────────────────────────────────────────────────────────────

type OperationalPriorityTableProps = {
  /** Priority rows sorted by urgency */
  rows: PriorityRow[];
  /** True = data came from live API */
  isLive: boolean;
  /** True while loading */
  isLoading: boolean;
  /** Error message if API failed */
  errorMessage: string | null;
};

/**
 * Operational Priority Table.
 *
 * Sorted by urgency score (critical/short runway first).
 * Provider balances are shown as separate rows — never aggregated.
 */
export function OperationalPriorityTable({
  rows,
  isLive,
  isLoading,
  errorMessage,
}: OperationalPriorityTableProps) {
  // Ensure table is always sorted ascending by urgency
  const sorted = useMemo(
    () => [...rows].sort((a, b) => a.urgencyScore - b.urgencyScore),
    [rows],
  );

  // ── States ─────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div
        className="chart-panel chart-panel--loading"
        aria-busy="true"
        aria-label="Loading Operational Priority Table"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Operations</p>
            <h2>Operational Priority</h2>
          </div>
          <span className="data-badge data-badge--loading">Loading…</span>
        </div>
        <div className="chart-skeleton chart-skeleton--table" aria-hidden="true" />
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div
        className="chart-panel chart-panel--error"
        role="alert"
        aria-label="Operational Priority Table error"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Operations</p>
            <h2>Operational Priority</h2>
          </div>
          <span className="data-badge data-badge--error">API error</span>
        </div>
        <p className="chart-error-message">
          Unable to load priority data. {errorMessage}
        </p>
      </div>
    );
  }

  if (sorted.length === 0) {
    return (
      <div
        className="chart-panel chart-panel--empty"
        aria-label="Operational Priority Table — no data"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Operations</p>
            <h2>Operational Priority</h2>
          </div>
          <span
            className={`data-badge ${isLive ? "data-badge--live" : "data-badge--synthetic"}`}
          >
            {isLive ? "Live backend result" : "Synthetic demo data"}
          </span>
        </div>
        <p className="chart-empty-message">
          Run a scenario to see the operational priority table.
        </p>
      </div>
    );
  }

  // ── Full table ─────────────────────────────────────────────────────────────

  return (
    <section
      className="chart-panel priority-table-panel"
      aria-label="Operational Priority Table — providers sorted by urgency"
    >
      <div className="chart-panel__header">
        <div>
          <p className="eyebrow">Operations · sorted by urgency</p>
          <h2>Operational Priority</h2>
          <p className="chart-panel__subtitle">
            Provider balances are shown separately — never aggregated.
            Recommendations are advisory only.
          </p>
        </div>
        <span
          className={`data-badge ${isLive ? "data-badge--live" : "data-badge--synthetic"}`}
          aria-label={
            isLive
              ? "Data sourced from live backend API"
              : "Synthetic demo data — not production data"
          }
        >
          {isLive ? "Live backend result" : "Synthetic demo data"}
        </span>
      </div>

      <div className="priority-table-wrapper">
        <table className="priority-table" aria-label="Operational Priority — sorted most urgent first">
          <caption className="priority-table__caption">
            Providers sorted by operational urgency. Human review required
            before any action.
          </caption>
          <thead>
            <tr>
              <th scope="col">Provider</th>
              <th scope="col">Risk</th>
              <th scope="col">Est. Runway</th>
              <th scope="col">Confidence</th>
              <th scope="col">Alert</th>
              <th scope="col">Case</th>
              <th scope="col">Recommended next step</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((row) => (
              <tr
                key={`${row.providerCode ?? "shared"}-${row.riskLevel}`}
                className={`priority-row priority-row--${row.riskLevel}`}
              >
                <td>
                  <span className="priority-provider-name">
                    {row.providerName}
                  </span>
                  {row.isSharedCash && (
                    <span className="priority-provider-tag">Physical cash</span>
                  )}
                  {row.providerCode && !row.isSharedCash && (
                    <code className="priority-provider-code">
                      {row.providerCode}
                    </code>
                  )}
                </td>
                <td>{riskChip(row.riskLevel)}</td>
                <td>
                  <span
                    className={`priority-runway ${
                      row.runwayMinutes !== null && row.runwayMinutes <= 60
                        ? "priority-runway--urgent"
                        : ""
                    }`}
                    aria-label={`Estimated runway: ${row.runwayLabel}`}
                  >
                    {row.runwayLabel}
                  </span>
                </td>
                <td>
                  {confidenceChip(row.confidenceTier, row.confidence)}
                </td>
                <td>
                  <span className="priority-status">
                    {statusText(row.alertStatus)}
                  </span>
                </td>
                <td>
                  <span className="priority-status">
                    {statusText(row.caseStatus)}
                  </span>
                </td>
                <td>
                  <span className="priority-next-step">
                    {row.recommendedNextStep}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="chart-advisory">
        Recommendations are advisory only. The system does not execute
        financial actions, declare fraud, or automatically block users.
      </p>
    </section>
  );
}
