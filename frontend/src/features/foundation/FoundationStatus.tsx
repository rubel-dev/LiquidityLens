"use client";

import { useEffect, useState } from "react";

import { getApiHealth } from "@/lib/api";

type ApiStatus = "checking" | "ok" | "unavailable";

export function FoundationStatus() {
  const [status, setStatus] = useState<ApiStatus>("checking");

  useEffect(() => {
    let mounted = true;

    getApiHealth()
      .then((health) => {
        if (mounted) {
          setStatus(health.status === "ok" ? "ok" : "unavailable");
        }
      })
      .catch(() => {
        if (mounted) {
          setStatus("unavailable");
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  const label =
    status === "ok" ? "OK" : status === "checking" ? "Checking" : "Unavailable";

  return (
    <div className="foundation-panel status-row">
      <span className="status-label">API connectivity</span>
      <span
        className={`status-value ${status === "ok" ? "status-ok" : "status-unavailable"}`}
        role="status"
      >
        {label}
      </span>
    </div>
  );
}
