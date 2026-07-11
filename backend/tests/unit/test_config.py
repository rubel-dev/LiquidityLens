from app.core.config import Settings, get_settings


def test_config_loading_from_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_NAME", "liquiditylens-test-api")
    monkeypatch.setenv("LLM_EXPLANATION_ENABLED", "false")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.app_env == "test"
    assert settings.app_name == "liquiditylens-test-api"
    assert settings.llm_explanation_enabled is False

    get_settings.cache_clear()


def test_llm_disabled_by_default():
    settings = Settings()

    assert settings.llm_explanation_enabled is False
    assert settings.llm_explanation_provider == "none"
