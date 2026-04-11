"""
Tests for axle.config.settings — Pydantic settings management.

Verifies:
  - Default values are loaded correctly
  - Environment variables override defaults
  - Settings singleton is accessible
"""
import pytest
import os


class TestSettings:
    """Test the Settings configuration class."""

    def test_default_dashboard_port(self):
        from axle.config.settings import Settings
        s = Settings()
        assert s.axle_dashboard_port == 4000

    def test_default_db_path(self):
        from axle.config.settings import Settings
        s = Settings()
        assert s.axle_db_path == "/var/lib/axle/axle.db"

    def test_default_vault_path(self):
        from axle.config.settings import Settings
        s = Settings()
        assert s.axle_vault_path == "/var/lib/axle/vault.enc"

    def test_api_keys_default_to_none(self):
        from axle.config.settings import Settings
        s = Settings()
        assert s.openai_api_key is None
        assert s.gemini_api_key is None
        assert s.openrouter_api_key is None

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("AXLE_DASHBOARD_PORT", "9000")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
        from axle.config.settings import Settings
        s = Settings()
        assert s.axle_dashboard_port == 9000
        assert s.openai_api_key == "sk-test-123"

    def test_settings_singleton_exists(self):
        from axle.config.settings import settings
        assert settings is not None
        assert hasattr(settings, "axle_dashboard_port")
