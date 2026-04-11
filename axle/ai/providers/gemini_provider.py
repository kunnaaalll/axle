"""
AXLE OS — Google Gemini AI Provider (T-049)

Uses the google-generativeai SDK to generate deployments and diagnoses.
"""
import json
from typing import Optional
from axle.ai.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini AI provider."""

    name = "gemini"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._model = None

    def is_available(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.api_key)

    def _get_model(self):
        """Lazy-initialize the Gemini client."""
        if self._model is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel("gemini-2.0-flash")
            except ImportError:
                raise RuntimeError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._model

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Generate a response using Gemini."""
        model = self._get_model()
        import google.generativeai as genai

        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            ),
        )
        return response.text
