/**
 * Component render tests for OperationalPriorityTable.
 *
 * Tests: sorting by urgency, provider isolation rows, missing value display,
 * live/synthetic badges, accessibility.
 */

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { OperationalPriorityTable } from "@/features/analytics/OperationalPriorityTable";
import type { PriorityRow } from "@/features/analytics/transforms";

const rows: PriorityRow[] = [
  {
    providerName: "Nagad (simulated)",
    providerCode: "NAGAD-SIM",
    isSharedCash: false,
    riskLevel: "stable",
    runwayMinutes: 220,
    runwayLabel: "3 hr 40 min",
    confidence: 0.9,
    confidenceTier: "high",
    alertStatus: null,
    caseStatus: null,
    recommendedNextStep: "No action required at this time.",
    urgencyScore: 3220,
  },
  {
    providerName: "bKash (simulated)",
    providerCode: "BKASH-SIM",
    isSharedCash: false,
    riskLevel: "critical",
    runwayMinutes: 24,
    runwayLabel: "24 min",
    confidence: 0.81,
    confidenceTier: "high",
    alertStatus: "open",
    caseStatus: "open",
    recommendedNextStep:
      "Coordinate approved liquidity support through the responsible provider operations channel.",
    urgencyScore: 24,
  },
  {
    providerName: "Shared physical cash",
    providerCode: null,
    isSharedCash: true,
    riskLevel: "stable",
    runwayMinutes: 160,
    runwayLabel: "2 hr 40 min",
    confidence: 0.72,
    confidenceTier: "medium",
    alertStatus: null,
    caseStatus: null,
    recommendedNextStep: "No action required at this time.",
    urgencyScore: 3160,
  },
  {
    providerName: "Rocket (simulated)",
    providerCode: "ROCKET-SIM",
    isSharedCash: false,
    riskLevel: "unknown",
    runwayMinutes: null,
    runwayLabel: "Unknown (data unavailable)",
    confidence: 0.25,
    confidenceTier: "low",
    alertStatus: null,
    caseStatus: null,
    recommendedNextStep: "Await data feed restoration before action.",
    urgencyScore: 9999,
  },
];

describe("OperationalPriorityTable — loading state", () => {
  it("T-CHART-012: shows loading state", () => {
    render(
      <OperationalPriorityTable
        rows={[]}
        isLive={false}
        isLoading={true}
        errorMessage={null}
      />,
    );
    expect(document.querySelector("[aria-busy='true']")).not.toBeNull();
  });
});

describe("OperationalPriorityTable — error state", () => {
  it("T-CHART-010: shows error state", () => {
    render(
      <OperationalPriorityTable
        rows={[]}
        isLive={false}
        isLoading={false}
        errorMessage="API 500: Server error"
      />,
    );
    expect(screen.getByRole("alert")).toBeDefined();
    expect(screen.getByText(/Unable to load priority data/i)).toBeDefined();
  });
});

describe("OperationalPriorityTable — empty state", () => {
  it("T-CHART-013: renders empty state", () => {
    render(
      <OperationalPriorityTable
        rows={[]}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText(/Run a scenario/i)).toBeDefined();
  });
});

describe("OperationalPriorityTable — sorting", () => {
  it("T-CHART-014: table rows are sorted by urgency — most critical first", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const table = screen.getByRole("table");
    const tableRows = table.querySelectorAll("tbody tr");
    // First row should be bKash (critical, 24 min)
    expect(tableRows[0]!.textContent).toContain("bKash");
  });
});

describe("OperationalPriorityTable — provider isolation", () => {
  it("T-CHART-001: renders each provider as a separate row", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const table = screen.getByRole("table");
    const tableRows = table.querySelectorAll("tbody tr");
    expect(tableRows).toHaveLength(4);
  });

  it("T-CHART-002: shared cash has Physical cash tag", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Physical cash")).toBeDefined();
  });
});

describe("OperationalPriorityTable — missing values", () => {
  it("T-CHART-003: null runway shows Unknown label, not zero or blank", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Unknown (data unavailable)")).toBeDefined();
  });
});

describe("OperationalPriorityTable — live vs synthetic badges", () => {
  it("T-CHART-008: shows Live backend result when isLive=true", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={true}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Live backend result")).toBeDefined();
  });

  it("T-CHART-009: shows Synthetic demo data when isLive=false", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    expect(screen.getByText("Synthetic demo data")).toBeDefined();
  });
});

describe("OperationalPriorityTable — accessibility", () => {
  it("T-CHART-015: table has accessible role and caption", () => {
    render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const table = screen.getByRole("table", {
      name: /Operational Priority/i,
    });
    expect(table).toBeDefined();
    expect(screen.getByText(/Human review required/i)).toBeDefined();
  });

  it("T-CHART-007: no fraud language in the table", () => {
    const { container } = render(
      <OperationalPriorityTable
        rows={rows}
        isLive={false}
        isLoading={false}
        errorMessage={null}
      />,
    );
    const text = container.textContent?.toLowerCase() ?? "";
    expect(text).not.toContain("fraud detected");
    expect(text).not.toContain("fraud probability");
    expect(text).not.toContain("criminal activity");
  });
});
