"use client";
import { clsx } from "clsx";
import type { Case } from "@/lib/api";

const STEPS = [
  { key: "created_at",      label: "Alert Fired",  color: "bg-blue-500" },
  { key: "acknowledged_at", label: "Acknowledged", color: "bg-yellow-500" },
  { key: "escalated_at",    label: "Escalated",    color: "bg-orange-500" },
  { key: "resolved_at",     label: "Resolved",     color: "bg-green-500" },
];

function fmt(iso: string | null) {
  if (!iso) return null;
  const d = new Date(iso);
  return d.toLocaleTimeString("en-BD", { hour: "2-digit", minute: "2-digit" });
}

export default function CoordinationTimeline({ c }: { c: Case }) {
  return (
    <div className="relative">
      <div className="flex items-start gap-0">
        {STEPS.map((step, i) => {
          const ts = (c as Record<string, string | null>)[step.key];
          const done = !!ts;
          const isLast = i === STEPS.length - 1;
          return (
            <div key={step.key} className="flex-1 flex flex-col items-center">
              <div className="flex items-center w-full">
                <div className={clsx("w-5 h-5 rounded-full border-2 flex-shrink-0 z-10", done ? `${step.color} border-transparent` : "bg-gray-800 border-gray-600")} />
                {!isLast && <div className={clsx("flex-1 h-0.5", done ? "bg-blue-600" : "bg-gray-700")} />}
              </div>
              <div className="text-xs text-center mt-1 px-1">
                <div className={clsx("font-medium", done ? "text-white" : "text-gray-600")}>{step.label}</div>
                {done && <div className="text-gray-500">{fmt(ts)}</div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
