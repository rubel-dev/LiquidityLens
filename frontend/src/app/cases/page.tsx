"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { api, type Case } from "@/lib/api";
import { clsx } from "clsx";
import CoordinationTimeline from "@/components/cases/CoordinationTimeline";

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  const reload = useCallback(() => api.cases.list().then(setCases), []);
  useEffect(() => { reload().finally(() => setLoading(false)); }, [reload]);

  const statusColor = (c: Case) => {
    if (c.resolved_at) return "border-green-800 bg-green-950/20";
    if (c.escalated_at) return "border-orange-700 bg-orange-950/20";
    if (c.acknowledged_at) return "border-yellow-700 bg-yellow-950/20";
    return "border-gray-700 bg-gray-900";
  };

  const statusLabel = (c: Case) => {
    if (c.resolved_at) return { text: c.false_positive ? "False Positive" : "Resolved", cls: "bg-green-800 text-green-200" };
    if (c.escalated_at) return { text: "Escalated", cls: "bg-orange-800 text-orange-200" };
    if (c.acknowledged_at) return { text: "Acknowledged", cls: "bg-yellow-800 text-yellow-200" };
    return { text: "Open", cls: "bg-red-800 text-red-200" };
  };

  if (loading) return <div className="text-gray-400 py-20 text-center">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Case Manager</h1>
        <span className="text-sm text-gray-400">{cases.length} cases</span>
      </div>

      {cases.length === 0 && (
        <div className="text-center py-16 text-gray-600">No cases yet — trigger a scenario from Operations</div>
      )}

      <div className="space-y-4">
        {cases.map((c) => {
          const sl = statusLabel(c);
          return (
            <Link key={c.id} href={`/cases/${c.id}`}>
              <div className={clsx("border rounded-xl p-4 space-y-3 hover:brightness-110 transition cursor-pointer", statusColor(c))}>
                {/* Header row */}
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className={clsx("text-xs px-2 py-0.5 rounded-full font-bold", sl.cls)}>{sl.text}</span>
                    <span className="text-xs text-gray-400 font-mono">{c.id.slice(0, 8)}...</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(c.created_at).toLocaleString("en-BD")}
                  </span>
                </div>

                {/* Timeline */}
                <CoordinationTimeline c={c} />

                {/* Owner + notes count */}
                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span>Owner: <span className="text-white font-medium">{c.assigned_to ?? "Unassigned"}</span></span>
                  <span>{c.notes.length} note{c.notes.length !== 1 ? "s" : ""}</span>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
