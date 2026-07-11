/**
 * LiquidityRunwayChart — time-series line chart showing forecasted balance
 * over time per provider.
 *
 * Safety rules:
 *   - Each provider renders as a separate, isolated line.
 *   - Shared physical cash is always its own line (never merged with e-money).
 *   - Missing balance renders as a gap in the line, never as zero.
 *   - Confidence < 0.40 suppresses the line and shows "Insufficient data".
 *   - All language is advisory ("Estimated shortage", not a declaration).
 *
 * @module analytics/LiquidityRunwayChart
 */

"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { RunwaySeries } from "./transforms";
import { formatBdt, formatRunwayMinutes, MIN_CONFIDENCE_TO_RENDER } from "./transforms";

// ── Provider colour palette (accessible, distinct) ───────────────────────────

/** Accessible, high-contrast colour per series index. */
const SERIES_COLOURS: readonly string[] = [
  "#E2136E", // brand pink  — shared cash
  "#2563EB", // blue        — bKash
  "#16A34A", // green       — Nagad
  "#D97706", // amber       — Rocket
  "#7C3AED", // violet      — any additional provider
];

function seriesColour(index: number): string {
  return SERIES_COLOURS[index % SERIES_COLOURS.length] ?? "#9CA3AF";
}

// ── Tooltip ──────────────────────────────────────────────────────────────────

type TooltipPayloadEntry = {
  name: string;
  value: number | null;
  color: string;
};

type CustomTooltipProps = {
  active?: boolean;
  payload?: TooltipPayloadEntry[];
  label?: string;
};

function CustomTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="chart-tooltip" role="tooltip">
      <p className="chart-tooltip-label">{label} min</p>
      {payload.map((entry) => (
        <div key={entry.name} className="chart-tooltip-row">
          <span
            className="chart-tooltip-dot"
            style={{ background: entry.color }}
          />
          <span>{entry.name}:</span>
          <strong>
            {entry.value !== null && entry.value !== undefined
              ? formatBdt(entry.value)
              : "Unknown (data unavailable)"}
          </strong>
        </div>
      ))}
    </div>
  );
}

// ── Shortage marker label ─────────────────────────────────────────────────────

type ShortageMarker = {
  /** Series name experiencing the earliest shortage */
  label: string;
  /** Minutes from now when shortage is estimated */
  minutesFromNow: number;
  /** Colour matching the series */
  colour: string;
};

function buildShortageMarkers(series: RunwaySeries[]): ShortageMarker[] {
  return series
    .filter(
      (s) =>
        s.runwayMinutes !== null &&
        s.runwayMinutes > 0 &&
        s.sufficientConfidence &&
        s.runwayMinutes <= 180,
    )
    .map((s, idx) => ({
      label: `Estimated shortage: ${s.providerName} (~${formatRunwayMinutes(s.runwayMinutes)})`,
      minutesFromNow: s.runwayMinutes!,
      colour: seriesColour(series.indexOf(s) === -1 ? idx : series.indexOf(s)),
    }));
}

// ── Chart component ──────────────────────────────────────────────────────────

type LiquidityRunwayChartProps = {
  /** Array of provider series. Each must be isolated; shared cash has providerCode null. */
  series: RunwaySeries[];
  /** True = data came from live API; false = synthetic fixture data */
  isLive: boolean;
  /** True while the API request is in flight */
  isLoading: boolean;
  /** Non-null string when the API request failed */
  errorMessage: string | null;
};

/**
 * Liquidity Runway Chart — shows estimated balance over time per provider.
 *
 * Charts are advisory decision-support tools only.
 * Human review is required before any operational action.
 */
export function LiquidityRunwayChart({
  series,
  isLive,
  isLoading,
  errorMessage,
}: LiquidityRunwayChartProps) {
  // Merge all unique time points across providers into a single X-axis
  const chartData = useMemo(() => {
    const minuteSet = new Set<number>();
    for (const s of series) {
      for (const p of s.points) {
        minuteSet.add(p.minutesFromNow);
      }
    }
    const sorted = Array.from(minuteSet).sort((a, b) => a - b);

    return sorted.map((min) => {
      const row: Record<string, number | null | string> = {
        minutesFromNow: min,
      };
      for (const s of series) {
        if (!s.sufficientConfidence) {
          // Do not render a line for insufficient confidence
          row[s.providerName] = null;
          continue;
        }
        const point = s.points.find((p) => p.minutesFromNow === min);
        // If point is absent for this minute: gap (null), never zero
        row[s.providerName] = point?.balanceBdt ?? null;
      }
      return row;
    });
  }, [series]);

  const shortageMarkers = useMemo(
    () => buildShortageMarkers(series),
    [series],
  );

  const insufficientSeries = series.filter((s) => !s.sufficientConfidence);

  // ── States ─────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div
        className="chart-panel chart-panel--loading"
        aria-busy="true"
        aria-label="Loading Liquidity Runway Chart"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Analytics</p>
            <h2>Liquidity Runway Chart</h2>
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
        aria-label="Liquidity Runway Chart error"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Analytics</p>
            <h2>Liquidity Runway Chart</h2>
          </div>
          <span className="data-badge data-badge--error">API error</span>
        </div>
        <p className="chart-error-message">
          Unable to load forecast data. Last valid data is shown if available.
        </p>
        <p className="chart-error-detail" aria-live="polite">
          {errorMessage}
        </p>
      </div>
    );
  }

  if (series.length === 0 || chartData.length === 0) {
    return (
      <div
        className="chart-panel chart-panel--empty"
        aria-label="Liquidity Runway Chart — no data"
      >
        <div className="chart-panel__header">
          <div>
            <p className="eyebrow">Analytics</p>
            <h2>Liquidity Runway Chart</h2>
          </div>
          <span className={`data-badge ${isLive ? "data-badge--live" : "data-badge--synthetic"}`}>
            {isLive ? "Live backend result" : "Synthetic demo data"}
          </span>
        </div>
        <p className="chart-empty-message">
          Run a scenario to see forecasted provider balances over time.
        </p>
      </div>
    );
  }

  // ── Full chart ─────────────────────────────────────────────────────────────

  return (
    <section
      className="chart-panel"
      aria-label="Liquidity Runway Chart — forecasted balance per provider over time"
    >
      <div className="chart-panel__header">
        <div>
          <p className="eyebrow">Analytics · decision support only</p>
          <h2>Liquidity Runway Chart</h2>
          <p className="chart-panel__subtitle">
            Estimated balance over time · each provider shown separately ·
            shared cash is provider-independent
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

      {/* Shortage markers summary */}
      {shortageMarkers.length > 0 && (
        <div className="chart-shortage-summary" role="status">
          {shortageMarkers.map((m) => (
            <span key={m.label} className="chart-shortage-tag">
              <span
                className="chart-shortage-dot"
                style={{ background: m.colour }}
                aria-hidden="true"
              />
              {m.label}
            </span>
          ))}
        </div>
      )}

      {/* Insufficient confidence notices */}
      {insufficientSeries.length > 0 && (
        <div className="chart-insufficient-notice" role="note">
          {insufficientSeries.map((s) => (
            <span key={s.providerName} className="chart-insufficient-tag">
              {s.providerName}: Insufficient data — no confident forecast
              (confidence {Math.round(s.confidence * 100)}% &lt;{" "}
              {Math.round(MIN_CONFIDENCE_TO_RENDER * 100)}% threshold)
            </span>
          ))}
        </div>
      )}

      <div
        className="chart-container"
        aria-hidden="true"
        role="img"
        aria-label="Line chart showing forecasted balance over time for each provider"
      >
        <ResponsiveContainer width="100%" height={280}>
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 24, bottom: 0, left: 16 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--border)"
              vertical={false}
            />
            <XAxis
              dataKey="minutesFromNow"
              tick={{ fontSize: 11, fill: "var(--text-tertiary)" }}
              tickFormatter={(v: number) =>
                v === 0 ? "Now" : `+${v}m`
              }
              label={{
                value: "Minutes from now",
                position: "insideBottom",
                offset: -4,
                fontSize: 10,
                fill: "var(--text-tertiary)",
              }}
            />
            <YAxis
              tick={{ fontSize: 11, fill: "var(--text-tertiary)" }}
              tickFormatter={(v: number) =>
                v >= 1_00_000
                  ? `৳${(v / 1_00_000).toFixed(1)}L`
                  : v >= 1_000
                    ? `৳${(v / 1_000).toFixed(0)}K`
                    : `৳${v}`
              }
              label={{
                value: "Balance (BDT)",
                angle: -90,
                position: "insideLeft",
                offset: 12,
                fontSize: 10,
                fill: "var(--text-tertiary)",
              }}
              width={70}
            />
            <Tooltip
              content={<CustomTooltip />}
              allowEscapeViewBox={{ x: false, y: true }}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 12 }}
              formatter={(value: string) => (
                <span style={{ color: "var(--text-secondary)" }}>{value}</span>
              )}
            />

            {/* Provider lines — each is isolated, shared cash is distinct */}
            {series.map((s, idx) => (
              <Line
                key={s.providerName}
                type="monotone"
                dataKey={s.providerName}
                stroke={seriesColour(idx)}
                strokeWidth={s.isSharedCash ? 2.5 : 2}
                strokeDasharray={s.isSharedCash ? undefined : undefined}
                dot={false}
                connectNulls={false}
                activeDot={{ r: 5 }}
                name={s.providerName}
                aria-label={`Balance forecast for ${s.providerName}`}
              />
            ))}

            {/* Shortage time markers */}
            {shortageMarkers.map((m) => (
              <ReferenceLine
                key={`shortage-${m.minutesFromNow}`}
                x={m.minutesFromNow}
                stroke={m.colour}
                strokeDasharray="5 4"
                strokeWidth={1.5}
                label={{
                  value: `⚠ ~${m.minutesFromNow}m`,
                  position: "top",
                  fontSize: 10,
                  fill: m.colour,
                }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <p className="chart-advisory">
        Charts are advisory decision-support tools. Human review is required
        before any operational action. Provider balances cannot be converted
        or transferred between providers.
      </p>
    </section>
  );
}
