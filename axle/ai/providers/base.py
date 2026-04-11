"""
AXLE OS — AI Provider Base Class

Defines the abstract interface that all AI providers must implement.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseProvider(ABC):
    """
    Abstract base class for AI providers.
    Each provider (Gemini, OpenRouter, OpenAI, Ollama) must implement these methods.
    """

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and ready to use."""
        ...

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """
        Generate a completion from the AI model.

        Args:
            system_prompt: The system instructions.
            user_prompt: The user's query or context.
            temperature: Creativity (0.0 = deterministic, 1.0 = creative).

        Returns:
            The model's text response.

        Raises:
            RuntimeError: If the API call fails.
        """
        ...

    def diagnose(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a diagnosis (uses generate with higher temperature)."""
        return self.generate(system_prompt, user_prompt, temperature=0.5)
