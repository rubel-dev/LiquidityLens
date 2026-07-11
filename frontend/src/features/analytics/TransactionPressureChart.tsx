/**
 * TransactionPressureChart — shows recent transaction demand against a
 * normal baseline, highlighting anomalous windows from evidence.
 *
 * Safety language rules (strict):
 *   ✓ "Unusual activity"
 *   ✓ "Requires review"
 *   ✓ "Higher than normal"
 *   ✓ "May have a legitimate explanation"
 *   ✗ "Fraud detected"  — NEVER
 *   ✗ "Fraud probability" — NEVER
 *   ✗ "Criminal activity" — NEVER
 *
 * @module analytics/TransactionPressureChart
 */

"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { FindingSummary } from "@/lib/api";
import type { PressureBaseline, PressurePoint } from "./transforms";
import { buildPressureBaseline, evidenceToPressurePoints } from "./transforms";

// ── Tooltip ──────────────────────────────────────────────────────────────────

type PressureTooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: PressurePoint; value: number }>;
  label?: string;
};

function PressureTooltip({ active, payload }: PressureTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0]?.payload;
  if (!point) return null;

  return (
    <div className="chart-tooltip" role="tooltip">
      <p className="chart-tooltip-label">{point.label}</p>
      <div className="chart-tooltip-row">
        <span>Transaction count:</span>
        <strong>{point.count}</strong>
      </div>
      {point.hasAnomaly && point.anomalyDescription && (
        <div className="chart-tooltip-anomaly">
          <span aria-label="Unusual activity indicator">⚠</span>
          {point.anomalyDescription}
        </div>
      )}
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

type TransactionPressureChartProps = {
  /** Anomaly findings from the analysis API (may be empty) */
  findings: FindingSummary[];
  /** True = data came from live API; false = synthetic fixture data */
  isLive: boolean;
  /** True while the API request is in flight */
  isLoading: boolean;
  /** Non-null string when the API request failed */
  errorMessage: string | null;
  /** Normal baseline count per 5-minute interval (from overview fixture) */
  baselineCount?: number;
};

const DEFAULT_BASELINE = 4; // synthetic baseline: ~4 transactions per 5 minutes

/**
 * Transaction Pressure Chart — shows demand in 5-minute buckets over the
 * last 30 minutes, with anomalous windows highlighted.
 *
 * This chart is for situational awareness only. Unusual patterns detected
 * by the backend require human review and may have legitimate explanations.
 */
export function TransactionPressureChart({
  findings,
  isLive,
  isLoading,
  errorMessage,
  baselineCount = DEFAULT_BASELINE,
}: TransactionPressureChartProps) {
  const points = useMemo(
    () => evidenceToPressurePoints(findings, baselineCount),
    [findings, baselineCount],
  );

  const currentMax = useMemo(
    () => Math.max(...points.map((p) => p.count)),
    [points],
  );

  const baseline = useMemo(
    () => buildPressureBaseline(baselineCount, currentMax),
    [baselineCount, currentMax],
  );

  const hasAnomaly = useMemo(
    () => points.some((p) => p.hasAnomaly),
    [points],
  );

  // ── States ─────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div
        className="chart-panel chart-panel--loading"
        aria-busy="true"
        aria-label="Loading Transaction Pressure Chart"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Analytics</p>
            <h2>Transaction Pressure</h2>
          </div>
          <span className="data-badge data-badge--loading">Loading…</span>
        </div>
        <div className="chart-skeleton" aria-hidden="true" />
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div
        className="chart-panel chart-panel--error"
        role="alert"
        aria-label="Transaction Pressure Chart error"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Analytics</p>
            <h2>Transaction Pressure</h2>
          </div>
          <span className="data-badge data-badge--error">API error</span>
        </div>
        <p className="chart-error-message">
          Unable to load transaction evidence. Last valid data is shown if
          available.
        </p>
        <p className="chart-error-detail" aria-live="polite">
          {errorMessage}
        </p>
      </div>
    );
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <section
      className="chart-panel"
      aria-label="Transaction Pressure Chart — demand in 5-minute buckets over 30 minutes"
    >
      <div className="chart-panel__header">
        <div>
          <p className="eyebrow">Analytics · decision support only</p>
          <h2>Transaction Pressure</h2>
          <p className="chart-panel__subtitle">
            30-minute window · 5-minute buckets · cash-in and cash-out demand
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

      {/* Baseline summary row */}
      <div className="chart-baseline-row">
        <div className="chart-baseline-item">
          <span>Normal baseline</span>
          <strong>{baseline.normalCount} / 5 min</strong>
        </div>
        <div className="chart-baseline-item">
          <span>Current peak</span>
          <strong>{currentMax} / 5 min</strong>
        </div>
        {baseline.ratioLabel && (
          <div
            className={`chart-baseline-item chart-baseline-ratio ${hasAnomaly ? "chart-baseline-ratio--anomaly" : ""}`}
          >
            <span>vs. baseline</span>
            <strong>{baseline.ratioLabel}</strong>
          </div>
        )}
      </div>

      {/* Anomaly notice — safe language only */}
      {hasAnomaly && (
        <div className="chart-anomaly-notice" role="note" aria-live="polite">
          <span className="chart-anomaly-notice__icon" aria-hidden="true">
            ⚠
          </span>
          <div>
            <strong>Unusual activity detected — requires human review</strong>
            <p>
              The backend engine has detected an unusual transaction pattern in
              the highlighted window. This may have a legitimate explanation and
              requires human review before any action is taken. The system does
              not automatically block users or declare wrongdoing.
            </p>
          </div>
        </div>
      )}

      <div
        className="chart-container"
        aria-hidden="true"
        role="img"
        aria-label="Bar chart showing transaction count per 5-minute interval"
      >
        <ResponsiveContainer width="100%" height={220}>
          <BarChart
            data={points}
            margin={{ top: 10, right: 24, bottom: 0, left: 8 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--border)"
              vertical={false}
            />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 11, fill: "var(--text-tertiary)" }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "var(--text-tertiary)" }}
              label={{
                value: "Transactions",
                angle: -90,
                position: "insideLeft",
                offset: 12,
                fontSize: 10,
                fill: "var(--text-tertiary)",
              }}
              width={55}
            />
            <Tooltip content={<PressureTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 11 }}
              content={() => (
                <div className="chart-legend-row">
                  <span className="chart-legend-dot chart-legend-dot--normal" />
                  <span>Normal activity</span>
                  <span
                    className="chart-legend-dot chart-legend-dot--anomaly"
                    style={{ marginLeft: 14 }}
                  />
                  <span>Unusual activity — requires review</span>
                </div>
              )}
            />

            {/* Baseline reference line */}
            <ReferenceLine
              y={baselineCount}
              stroke="var(--stable)"
              strokeDasharray="5 4"
              strokeWidth={1.5}
              label={{
                value: `Baseline (${baselineCount})`,
                position: "insideTopRight",
                fontSize: 10,
                fill: "var(--stable)",
              }}
            />

            {/* Bars coloured by anomaly */}
            <Bar dataKey="count" name="Transactions" radius={[3, 3, 0, 0]}>
              {points.map((entry) => (
                <Cell
                  key={`cell-${entry.label}`}
                  fill={
                    entry.hasAnomaly
                      ? "var(--critical)"
                      : "var(--watch)"
                  }
                  fillOpacity={entry.hasAnomaly ? 0.85 : 0.6}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="chart-advisory">
        Unusual activity indicators require human review and may have
        legitimate explanations. The system does not declare fraud, block
        users, or execute financial actions.
      </p>
    </section>
  );
}
