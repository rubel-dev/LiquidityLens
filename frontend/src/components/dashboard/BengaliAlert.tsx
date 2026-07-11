"use client";
import { clsx } from "clsx";
import type { Alert } from "@/lib/api";

export default function BengaliAlert({ alert }: { alert: Alert }) {
  if (!alert.message_bn && !alert.message_en) return null;

  const severityBorder: Record<string, string> = {
    critical: "border-red-500 bg-red-950/50",
    high:     "border-red-400 bg-red-950/30",
    medium:   "border-yellow-500 bg-yellow-950/30",
    low:      "border-blue-500 bg-blue-950/20",
  };

  return (
    <div className={clsx("rounded-xl border-2 p-4 space-y-3", severityBorder[alert.severity] ?? "border-gray-700 bg-gray-900")}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-widest text-gray-400">
          {alert.type} alert · {alert.provider?.toUpperCase() ?? "ALL"}
        </span>
        <span className={clsx(
          "text-xs px-2 py-0.5 rounded-full font-bold uppercase",
          alert.severity === "critical" || alert.severity === "high"
            ? "bg-red-700 text-red-100"
            : alert.severity === "medium"
            ? "bg-yellow-700 text-yellow-100"
            : "bg-blue-700 text-blue-100"
        )}>
          {alert.severity}
        </span>
      </div>

      {/* Bengali message */}
      {alert.message_bn && (
        <div className="text-base leading-relaxed" style={{ fontFamily: "serif" }}>
          {alert.message_bn}
        </div>
      )}

      {/* English message */}
      {alert.message_en && (
        <div className="text-xs text-gray-400 border-t border-gray-700 pt-2">
          {alert.message_en}
        </div>
      )}

      {/* Confidence */}
      {alert.confidence !== null && (
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>Confidence: {Math.round((alert.confidence ?? 0) * 100)}%</span>
          <span>·</span>
          <span>Uncertainty: {alert.uncertainty}</span>
          {alert.eta_minutes && <><span>·</span><span>ETA: ~{alert.eta_minutes} min</span></>}
        </div>
      )}

      {/* Owner */}
      {alert.owner_name && (
        <div className="text-xs bg-gray-800 rounded px-2 py-1 text-gray-300">
          Assigned to: <span className="font-semibold text-white">{alert.owner_name}</span>
          {" · "}Status: <span className="font-semibold">{alert.status}</span>
        </div>
      )}
    </div>
  );
}
