"use client";
import { useEffect, useState, useCallback } from "react";
import { api, type Agent, type LiquidityData, type Alert } from "@/lib/api";
import { useWebSocket } from "@/lib/websocket";
import DeceptiveTotal from "@/components/dashboard/DeceptiveTotal";
import ProviderCard from "@/components/dashboard/ProviderCard";
import BengaliAlert from "@/components/dashboard/BengaliAlert";

const DEMO_AGENT = "Karim Mia";

export default function AgentPage() {
  const [agent, setAgent] = useState<Agent | null>(null);
  const [liquidity, setLiquidity] = useState<LiquidityData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async (agentId: string) => {
    const [liq, al] = await Promise.all([
      api.analytics.liquidity(agentId),
      api.alerts.list({ status: "open" }),
    ]);
    setLiquidity(liq);
    setAlerts(al.filter((a) => a.agent_id === agentId).slice(0, 3));
  }, []);

  useEffect(() => {
    api.agents.list().then((agents) => {
      const karim = agents.find((a) => a.name === DEMO_AGENT) ?? agents[0];
      setAgent(karim);
      loadData(karim.id).finally(() => setLoading(false));
    });
  }, [loadData]);

  useWebSocket(
    useCallback((msg) => {
      if (msg.type === "new_alert" && agent && msg.data.agent_id === agent.id) {
        api.analytics.liquidity(agent.id).then(setLiquidity);
        api.alerts.list({ status: "open" }).then((al) =>
          setAlerts(al.filter((a) => a.agent_id === agent!.id).slice(0, 3))
        );
        if (typeof document !== "undefined") {
          document.title = "⚠ ALERT — Agent Dashboard";
          setTimeout(() => (document.title = "Agent Liquidity Dashboard"), 5000);
        }
      }
    }, [agent, loadData])
  );

  if (loading) return <div className="text-gray-400 py-20 text-center">Loading...</div>;
  if (!agent || !liquidity) return <div className="text-red-400 py-20 text-center">Failed to load</div>;

  return (
    <div className="space-y-6">
      {/* Agent header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{agent.name}</h1>
          <p className="text-gray-400 text-sm">{agent.area}</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500">Physical Cash</div>
          <div className="text-xl font-bold text-blue-400">৳{agent.physical_cash.toLocaleString()}</div>
        </div>
      </div>

      {/* ★ DECEPTIVE TOTAL — the core demo moment */}
      <DeceptiveTotal data={liquidity} physicalCash={agent.physical_cash} />

      {/* Provider cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {liquidity.providers.map((p) => (
          <ProviderCard key={p.provider} p={p} />
        ))}
      </div>

      {/* Active alerts with Bengali messages */}
      {alerts.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Active Alerts</h2>
          {alerts.map((a) => (
            <BengaliAlert key={a.id} alert={a} />
          ))}
        </div>
      )}

      {alerts.length === 0 && (
        <div className="text-center py-8 text-gray-600 text-sm">No active alerts</div>
      )}
    </div>
  );
}
