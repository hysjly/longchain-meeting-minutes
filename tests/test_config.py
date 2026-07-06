import pytest

from meeting_minutes_agent.config import load_settings


def test_load_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("MIMO_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="MIMO_API_KEY"):
        load_settings()


def test_load_settings_rejects_placeholder_api_key(monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "replace-with-your-token-plan-key")

    with pytest.raises(ValueError, match="replace"):
        load_settings()


def test_load_settings_uses_mimo_defaults(monkeypatch):
    monkeypatch.setenv("MIMO_API_KEY", "test-key")
    monkeypatch.delenv("MIMO_BASE_URL", raising=False)
    monkeypatch.delenv("MIMO_MODEL", raising=False)

    settings = load_settings()

    assert settings.api_key == "test-key"
    assert settings.base_url == "https://token-plan-cn.xiaomimimo.com/v1"
    assert settings.model == "mimo-v2.5-pro"
    assert settings.provider == "openai_compatible"
