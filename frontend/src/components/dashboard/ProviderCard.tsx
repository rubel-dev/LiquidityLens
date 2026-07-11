"use client";
import { clsx } from "clsx";
import type { LiquidityProvider } from "@/lib/api";

const PROVIDER_COLORS: Record<string, string> = {
  bkash:  "border-pink-500",
  nagad:  "border-orange-500",
  rocket: "border-purple-500",
};
const PROVIDER_BG: Record<string, string> = {
  bkash:  "bg-pink-950/40",
  nagad:  "bg-orange-950/40",
  rocket: "bg-purple-950/40",
};
const QUALITY_BADGE: Record<string, string> = {
  ok:       "bg-green-800 text-green-200",
  delayed:  "bg-yellow-800 text-yellow-200",
  missing:  "bg-red-800 text-red-200",
  conflict: "bg-red-800 text-red-200",
};

function etaColor(eta: number | null) {
  if (eta === null) return "text-green-400";
  if (eta < 20) return "text-red-400 animate-pulse";
  if (eta < 45) return "text-red-400";
  if (eta < 90) return "text-yellow-400";
  return "text-green-400";
}

export default function ProviderCard({ p }: { p: LiquidityProvider }) {
  const borderColor = PROVIDER_COLORS[p.provider] ?? "border-gray-700";
  const bgColor = PROVIDER_BG[p.provider] ?? "bg-gray-900";

  return (
    <div className={clsx("rounded-xl border-2 p-4 flex flex-col gap-3", borderColor, bgColor)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="font-bold text-lg uppercase tracking-wide">{p.provider}</span>
        <span className={clsx("text-xs px-2 py-0.5 rounded-full font-medium", QUALITY_BADGE[p.data_quality] ?? "bg-gray-700 text-gray-300")}>
          {p.data_quality}
        </span>
      </div>

      {/* Balance */}
      {p.balance !== null ? (
        <div>
          <div className="text-2xl font-bold">৳{p.balance.toLocaleString()}</div>
          <div className="text-xs text-gray-400">e-money balance</div>
        </div>
      ) : (
        <div className="text-yellow-400 text-sm">Balance unavailable</div>
      )}

      {/* ETA */}
      {p.eta_minutes !== null && (
        <div className={clsx("text-sm font-semibold", etaColor(p.eta_minutes))}>
          ⚠ Depletes in ~{p.eta_minutes} min
        </div>
      )}

      {/* Confidence bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Confidence</span>
          <span>{Math.round(p.confidence * 100)}%</span>
        </div>
        <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={clsx("h-full rounded-full transition-all", p.confidence > 0.7 ? "bg-green-500" : p.confidence > 0.4 ? "bg-yellow-500" : "bg-red-500")}
            style={{ width: `${p.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Topup recommendation */}
      {p.recommended_topup && (
        <div className="text-xs bg-yellow-900/50 border border-yellow-700 rounded px-2 py-1 text-yellow-300">
          Recommended top-up: ৳{p.recommended_topup.toLocaleString()}
        </div>
      )}

      {/* Rate */}
      {p.rate_per_minute > 0 && (
        <div className="text-xs text-gray-500">Outflow: ৳{(p.rate_per_minute * 60).toFixed(0)}/hr</div>
      )}
    </div>
  );
}
