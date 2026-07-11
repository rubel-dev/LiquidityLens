from pathlib import Path


def test_core_intelligence_has_no_llm_alert_api_or_financial_execution_dependencies() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for module in ("anomaly", "confidence")
        for path in Path(f"app/{module}").glob("*.py")
    )

    assert "openai" not in source
    assert "anthropic" not in source
    assert "app.alerts" not in source
    assert "app.api" not in source
    assert "execute_transfer" not in source
    assert "freeze_account" not in source
    assert "fraud detected" not in source
