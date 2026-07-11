import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";

const HEALTH_RESPONSE = {
  status: "ok",
  service: "liquiditylens-api",
  version: "0.1.0",
};

const SCENARIO_RUN_RESPONSE = {
  run_ref: "SIM-RUN-000001",
  scenario_code: "hidden_provider_shortage",
  status: "completed",
  seed: "5001",
  fingerprint: "154bb67ce5df79d4",
  generated_counts: { transactions: 40, balances: 3 },
};

const ANALYSIS_RESPONSE = {
  run_ref: "SIM-RUN-000001",
  agent_id: "00000000-0000-0000-0000-000000000010",
  forecasts_created: 3,
  findings_created: 1,
  alerts_created: 2,
  forecasts: [],
  findings: [],
  alert_ids: [],
};

function makeJsonResponse(body: unknown, ok = true) {
  return { ok, json: async () => body };
}

function stubHealthyApi() {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(makeJsonResponse(HEALTH_RESPONSE)),
  );
}

function stubSmartApi() {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((url: string) => {
      const path = typeof url === "string" ? url : String(url);
      if (path.includes("/analyze/"))
        return Promise.resolve(makeJsonResponse(ANALYSIS_RESPONSE));
      if (path.includes("/scenarios/") && path.includes("/run"))
        return Promise.resolve(makeJsonResponse(SCENARIO_RUN_RESPONSE));
      if (path.includes("/scenario-runs/"))
        return Promise.resolve(makeJsonResponse(SCENARIO_RUN_RESPONSE));
      if (path.includes("/alerts"))
        return Promise.resolve(makeJsonResponse([]));
      return Promise.resolve(makeJsonResponse(HEALTH_RESPONSE));
    }),
  );
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("LiquidityLens role-based demo", () => {
  it("renders the operations command centre and health state", async () => {
    stubSmartApi();
    render(<Home />);

    expect(
      screen.getByRole("heading", { name: "Liquidity command centre" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Synthetic data only")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        name: "Aggregate healthy. One rail is not.",
      }),
    ).toBeInTheDocument();
    expect(screen.getByText("Evidence fingerprint")).toBeInTheDocument();
    expect(screen.getByText("Case lifecycle")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getAllByRole("status")[0]).toHaveTextContent("OK"),
    );
  });

  it("falls back to an unavailable API state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    render(<Home />);

    await waitFor(() =>
      expect(screen.getAllByRole("status")[0]).toHaveTextContent("Unavailable"),
    );
  });

  it("shows low-confidence graceful degradation for missing data", async () => {
    stubSmartApi();
    const user = userEvent.setup();
    render(<Home />);

    await user.selectOptions(screen.getByLabelText("Scenario"), "SCN-003");
    await user.click(screen.getByRole("tab", { name: "Agent" }));

    expect(screen.getByText("Balance unavailable")).toBeInTheDocument();
    // The analytics module also renders insufficient-data notices for
    // all providers in SCN-003, so use getAllByText to allow multiple.
    expect(
      screen.getAllByText(/Insufficient data — no confident forecast/).length,
    ).toBeGreaterThan(0);
    // The analytics priority table also shows 30% confidence for each provider,
    // so use getAllByText and assert it appears at least once.
    expect(screen.getAllByText("30%").length).toBeGreaterThan(0);
  });

  it("keeps expected Eid demand out of the review queue", async () => {
    stubSmartApi();
    const user = userEvent.setup();
    render(<Home />);

    await user.selectOptions(screen.getByLabelText("Scenario"), "SCN-005");

    expect(
      screen.getByRole("heading", {
        name: "Expected demand correctly stays out of the case queue",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getAllByText(
        "The pattern is consistent with expected demand; no additional review is currently recommended.",
      ),
    ).toHaveLength(2);
  });

  it("supports safe localized explanations in the risk view", async () => {
    stubHealthyApi();
    const user = userEvent.setup();
    render(<Home />);

    await user.click(screen.getByRole("tab", { name: "Risk" }));
    await user.click(screen.getByRole("button", { name: "বাংলা" }));

    // Verify the Bangla explanation is active (language switcher worked)
    // and the deterministic template label is present
    const selectedBtn = screen.getByRole("button", { name: "বাংলা" });
    expect(selectedBtn).toHaveClass("selected");
    expect(screen.getByText(/Deterministic template/)).toBeInTheDocument();
  });

  it("advances the auditable case lifecycle", async () => {
    stubSmartApi();
    const user = userEvent.setup();
    render(<Home />);

    await user.click(
      screen.getByRole("button", { name: "Assign to field officer" }),
    );
    expect(
      screen.getByRole("button", { name: "Acknowledge" }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Acknowledge" }));
    await user.click(
      screen.getByRole("button", { name: "Escalate for review" }),
    );
    expect(
      screen.getByRole("button", { name: "Start risk review" }),
    ).toBeInTheDocument();
  });

  it("exposes manager evidence and deterministic demo controls", async () => {
    stubSmartApi();
    const user = userEvent.setup();
    render(<Home />);

    await user.click(screen.getByRole("tab", { name: "Manager" }));
    expect(
      screen.getByRole("heading", { name: "Metrics" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Audit trail" }),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("tab", { name: "Demo" }));
    expect(
      screen.getByRole("heading", { name: "Run provenance" }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Run scenario" }));
    await waitFor(() =>
      expect(screen.getByText(/Live · run SIM-RUN-000001/)).toBeInTheDocument(),
    );
    await user.click(screen.getByRole("button", { name: /Replay/ }));
    await waitFor(() =>
      expect(screen.getByText(/Replay matched seed/)).toBeInTheDocument(),
    );
    await user.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByText(/reference data preserved/)).toBeInTheDocument();
  });
});
