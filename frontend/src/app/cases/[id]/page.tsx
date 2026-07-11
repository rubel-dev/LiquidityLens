"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, type Case, type Alert } from "@/lib/api";
import CoordinationTimeline from "@/components/cases/CoordinationTimeline";
import EvidencePanel from "@/components/alerts/EvidencePanel";
import BengaliAlert from "@/components/dashboard/BengaliAlert";
import { clsx } from "clsx";

export default function CaseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [c, setC] = useState<Case | null>(null);
  const [alert, setAlert] = useState<Alert | null>(null);
  const [note, setNote] = useState("");
  const [author, setAuthor] = useState("Field Officer");
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    const caseData = await api.cases.get(id);
    setC(caseData);
    const alertData = await api.alerts.get(caseData.alert_id);
    setAlert(alertData);
  }, [id]);

  useEffect(() => { reload().finally(() => setLoading(false)); }, [reload]);

  const addNote = async () => {
    if (!note.trim()) return;
    await api.cases.addNote(id, note, author);
    setNote("");
    reload();
  };

  const acknowledge = async () => {
    await api.alerts.acknowledge(alert!.id, "Reviewed in Case Manager.", author);
    reload();
  };

  const escalate = async () => {
    await api.alerts.escalate(alert!.id, "Escalated after review.", author);
    reload();
  };

  const resolve = async () => {
    const resNote = note || "Reviewed and resolved.";
    await api.alerts.resolve(alert!.id, resNote, author);
    setNote("");
    reload();
  };

  const falsePositive = async () => {
    await api.alerts.falsePositive(alert!.id, note || "Normal demand pattern.", author);
    setNote("");
    reload();
  };

  if (loading) return <div className="text-gray-400 py-20 text-center">Loading...</div>;
  if (!c || !alert) return <div className="text-red-400 py-20 text-center">Not found</div>;

  return (
    <div className="space-y-6 max-w-3xl">
      <button onClick={() => router.back()} className="text-sm text-gray-400 hover:text-white transition">
        ← Back to Cases
      </button>

      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Case Detail</h1>
        <span className="text-xs font-mono text-gray-500">{c.id}</span>
      </div>

      {/* Coordination timeline */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Lifecycle</h2>
        <CoordinationTimeline c={c} />
        <div className="mt-3 text-xs text-gray-500">
          Owner: <span className="text-white font-medium">{c.assigned_to ?? "Unassigned"}</span>
          {" · "}Role: <span className="text-gray-300">{c.assigned_role ?? "—"}</span>
          {c.false_positive && <span className="ml-2 text-green-400 font-bold">★ Marked false positive</span>}
        </div>
      </div>

      {/* Bengali alert */}
      <BengaliAlert alert={alert} />

      {/* Evidence panel */}
      <EvidencePanel alert={alert} />

      {/* Action buttons */}
      {!c.resolved_at && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Actions</h2>
          <div className="flex flex-wrap gap-2">
            {!c.acknowledged_at && (
              <button onClick={acknowledge} className="px-4 py-2 bg-blue-700 hover:bg-blue-600 rounded text-sm text-white transition">
                Acknowledge
              </button>
            )}
            {!c.escalated_at && (
              <button onClick={escalate} className="px-4 py-2 bg-orange-700 hover:bg-orange-600 rounded text-sm text-white transition">
                Escalate to Risk Analyst
              </button>
            )}
            <button onClick={resolve} className="px-4 py-2 bg-green-700 hover:bg-green-600 rounded text-sm text-white transition">
              Resolve
            </button>
            <button onClick={falsePositive} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white transition">
              Mark False Positive
            </button>
          </div>
          <div className="flex gap-2">
            <select
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-200"
            >
              <option>Field Officer</option>
              <option>Risk Analyst</option>
              <option>Ops Manager</option>
            </select>
            <input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Add case note..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-200 placeholder:text-gray-600"
              onKeyDown={(e) => e.key === "Enter" && addNote()}
            />
            <button onClick={addNote} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-white transition">
              Add Note
            </button>
          </div>
        </div>
      )}

      {/* Audit trail */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Audit Trail</h2>
        {c.notes.length === 0 && <div className="text-gray-600 text-sm">No notes yet.</div>}
        {c.notes.map((n, i) => (
          <div key={i} className="border-l-2 border-gray-700 pl-3 text-sm space-y-0.5">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-gray-300">{n.author}</span>
              <span className="text-gray-600 text-xs">{new Date(n.timestamp).toLocaleString("en-BD")}</span>
            </div>
            <div className="text-gray-400">{n.text}</div>
          </div>
        ))}
        {c.resolution_note && (
          <div className="border-l-2 border-green-600 pl-3 text-sm text-green-300">
            Resolution: {c.resolution_note}
          </div>
        )}
      </div>
    </div>
  );
}
