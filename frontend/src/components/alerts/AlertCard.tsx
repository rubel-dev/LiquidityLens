"use client";
import { clsx } from "clsx";
import type { Alert } from "@/lib/api";

const SEVERITY_STYLE: Record<string, string> = {
  critical: "border-l-red-500 bg-red-950/20",
  high:     "border-l-red-400 bg-red-950/10",
  medium:   "border-l-yellow-500 bg-yellow-950/10",
  low:      "border-l-blue-500 bg-blue-950/10",
};
const SEVERITY_BADGE: Record<string, string> = {
  critical: "bg-red-700 text-red-100",
  high:     "bg-red-800 text-red-200",
  medium:   "bg-yellow-800 text-yellow-200",
  low:      "bg-blue-800 text-blue-200",
};

interface Props {
  alert: Alert;
  onAcknowledge?: (id: string) => void;
  onEscalate?: (id: string) => void;
  onClick?: (id: string) => void;
}

export default function AlertCard({ alert, onAcknowledge, onEscalate, onClick }: Props) {
  const timeAgo = (iso: string) => {
    const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  };

  return (
    <div
      className={clsx(
        "border-l-4 rounded-r-xl p-4 space-y-2 cursor-pointer hover:brightness-110 transition",
        SEVERITY_STYLE[alert.severity] ?? "border-l-gray-500 bg-gray-900"
      )}
      onClick={() => onClick?.(alert.id)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={clsx("text-xs px-2 py-0.5 rounded-full font-bold uppercase", SEVERITY_BADGE[alert.severity])}>
            {alert.severity}
          </span>
          <span className="text-xs text-gray-400 uppercase">{alert.type}</span>
          {alert.provider && (
            <span className="text-xs font-semibold text-gray-300 uppercase">{alert.provider}</span>
          )}
        </div>
        <span className="text-xs text-gray-500 shrink-0">{timeAgo(alert.created_at)}</span>
      </div>

      {/* Bengali message preview */}
      {alert.message_bn && (
        <div className="text-sm leading-relaxed line-clamp-2" style={{ fontFamily: "serif" }}>
          {alert.message_bn}
        </div>
      )}

      {/* ETA + confidence row */}
      <div className="flex items-center gap-3 text-xs text-gray-500">
        {alert.eta_minutes && <span>ETA: ~{alert.eta_minutes} min</span>}
        {alert.confidence && <span>Confidence: {Math.round(alert.confidence * 100)}%</span>}
        <span>Owner: {alert.owner_name ?? "Unassigned"}</span>
      </div>

      {/* Actions */}
      {alert.status === "open" && (onAcknowledge || onEscalate) && (
        <div className="flex gap-2 pt-1" onClick={(e) => e.stopPropagation()}>
          {onAcknowledge && (
            <button
              onClick={() => onAcknowledge(alert.id)}
              className="text-xs px-3 py-1 bg-blue-800 hover:bg-blue-700 rounded text-white transition"
            >
              Acknowledge
            </button>
          )}
          {onEscalate && (
            <button
              onClick={() => onEscalate(alert.id)}
              className="text-xs px-3 py-1 bg-orange-800 hover:bg-orange-700 rounded text-white transition"
            >
              Escalate
            </button>
          )}
        </div>
      )}
    </div>
  );
}
