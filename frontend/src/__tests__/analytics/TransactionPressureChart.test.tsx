/**
 * Component render tests for TransactionPressureChart.
 *
 * Critical safety check: no "fraud" language must appear in any rendered output.
 */

import { render, screen } from "@testing-library/react";
import { describe, expect, it, beforeAll } from "vitest";

import type { FindingSummary } from "@/lib/api";
import { TransactionPressureChart } from "@/features/analytics/TransactionPressureChart";

beforeAll(() => {
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

const anomalyFindings: FindingSummary[] = [
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

describe("TransactionPressureChart — loading state", () => {
  it("T-CHART-012: shows loading state", () => {
    render(
      <TransactionPressureChart
        findings={[]}
        isLive={false}
        isLoading={true}
        errorMessage={null}
      />,
    );
    expect(document.querySelector("[aria-busy='true']")).not.toBeNull();
  });
});

describe("TransactionPressureChart — error state", () => {
  it("T-CHART-010: shows error state and message", () => {
    render(
      <TransactionPressureChart
        findings={[]}
        isLive={false}
        isLoading={false}
        errorMessage="API 503: Service unavailable"
      />,
    );
    expect(screen.getByRole("alert")).toBeDefined();
    expect(screen.getByText(/Unable to load transaction evidence/i)).toBeDefined();
  });
});

describe("TransactionPressureChart — safe language", () => {
  it("T-CHART-006: anomaly notice uses safe language", () => {
    render(
      <TransactionPressureChart
        findings={anomalyFindings}
        isLive={true}
        isLoading={false}
        errorMessage={null}
      />,
    );
    // Safe language must appear
    expect(screen.getByText(/Unusual activity detected/i)).toBeDefined();
    // Use getAllByText since 'human review' appears in notice + advisory footer
    const humanReviewMatches = screen.getAllByText(/human review/i);
    expect(humanReviewMatches.length).toBeGreaterThan(0);
    const legitimateMatches = screen.getAllByText(/legitimate explanation/i);
    expect(legitimateMatches.length).toBeGreaterThan(0);
  });

  it("T-CHART-007: no fraud language appears anywhere in the rendered output", () => {
    const { container } = render(
      <TransactionPressureChart
        findings={anomalyFindings}
        isLive={true}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const text = container.textContent?.toLowerCase() ?? "";
    expect(text).not.toContain("fraud detected");
    expect(text).not.toContain("fraud probability");
    expect(text).not.toContain("criminal activity");
  });

  it("T-CHART-007: no fraud language with no findings either", () => {
    const { container } = render(
      <TransactionPressureChart
        findings={[]}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const text = container.textContent?.toLowerCase() ?? "";
    // Check for specific banned phrases — advisory text may say "does not declare fraud"
    // which is a disclaimer and is acceptable. Banned are the positive declarations.
    expect(text).not.toContain("fraud detected");
    expect(text).not.toContain("fraud probability");
    expect(text).not.toContain("criminal activity");
  });
});

describe("TransactionPressureChart — live vs synthetic badges", () => {
  it("T-CHART-008: shows Live backend result when isLive=true", () => {
    render(
      <TransactionPressureChart
        findings={[]}
        isLive={true}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Live backend result")).toBeDefined();
  });

  it("T-CHART-009: shows Synthetic demo data when isLive=false", () => {
    render(
      <TransactionPressureChart
        findings={[]}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Synthetic demo data")).toBeDefined();
  });
});

describe("TransactionPressureChart — accessibility", () => {
  it("T-CHART-015: chart section has aria-label", () => {
    render(
      <TransactionPressureChart
        findings={[]}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const section = screen.getByRole("region", {
      name: /Transaction Pressure Chart/i,
    });
    expect(section).toBeDefined();
  });
});

describe("TransactionPressureChart — responsive rendering", () => {
  it("T-CHART-011: renders without crashing", () => {
    const { container } = render(
      <TransactionPressureChart
        findings={anomalyFindings}
        isLive={true}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(container.firstChild).not.toBeNull();
  });
});
