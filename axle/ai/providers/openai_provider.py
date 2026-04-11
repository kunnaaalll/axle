"""
AXLE OS — OpenAI GPT Provider (T-050)

Uses the openai SDK to generate deployments and diagnoses.
"""
from typing import Optional
from axle.ai.providers.base import BaseProvider


class OpenAIProvider(BaseProvider):
    """OpenAI GPT provider."""

    name = "openai"

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.api_key)

    def _get_client(self):
        """Lazy-initialize the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise RuntimeError(
                    "openai package not installed. "
                    "Install with: pip install openai"
                )
        return self._client

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Generate a response using OpenAI."""
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
