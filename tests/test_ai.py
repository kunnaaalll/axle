"""
Tests for axle.ai — Engine, Providers, and Prompts. (T-055)

All provider API calls are MOCKED — no real API keys needed.
Covers:
  - Provider base class contract
  - Each provider's is_available() logic
  - AIEngine provider selection and fallback
  - Plan generation with mocked responses
  - Diagnosis with mocked responses
  - Chat interface
  - JSON response parsing (valid, markdown-wrapped, invalid)
  - Fallback plan on parse failure
  - Prompt templates exist and have required placeholders
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from axle.ai.engine import AIEngine, PROVIDER_ORDER
from axle.ai.providers.base import BaseProvider
from axle.ai.providers.gemini_provider import GeminiProvider
from axle.ai.providers.openai_provider import OpenAIProvider
from axle.ai.providers.openrouter_provider import OpenRouterProvider
from axle.ai.providers.ollama_provider import OllamaProvider
from axle.ai.prompts import (
    DEPLOYMENT_PLAN_SYSTEM,
    DEPLOYMENT_PLAN_USER,
    DIAGNOSIS_SYSTEM,
    DIAGNOSIS_USER,
    CHATBOT_SYSTEM,
)
from axle.core.models import (
    DeploymentPlan,
    DeploymentStep,
    HealthMetrics,
    ProjectProfile,
    ServerProfile,
    StackType,
    FrameworkType,
    DatabaseType,
)


# =============================================================================
# Mock Provider
# =============================================================================

class MockProvider(BaseProvider):
    """A test provider that returns canned responses."""

    name = "mock"

    def __init__(self, available: bool = True, response: str = "mock response"):
        self._available = available
        self._response = response

    def is_available(self) -> bool:
        return self._available

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        return self._response


# Sample AI response for plan generation
SAMPLE_PLAN_JSON = json.dumps([
    {"id": "install-runtime", "name": "Install Node.js 20", "command": "nvm install 20 && nvm use 20", "plugin": "runtime", "depends_on": []},
    {"id": "install-deps", "name": "Install dependencies", "command": "npm install", "plugin": "runtime", "depends_on": ["install-runtime"]},
    {"id": "setup-db", "name": "Create PostgreSQL database", "command": "sudo -u postgres createdb myapp", "plugin": "database", "depends_on": []},
    {"id": "build", "name": "Build project", "command": "npm run build", "plugin": "runtime", "depends_on": ["install-deps"]},
    {"id": "create-service", "name": "Create systemd service", "command": "systemctl enable myapp", "plugin": "systemd", "depends_on": ["build"]},
    {"id": "setup-nginx", "name": "Configure Nginx", "command": "nginx -t && systemctl reload nginx", "plugin": "nginx", "depends_on": ["create-service"]},
])


# =============================================================================
# Provider Tests
# =============================================================================

class TestProviderBase:
    def test_base_class_is_abstract(self):
        with pytest.raises(TypeError):
            BaseProvider()

    def test_mock_provider_works(self):
        p = MockProvider(available=True, response="hello")
        assert p.is_available() is True
        assert p.generate("sys", "usr") == "hello"
        assert p.diagnose("sys", "usr") == "hello"


class TestGeminiProvider:
    def test_not_available_without_key(self):
        p = GeminiProvider(api_key=None)
        assert p.is_available() is False

    def test_available_with_key(self):
        p = GeminiProvider(api_key="test-key-123")
        assert p.is_available() is True

    def test_name(self):
        assert GeminiProvider.name == "gemini"


class TestOpenAIProvider:
    def test_not_available_without_key(self):
        p = OpenAIProvider(api_key=None)
        assert p.is_available() is False

    def test_available_with_key(self):
        p = OpenAIProvider(api_key="sk-test-123")
        assert p.is_available() is True

    def test_name(self):
        assert OpenAIProvider.name == "openai"

    def test_default_model(self):
        p = OpenAIProvider(api_key="key")
        assert p.model == "gpt-4o-mini"


class TestOpenRouterProvider:
    def test_not_available_without_key(self):
        p = OpenRouterProvider(api_key=None)
        assert p.is_available() is False

    def test_available_with_key(self):
        p = OpenRouterProvider(api_key="or-test-key")
        assert p.is_available() is True

    def test_name(self):
        assert OpenRouterProvider.name == "openrouter"

    def test_base_url(self):
        assert "openrouter.ai" in OpenRouterProvider.BASE_URL


class TestOllamaProvider:
    def test_not_available_when_offline(self):
        p = OllamaProvider(host="http://localhost:99999")
        assert p.is_available() is False

    def test_name(self):
        assert OllamaProvider.name == "ollama"


# =============================================================================
# AIEngine Tests
# =============================================================================

class TestAIEngine:

    def _engine_with_mock(self, response=SAMPLE_PLAN_JSON):
        """Create an engine with a mock provider injected."""
        engine = AIEngine()
        mock = MockProvider(available=True, response=response)
        engine.providers = {"mock": mock}
        return engine

    def test_provider_order(self):
        assert PROVIDER_ORDER == ["gemini", "openrouter", "openai", "ollama"]

    def test_no_providers_raises(self):
        engine = AIEngine()
        # Clear all providers to simulate no configuration
        engine.providers = {}
        with pytest.raises(RuntimeError, match="No AI provider available"):
            engine.get_active_provider()

    def test_preferred_provider_used(self):
        engine = AIEngine(gemini_api_key="key")
        engine.preferred_provider = "gemini"
        provider = engine.get_active_provider()
        assert provider.name == "gemini"

    def test_fallback_order(self):
        engine = AIEngine(openai_api_key="sk-123")
        # Gemini: no key, OpenRouter: no key, OpenAI: has key, Ollama: offline
        provider = engine.get_active_provider()
        assert provider.name == "openai"

    def test_list_available_providers(self):
        engine = AIEngine(gemini_api_key="key", openrouter_api_key="key2")
        available = engine.list_available_providers()
        assert "gemini" in available
        assert "openrouter" in available
        assert "openai" not in available

    def test_generate_plan(self):
        engine = self._engine_with_mock()
        profile = ProjectProfile(
            name="test-app", stack=StackType.NODEJS, framework=FrameworkType.EXPRESS,
            database=DatabaseType.POSTGRESQL, start_command="npm start",
        )
        plan = engine.generate_plan(profile)

        assert isinstance(plan, DeploymentPlan)
        assert plan.project_name == "test-app"
        assert len(plan.steps) == 6
        assert plan.steps[0].id == "install-runtime"

    def test_generate_plan_with_server(self):
        engine = self._engine_with_mock()
        profile = ProjectProfile(name="app", stack=StackType.PYTHON, start_command="python main.py")
        server = ServerProfile(cpu_count=4, ram_total_mb=8192)
        plan = engine.generate_plan(profile, server)

        assert plan.server.cpu_count == 4

    def test_plan_parsing_with_markdown_fences(self):
        wrapped = f"```json\n{SAMPLE_PLAN_JSON}\n```"
        engine = self._engine_with_mock(response=wrapped)
        profile = ProjectProfile(name="app", stack=StackType.NODEJS, start_command="npm start")
        plan = engine.generate_plan(profile)

        assert len(plan.steps) == 6

    def test_plan_parsing_invalid_json(self):
        engine = self._engine_with_mock(response="This is not JSON at all")
        profile = ProjectProfile(name="app", stack=StackType.NODEJS, start_command="npm start")
        plan = engine.generate_plan(profile)

        # Should return fallback plan
        assert len(plan.steps) == 1
        assert plan.steps[0].id == "manual-review"

    def test_diagnose(self):
        engine = self._engine_with_mock(response="CPU is high. Restart Nginx.")
        metrics = HealthMetrics(cpu_percent=95, ram_used_mb=3500, ram_total_mb=4096)
        result = engine.diagnose(metrics)

        assert "CPU" in result or "Nginx" in result

    def test_chat(self):
        engine = self._engine_with_mock(response="Your server is healthy.")
        result = engine.chat("How is my server?")
        assert "healthy" in result


# =============================================================================
# Prompt Tests
# =============================================================================

class TestPrompts:

    def test_deployment_system_prompt_exists(self):
        assert len(DEPLOYMENT_PLAN_SYSTEM) > 100
        assert "deployment plan" in DEPLOYMENT_PLAN_SYSTEM.lower()

    def test_deployment_user_template_placeholders(self):
        assert "{name}" in DEPLOYMENT_PLAN_USER
        assert "{stack}" in DEPLOYMENT_PLAN_USER
        assert "{framework}" in DEPLOYMENT_PLAN_USER
        assert "{database}" in DEPLOYMENT_PLAN_USER
        assert "{cpu_count}" in DEPLOYMENT_PLAN_USER

    def test_diagnosis_system_prompt_exists(self):
        assert len(DIAGNOSIS_SYSTEM) > 50
        assert "anomal" in DIAGNOSIS_SYSTEM.lower() or "issue" in DIAGNOSIS_SYSTEM.lower()

    def test_diagnosis_user_template_placeholders(self):
        assert "{cpu_percent}" in DIAGNOSIS_USER
        assert "{ram_used_mb}" in DIAGNOSIS_USER
        assert "{logs}" in DIAGNOSIS_USER

    def test_chatbot_system_prompt_exists(self):
        assert "AXLE" in CHATBOT_SYSTEM
