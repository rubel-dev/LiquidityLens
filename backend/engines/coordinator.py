"""Alert routing — assigns owner role and name based on alert type and severity."""
from dataclasses import dataclass


ROUTING_TABLE = {
    ("liquidity", "critical"): ("field_officer",    "bKash Field Officer"),
    ("liquidity", "high"):     ("field_officer",    "Field Officer"),
    ("liquidity", "medium"):   ("ops_manager",      "Operations Manager"),
    ("liquidity", "low"):      ("agent",            "Agent Self-Service"),
    ("anomaly",   "critical"): ("risk_analyst",     "Risk Analyst"),
    ("anomaly",   "high"):     ("risk_analyst",     "Risk Analyst"),
    ("anomaly",   "medium"):   ("field_officer",    "Field Officer"),
    ("anomaly",   "low"):      ("field_officer",    "Field Officer"),
    ("data_quality", "high"):  ("ops_manager",      "Operations Manager"),
    ("data_quality", "medium"):("ops_manager",      "Operations Manager"),
    ("data_quality", "low"):   ("agent",            "Agent Self-Service"),
}


@dataclass
class RoutingDecision:
    owner_role: str
    owner_name: str
    recommended_action: str


RECOMMENDED_ACTIONS = {
    "field_officer": "Contact agent and arrange balance top-up through approved channels.",
    "risk_analyst":  "Review transaction evidence before taking any action. Do not accuse.",
    "ops_manager":   "Monitor situation and coordinate between provider teams.",
    "agent":         "Check your balance and contact your field officer if needed.",
}


def route(alert_type: str, severity: str, provider: str | None = None) -> RoutingDecision:
    key = (alert_type, severity)
    role, name = ROUTING_TABLE.get(key, ("ops_manager", "Operations Manager"))

    if provider and role == "field_officer":
        name = f"{provider.capitalize()} Field Officer"

    return RoutingDecision(
        owner_role=role,
        owner_name=name,
        recommended_action=RECOMMENDED_ACTIONS.get(role, "Review and take appropriate action."),
    )


def determine_severity(eta_minutes: int | None, alert_type: str) -> str:
    if alert_type == "data_quality":
        return "medium"
    if eta_minutes is None:
        return "low"
    if eta_minutes < 20:
        return "critical"
    if eta_minutes < 45:
        return "high"
    if eta_minutes < 90:
        return "medium"
    return "low"
