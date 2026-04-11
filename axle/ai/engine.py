"""
AXLE OS — AI Engine (T-046 to T-048, T-054)

Central AI orchestrator that:
  - Manages multiple AI providers (Gemini, OpenRouter, OpenAI, Ollama)
  - Routes requests to the configured or first-available provider
  - Implements automatic fallback: Gemini → OpenRouter → OpenAI → Ollama
  - Provides two core interfaces:
      1. generate_plan() — turn a ProjectProfile into a DeploymentPlan
      2. diagnose() — analyze server health from metrics and logs
"""
import json
import logging
from typing import List, Optional

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
)

logger = logging.getLogger("axle.ai")


# Provider priority order for fallback
PROVIDER_ORDER = ["gemini", "openrouter", "openai", "ollama"]


class AIEngine:
    """
    Central AI engine with multi-provider support and automatic fallback.

    Usage:
        engine = AIEngine(gemini_api_key="...", openrouter_api_key="...")
        plan = engine.generate_plan(profile, server)
        diagnosis = engine.diagnose(metrics, logs)
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ):
        self.providers: dict[str, BaseProvider] = {
            "gemini": GeminiProvider(api_key=gemini_api_key),
            "openrouter": OpenRouterProvider(api_key=openrouter_api_key),
            "openai": OpenAIProvider(api_key=openai_api_key),
            "ollama": OllamaProvider(),
        }
        self.preferred_provider = preferred_provider

    def get_active_provider(self) -> BaseProvider:
        """
        Get the best available provider. (T-054)

        Priority:
          1. User's preferred provider (if set and available)
          2. Fallback order: Gemini → OpenRouter → OpenAI → Ollama
        """
        # Try preferred provider first
        if self.preferred_provider and self.preferred_provider in self.providers:
            provider = self.providers[self.preferred_provider]
            if provider.is_available():
                return provider
            logger.warning(
                f"Preferred provider '{self.preferred_provider}' is not available, "
                "falling back..."
            )

        # Fallback chain
        for name in PROVIDER_ORDER:
            if name not in self.providers:
                continue
            provider = self.providers[name]
            if provider.is_available():
                logger.info(f"Using AI provider: {name}")
                return provider

        # Also check any non-standard providers (e.g. "mock" in tests)
        for name, provider in self.providers.items():
            if provider.is_available():
                logger.info(f"Using AI provider: {name}")
                return provider

        raise RuntimeError(
            "No AI provider available. Configure at least one:\n"
            "  - Set GEMINI_API_KEY for Google Gemini\n"
            "  - Set OPENROUTER_API_KEY for OpenRouter\n"
            "  - Set OPENAI_API_KEY for OpenAI\n"
            "  - Install Ollama for local inference"
        )

    def list_available_providers(self) -> List[str]:
        """Return names of all currently available providers."""
        return [name for name, p in self.providers.items() if p.is_available()]

    # ==========================================================================
    # Core Interface: Deployment Planning (T-047)
    # ==========================================================================

    def generate_plan(
        self,
        profile: ProjectProfile,
        server: Optional[ServerProfile] = None,
    ) -> DeploymentPlan:
        """
        Generate a deployment plan by sending the project profile to the AI.

        Args:
            profile: The scanned project profile.
            server: The target server profile (defaults if not provided).

        Returns:
            A DeploymentPlan with ordered steps.
        """
        if server is None:
            server = ServerProfile()

        provider = self.get_active_provider()

        # Build the user prompt from templates
        user_prompt = DEPLOYMENT_PLAN_USER.format(
            name=profile.name,
            stack=profile.stack.value,
            framework=profile.framework.value,
            version=profile.version or "latest",
            database=profile.database.value,
            build_command=profile.build_command or "none",
            start_command=profile.start_command,
            port=profile.port,
            has_frontend=profile.has_frontend,
            has_backend=profile.has_backend,
            env_vars=", ".join(profile.env_vars) if profile.env_vars else "none",
            os_name=server.os_name,
            cpu_count=server.cpu_count,
            ram_total_mb=server.ram_total_mb,
            disk_total_gb=server.disk_total_gb,
        )

        # Call the AI
        raw_response = provider.generate(DEPLOYMENT_PLAN_SYSTEM, user_prompt)

        # Parse the response into deployment steps
        steps = self._parse_plan_response(raw_response)

        return DeploymentPlan(
            project_name=profile.name,
            profile=profile,
            server=server,
            steps=steps,
        )

    # ==========================================================================
    # Core Interface: Diagnosis (T-048)
    # ==========================================================================

    def diagnose(
        self,
        metrics: HealthMetrics,
        logs: str = "",
        profile: Optional[ProjectProfile] = None,
    ) -> str:
        """
        Diagnose server issues using AI analysis of metrics and logs.

        Args:
            metrics: Current health metrics snapshot.
            logs: Recent application log lines.
            profile: The deployed project profile (optional).

        Returns:
            Human-readable diagnosis and recommendations.
        """
        provider = self.get_active_provider()

        user_prompt = DIAGNOSIS_USER.format(
            cpu_percent=metrics.cpu_percent,
            ram_used_mb=metrics.ram_used_mb,
            ram_total_mb=metrics.ram_total_mb,
            ram_percent=f"{metrics.ram_percent:.1f}",
            disk_used_gb=metrics.disk_used_gb,
            disk_total_gb=metrics.disk_total_gb,
            disk_percent=f"{metrics.disk_percent:.1f}",
            process_running=metrics.process_running,
            http_status_code=metrics.http_status_code or "N/A",
            http_response_time_ms=metrics.http_response_time_ms or "N/A",
            db_connections_active=metrics.db_connections_active or "N/A",
            ssl_days_remaining=metrics.ssl_days_remaining or "N/A",
            stack=profile.stack.value if profile else "unknown",
            framework=profile.framework.value if profile else "unknown",
            database=profile.database.value if profile else "none",
            logs=logs or "(no recent logs)",
        )

        return provider.diagnose(DIAGNOSIS_SYSTEM, user_prompt)

    # ==========================================================================
    # Chat Interface
    # ==========================================================================

    def chat(self, question: str, context: str = "") -> str:
        """Ask the AI a question about the server."""
        provider = self.get_active_provider()
        user_prompt = f"{context}\n\nUser question: {question}" if context else question
        return provider.generate(CHATBOT_SYSTEM, user_prompt, temperature=0.5)

    # ==========================================================================
    # Internal Helpers
    # ==========================================================================

    def _parse_plan_response(self, raw: str) -> List[DeploymentStep]:
        """Parse the AI's JSON response into DeploymentStep objects."""
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last lines (```json and ```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            steps_data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {cleaned[:200]}")
            # Return a minimal fallback plan
            return self._fallback_plan()

        steps = []
        for s in steps_data:
            steps.append(DeploymentStep(
                id=s.get("id", f"step-{len(steps)+1}"),
                name=s.get("name", "Unknown step"),
                command=s.get("command", "echo 'no command'"),
                plugin=s.get("plugin"),
                depends_on=s.get("depends_on", []),
            ))

        return steps

    def _fallback_plan(self) -> List[DeploymentStep]:
        """Return a minimal deployment plan when AI response parsing fails."""
        return [
            DeploymentStep(
                id="manual-review",
                name="Manual Review Required",
                command="echo 'AI plan parsing failed — manual deployment required'",
                plugin=None,
            )
        ]
