import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";

function stubHealthyApi() {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "ok",
        service: "liquiditylens-api",
        version: "0.1.0",
      }),
    }),
  );
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("LiquidityLens role-based demo", () => {
  it("renders the operations command centre and health state", async () => {
    stubHealthyApi();
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
    stubHealthyApi();
    const user = userEvent.setup();
    render(<Home />);

    await user.selectOptions(screen.getByLabelText("Scenario"), "SCN-003");
    await user.click(screen.getByRole("tab", { name: "Agent" }));

    expect(screen.getByText("Balance unavailable")).toBeInTheDocument();
    expect(
      screen.getByText(/Insufficient data — no confident forecast/),
    ).toBeInTheDocument();
    expect(screen.getByText("30%")).toBeInTheDocument();
  });

  it("keeps expected Eid demand out of the review queue", async () => {
    stubHealthyApi();
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

    expect(screen.getByText(/মানব পর্যালোচনা প্রয়োজন/)).toBeInTheDocument();
    expect(
      screen.getByText(/Deterministic template fallback/),
    ).toBeInTheDocument();
  });

  it("advances the auditable case lifecycle", async () => {
    stubHealthyApi();
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
    stubHealthyApi();
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
    expect(screen.getByText(/Scenario complete/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Replay" }));
    expect(
      screen.getByText(/Replay matched original seed/),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByText(/reference data preserved/)).toBeInTheDocument();
  });
});
