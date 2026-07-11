from pathlib import Path


def test_operations_layer_has_no_llm_or_financial_execution_dependencies() -> None:
    root = Path(__file__).resolve().parents[2] / "app"
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for folder in ("alerts", "cases", "api")
        for path in (root / folder).rglob("*.py")
    ).lower()

    assert "import openai" not in sources
    assert "import anthropic" not in sources
    assert "execute_transfer" not in sources
    assert "execute_refill" not in sources
    assert "automatic blocking" not in sources
    assert "fraud detected" not in sources
