"use client";
import { useState } from "react";
import { clsx } from "clsx";
import type { LiquidityData } from "@/lib/api";

export default function DeceptiveTotal({ data, physicalCash }: { data: LiquidityData; physicalCash: number }) {
  const [expanded, setExpanded] = useState(false);

  const total = data.aggregate_emoney + physicalCash;
  const criticalProviders = data.providers.filter(
    (p) => p.eta_minutes !== null && p.eta_minutes < 45
  );
  const isDeceptive = criticalProviders.length > 0 && total > 20000;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm text-gray-400">Total Liquidity</span>
        {isDeceptive && (
          <span className="text-xs bg-red-900 text-red-300 px-2 py-0.5 rounded-full animate-pulse">
            Hidden shortage
          </span>
        )}
      </div>

      {/* The deceptive number */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-left w-full"
      >
        <div className={clsx("text-4xl font-bold mb-1", isDeceptive ? "text-green-400" : "text-green-400")}>
          ৳{total.toLocaleString()}
        </div>
        <div className="text-xs text-gray-500">
          {expanded ? "▲ Hide breakdown" : "▼ Show provider breakdown"}
        </div>
      </button>

      {/* Animated breakdown */}
      {expanded && (
        <div className="mt-4 space-y-2 border-t border-gray-800 pt-4">
          {data.providers.map((p) => {
            const isCritical = p.eta_minutes !== null && p.eta_minutes < 45;
            return (
              <div key={p.provider} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className={clsx("w-2 h-2 rounded-full", isCritical ? "bg-red-500 animate-pulse" : "bg-green-500")} />
                  <span className="uppercase font-medium">{p.provider}</span>
                  {p.data_quality !== "ok" && (
                    <span className="text-xs text-yellow-400">({p.data_quality})</span>
                  )}
                </div>
                <div className="text-right">
                  {p.balance !== null ? (
                    <span className={clsx("font-semibold", isCritical ? "text-red-400" : "text-gray-200")}>
                      ৳{p.balance.toLocaleString()}
                    </span>
                  ) : (
                    <span className="text-yellow-400 text-xs">unavailable</span>
                  )}
                  {isCritical && (
                    <div className="text-xs text-red-400">~{p.eta_minutes} min left</div>
                  )}
                </div>
              </div>
            );
          })}
          <div className="flex items-center justify-between text-sm border-t border-gray-800 pt-2 mt-2">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="font-medium">Physical Cash</span>
            </div>
            <span className="font-semibold">৳{physicalCash.toLocaleString()}</span>
          </div>
        </div>
      )}

      {isDeceptive && (
        <div className="mt-3 text-xs bg-red-950 border border-red-800 rounded px-3 py-2 text-red-300">
          The aggregate looks healthy, but {criticalProviders.map(p => p.provider.toUpperCase()).join(", ")} will deplete
          in {Math.min(...criticalProviders.map(p => p.eta_minutes ?? 999))} minutes.
        </div>
      )}
    </div>
  );
}
