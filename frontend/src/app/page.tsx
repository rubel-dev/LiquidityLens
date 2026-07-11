import { FoundationStatus } from "@/features/foundation/FoundationStatus";

export default function Home() {
  return (
    <main>
      <section className="foundation-shell" aria-labelledby="foundation-title">
        <div className="foundation-panel">
          <h1 id="foundation-title" className="foundation-title">
            LiquidityLens
          </h1>
          <p className="foundation-subtitle">
            Safe multi-provider liquidity decision-support prototype
          </p>
        </div>
        <FoundationStatus />
        <div className="foundation-panel synthetic-label">
          Synthetic data only
        </div>
      </section>
    </main>
  );
}
