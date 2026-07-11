from pathlib import Path


def test_liquidity_module_contains_no_unsafe_execution_or_llm_dependencies() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8").lower() for path in Path("app/liquidity").glob("*.py")
    )

    assert "openai" not in source
    assert "anthropic" not in source
    assert "execute_transfer" not in source
    assert "freeze_account" not in source
    assert "block_account" not in source
    assert "fraud detected" not in source
