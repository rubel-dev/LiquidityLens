import re
from datetime import UTC, datetime

from app.scenarios.catalog import CANONICAL_SCENARIOS
from app.scenarios.generators import generate_scenario
from app.scenarios.schemas import ScenarioConfig

PHONE_LIKE_RE = re.compile(r"(\+?880|01[3-9])\d{8,}")
FORBIDDEN_WORDS = {"fraud", "criminal", "guilty", "password", "otp", "pin", "freeze", "block"}


def test_generated_scenario_data_has_no_phone_like_identifiers_or_credentials():
    config = ScenarioConfig(start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC))
    for index, scenario_code in enumerate(CANONICAL_SCENARIOS, start=1):
        scenario = generate_scenario(scenario_code, index, f"SIM-RUN-{index:06d}", config)
        payload = str(scenario)

        assert PHONE_LIKE_RE.search(payload) is None
        assert not (FORBIDDEN_WORDS & set(payload.lower().replace("_", " ").split()))


def test_generated_scenarios_do_not_model_provider_balance_merging():
    config = ScenarioConfig(start_timestamp=datetime(2026, 7, 11, 9, 0, tzinfo=UTC))
    scenario = generate_scenario("hidden_provider_shortage", 1001, "SIM-RUN-000001", config)

    assert all(snapshot.provider_code is not None for snapshot in scenario.provider_balances)
    assert all(snapshot.provider_code is None for snapshot in scenario.shared_cash)
    assert "transfer" not in str(scenario.transactions).lower()
