import re

SAMPLE_SYNTHETIC_IDS = [
    "SIM-USER-0001",
    "SIM-AGENT-0001",
    "SIM-CUST-0001",
    "SIM-TXN-000001",
    "SIM-SCENARIO-001",
]

PHONE_LIKE_RE = re.compile(r"^(\+?880|01)\d{8,}$")


def test_sample_identifiers_are_synthetic_and_not_phone_like():
    for value in SAMPLE_SYNTHETIC_IDS:
        assert value.startswith("SIM-")
        assert not PHONE_LIKE_RE.match(value)

