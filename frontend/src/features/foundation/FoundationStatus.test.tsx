import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Home from "@/app/page";

describe("foundation page", () => {
  it("renders the product foundation copy", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok", service: "liquiditylens-api", version: "0.1.0" }),
      }),
    );

    render(<Home />);

    expect(screen.getByRole("heading", { name: "LiquidityLens" })).toBeInTheDocument();
    expect(
      screen.getByText("Safe multi-provider liquidity decision-support prototype"),
    ).toBeInTheDocument();
    expect(screen.getByText("Synthetic data only")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("OK"));
  });

  it("renders an unavailable API state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    render(<Home />);

    await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Unavailable"));
  });
});

