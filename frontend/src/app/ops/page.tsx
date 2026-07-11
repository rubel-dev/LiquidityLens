"use client";
import { useEffect, useState, useCallback } from "react";
import { api, type Agent, type Alert } from "@/lib/api";
import { useWebSocket } from "@/lib/websocket";
import AlertCard from "@/components/alerts/AlertCard";
import { clsx } from "clsx";

const RISK_COLOR = (alerts: number) =>
  alerts === 0 ? "bg-green-900/30 border-green-800" :
  alerts === 1 ? "bg-yellow-900/30 border-yellow-800" :
  "bg-red-900/30 border-red-800";

export default function OpsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [filter, setFilter] = useState({ provider: "", severity: "", status: "open" });
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    const [ag, al] = await Promise.all([
      api.agents.list(),
      api.alerts.list({ status: filter.status || undefined, provider: filter.provider || undefined, severity: filter.severity || undefined }),
    ]);
    setAgents(ag);
    setAlerts(al);
  }, [filter]);

  useEffect(() => { reload().finally(() => setLoading(false)); }, [reload]);

  useWebSocket(useCallback((msg) => {
    if (msg.type === "new_alert") {
      reload();
      if (typeof document !== "undefined") {
        const sev = (msg.data.severity as string) ?? "";
        if (sev === "critical" || sev === "high") {
          document.title = `⚠ ${sev.toUpperCase()} ALERT — Operations`;
          setTimeout(() => (document.title = "Agent Liquidity Dashboard"), 8000);
        }
      }
    }
  }, [reload]));

  const acknowledge = async (id: string) => {
    await api.alerts.acknowledge(id, "Acknowledged from Operations Dashboard.", "Field Officer");
    reload();
  };
  const escalate = async (id: string) => {
    await api.alerts.escalate(id, "Escalated to Risk Analyst.", "Field Officer");
    reload();
  };

  const sortedAlerts = [...alerts].sort((a, b) => {
    const order = { critical: 0, high: 1, medium: 2, low: 3 };
    return (order[a.severity as keyof typeof order] ?? 4) - (order[b.severity as keyof typeof order] ?? 4);
  });

  if (loading) return <div className="text-gray-400 py-20 text-center">Loading...</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Operations Dashboard</h1>

      {/* Agent overview grid */}
      <div>
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Agent Status</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {agents.map((a) => (
            <div key={a.id} className={clsx("rounded-lg border p-3 text-sm", RISK_COLOR(a.open_alerts))}>
              <div className="font-semibold text-white truncate">{a.name}</div>
              <div className="text-xs text-gray-400 truncate">{a.area}</div>
              <div className="mt-1 flex items-center gap-2">
                <span className={clsx("font-bold", a.open_alerts > 0 ? "text-red-400" : "text-green-400")}>
                  {a.open_alerts} alert{a.open_alerts !== 1 ? "s" : ""}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                ৳{a.total_balance.toLocaleString()} total
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={filter.severity}
          onChange={(e) => setFilter((f) => ({ ...f, severity: e.target.value }))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-gray-200"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={filter.provider}
          onChange={(e) => setFilter((f) => ({ ...f, provider: e.target.value }))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-gray-200"
        >
          <option value="">All Providers</option>
          <option value="bkash">bKash</option>
          <option value="nagad">Nagad</option>
          <option value="rocket">Rocket</option>
        </select>
        <select
          value={filter.status}
          onChange={(e) => setFilter((f) => ({ ...f, status: e.target.value }))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-gray-200"
        >
          <option value="open">Open</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="escalated">Escalated</option>
          <option value="resolved">Resolved</option>
          <option value="">All</option>
        </select>
        <button
          onClick={() => api.simulate.eidRush().then(reload)}
          className="ml-auto text-xs px-3 py-1.5 bg-orange-900 hover:bg-orange-800 text-orange-200 rounded border border-orange-700 transition"
        >
          Trigger Eid Rush (Demo)
        </button>
      </div>

      {/* Alert queue */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
          Alert Queue ({sortedAlerts.length})
        </h2>
        {sortedAlerts.length === 0 && (
          <div className="text-center py-12 text-gray-600">No alerts matching filter</div>
        )}
        {sortedAlerts.map((a) => (
          <AlertCard
            key={a.id}
            alert={a}
            onAcknowledge={a.status === "open" ? acknowledge : undefined}
            onEscalate={a.status === "open" ? escalate : undefined}
          />
        ))}
      </div>
    </div>
  );
}
