from pathlib import Path

FORBIDDEN = {"fraud", "criminal", "guilty", "password", "otp", "pin", "freeze", "block"}


def test_validation_module_does_not_declare_wrongdoing_or_financial_actions():
    validation_files = Path("app/validation").glob("*.py")
    provider_files = Path("app/providers").glob("*.py")
    paths = [*validation_files, *provider_files]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)

    assert not (FORBIDDEN & set(text.replace("_", " ").split()))
    assert "transfer balances" not in text
