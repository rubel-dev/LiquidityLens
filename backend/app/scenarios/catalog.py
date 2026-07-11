from app.scenarios.schemas import ScenarioDefinition

PROVIDERS = (
    ("BK", "bKash simulated", "SIM-PROVIDER-BK"),
    ("NG", "Nagad simulated", "SIM-PROVIDER-NG"),
    ("RK", "Rocket simulated", "SIM-PROVIDER-RK"),
)

CANONICAL_SCENARIOS: dict[str, ScenarioDefinition] = {
    "normal_day": ScenarioDefinition(
        code="normal_day",
        name="Scenario A - Normal Day",
        purpose=(
            "Stable demand, balanced provider activity, sufficient shared cash, and complete feeds."
        ),
        expected_ground_truth=("normal",),
        review_required=False,
        anomaly_positive=False,
        false_positive_case=False,
    ),
    "eid_rush": ScenarioDefinition(
        code="eid_rush",
        name="Scenario B - Eid Rush",
        purpose="Legitimate seasonal high demand with broad account distribution.",
        expected_ground_truth=("legitimate_demand_spike",),
        review_required=False,
        anomaly_positive=False,
        false_positive_case=True,
    ),
    "hidden_provider_shortage": ScenarioDefinition(
        code="hidden_provider_shortage",
        name="Scenario C - Hidden Provider Shortage",
        purpose=(
            "Total outlet value appears healthy while one provider e-money balance approaches "
            "depletion."
        ),
        expected_ground_truth=("provider_liquidity_pressure",),
        review_required=True,
        anomaly_positive=False,
        false_positive_case=False,
    ),
    "shared_cash_crisis": ScenarioDefinition(
        code="shared_cash_crisis",
        name="Scenario D - Shared Cash Crisis",
        purpose=(
            "Cash-out demand across providers makes shared physical cash the limiting resource."
        ),
        expected_ground_truth=("shared_cash_pressure",),
        review_required=True,
        anomaly_positive=False,
        false_positive_case=False,
    ),
    "liquidity_pressure_unusual_activity": ScenarioDefinition(
        code="liquidity_pressure_unusual_activity",
        name="Scenario E - Liquidity Pressure with Unusual Activity",
        purpose=(
            "Rapid cash-out increase with repeated amounts and concentrated synthetic accounts."
        ),
        expected_ground_truth=(
            "provider_liquidity_pressure",
            "unusual_repeated_amounts",
            "unusual_velocity",
            "account_concentration",
        ),
        review_required=True,
        anomaly_positive=True,
        false_positive_case=False,
    ),
    "salary_day_legitimate_spike": ScenarioDefinition(
        code="salary_day_legitimate_spike",
        name="Scenario F - Salary-Day Legitimate Spike",
        purpose="High but expected demand with broad account diversity.",
        expected_ground_truth=("legitimate_demand_spike",),
        review_required=False,
        anomaly_positive=False,
        false_positive_case=True,
    ),
    "delayed_feed": ScenarioDefinition(
        code="delayed_feed",
        name="Scenario G - Delayed Feed",
        purpose="One provider feed timestamp becomes delayed and must not be treated as current.",
        expected_ground_truth=("delayed_feed", "stale_feed"),
        review_required=True,
        anomaly_positive=False,
        false_positive_case=False,
    ),
    "missing_feed": ScenarioDefinition(
        code="missing_feed",
        name="Scenario H - Missing Feed",
        purpose="One provider feed is unavailable and missing balance remains unknown.",
        expected_ground_truth=("missing_feed",),
        review_required=True,
        anomaly_positive=False,
        false_positive_case=False,
    ),
    "conflicting_balance": ScenarioDefinition(
        code="conflicting_balance",
        name="Scenario I - Conflicting Balance",
        purpose="Transaction totals and reported provider balance disagree intentionally.",
        expected_ground_truth=("conflicting_balance",),
        review_required=True,
        anomaly_positive=False,
        false_positive_case=False,
    ),
    "agent_unavailable": ScenarioDefinition(
        code="agent_unavailable",
        name="Scenario J - Agent Unavailable",
        purpose="Agent or outlet availability changes for future coordination modules.",
        expected_ground_truth=("agent_unavailable",),
        review_required=True,
        anomaly_positive=False,
        false_positive_case=False,
    ),
}


def get_scenario(code: str) -> ScenarioDefinition:
    return CANONICAL_SCENARIOS[code]
