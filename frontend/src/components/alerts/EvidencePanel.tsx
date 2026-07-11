"use client";
import type { Alert } from "@/lib/api";

export default function EvidencePanel({ alert }: { alert: Alert }) {
  if (!alert.evidence) return null;
  const ev = alert.evidence as Record<string, unknown>;

  return (
    <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-4">
      <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider">Evidence</h3>

      {/* Liquidity evidence */}
      {alert.type === "liquidity" && (
        <div className="grid grid-cols-2 gap-3 text-sm">
          {ev.balance != null && (
            <div className="bg-gray-800 rounded p-3">
              <div className="text-xs text-gray-400">Balance</div>
              <div className="font-bold text-white">৳{Number(ev.balance).toLocaleString()}</div>
            </div>
          )}
          {ev.rate_per_minute != null && (
            <div className="bg-gray-800 rounded p-3">
              <div className="text-xs text-gray-400">Outflow Rate</div>
              <div className="font-bold text-red-400">৳{(Number(ev.rate_per_minute) * 60).toFixed(0)}/hr</div>
            </div>
          )}
          {ev.recommended_topup != null && (
            <div className="bg-yellow-900/50 border border-yellow-700 rounded p-3 col-span-2">
              <div className="text-xs text-yellow-400">Recommended Top-up</div>
              <div className="font-bold text-yellow-200">৳{Number(ev.recommended_topup).toLocaleString()}</div>
            </div>
          )}
        </div>
      )}

      {/* Anomaly evidence */}
      {alert.type === "anomaly" && (
        <div className="space-y-3">
          {/* Velocity */}
          {ev.velocity && (() => { const v = ev.velocity as Record<string, unknown>; return v.flagged ? (
            <div className="bg-gray-800 rounded p-3 text-sm">
              <div className="text-xs text-orange-400 font-bold mb-1">VELOCITY</div>
              <div className="text-gray-200">{Number(v.count)} transactions in 15 min <span className="text-red-400">(threshold: {Number(v.threshold)})</span></div>
            </div>
          ) : null; })()}

          {/* Clustering */}
          {ev.clustering && (() => { const c = ev.clustering as Record<string, unknown>; return c.flagged ? (
            <div className="bg-gray-800 rounded p-3 text-sm">
              <div className="text-xs text-orange-400 font-bold mb-1">AMOUNT CLUSTERING</div>
              <div className="text-gray-200">{Math.round(Number(c.ratio) * 100)}% of amounts in range <span className="font-bold text-yellow-300">{c.range as string}</span></div>
              {Array.isArray(c.amounts) && c.amounts.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {(c.amounts as number[]).slice(0, 8).map((a, i) => (
                    <span key={i} className="text-xs bg-gray-700 px-2 py-0.5 rounded">৳{a.toLocaleString()}</span>
                  ))}
                </div>
              )}
            </div>
          ) : null; })()}

          {/* Concentration */}
          {ev.concentration && (() => { const c = ev.concentration as Record<string, unknown>; return c.flagged ? (
            <div className="bg-gray-800 rounded p-3 text-sm">
              <div className="text-xs text-orange-400 font-bold mb-1">ACCOUNT CONCENTRATION</div>
              <div className="text-gray-200">Only <span className="font-bold text-red-400">{Number(c.unique_accounts)} unique accounts</span> in {Number(c.total_transactions)} transactions (ratio: {Number(c.ratio).toFixed(2)})</div>
              {Array.isArray(c.top_accounts) && (c.top_accounts as {account_id:string;count:number;total_amount:number}[]).slice(0, 3).map((a) => (
                <div key={a.account_id} className="mt-1 text-xs text-gray-400">{a.account_id} — {a.count} txns, ৳{a.total_amount.toLocaleString()}</div>
              ))}
            </div>
          ) : null; })()}
        </div>
      )}

      {/* Confidence + disclaimer */}
      <div className="border-t border-gray-700 pt-3 text-xs text-gray-500">
        Confidence: {Math.round((alert.confidence ?? 0) * 100)}% · Uncertainty: {alert.uncertainty}
        <div className="mt-1 text-yellow-700">
          This is advisory only. Do not take action without human review.
        </div>
      </div>
    </div>
  );
}
