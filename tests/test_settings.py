
from app.core.settings import Settings


def test_settings_default_values():
    config = Settings(_env_file=None)

    assert config.app_name == "Personal Assistant"
    assert config.app_env == "development"
    assert config.app_debug is True
    assert config.database_url == (
        "postgresql://user:password@localhost:5432/personal_assistant"
    )


def test_settings_environment_variables(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Assistente de Teste")
    monkeypatch.setenv("APP_ENV", "testing")
    monkeypatch.setenv("APP_DEBUG", "false")

    config = Settings(_env_file=None)

    assert config.app_name == "Assistente de Teste"
    assert config.app_env == "testing"
    assert config.app_debug is False