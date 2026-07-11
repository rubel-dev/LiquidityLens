from app.providers.simulated import SimulatedProviderAdapter

SUPPORTED_PROVIDER_CODES = ("SIM-PROVIDER-BK", "SIM-PROVIDER-NG", "SIM-PROVIDER-RK")


def simulated_provider_registry() -> dict[str, SimulatedProviderAdapter]:
    return {code: SimulatedProviderAdapter(code) for code in SUPPORTED_PROVIDER_CODES}


def get_simulated_adapter(provider_code: str) -> SimulatedProviderAdapter:
    normalized = (
        provider_code
        if provider_code.startswith("SIM-PROVIDER-")
        else f"SIM-PROVIDER-{provider_code}"
    )
    return simulated_provider_registry()[normalized]
