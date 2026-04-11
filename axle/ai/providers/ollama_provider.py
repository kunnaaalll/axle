"""
AXLE OS — Ollama Provider (T-051)

Uses the local Ollama HTTP API for fully offline AI.
No API key required — just needs Ollama installed on the server.
"""
import json
from typing import Optional
from axle.ai.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    """Local Ollama AI provider (no API key required)."""

    name = "ollama"

    def __init__(self, model: str = "llama3.1", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def is_available(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            import urllib.request
            req = urllib.request.Request(f"{self.host}/api/tags")
            urllib.request.urlopen(req, timeout=3)
            return True
        except Exception:
            return False

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Generate a response using local Ollama."""
        import urllib.request

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
        )

        response = urllib.request.urlopen(req, timeout=120)
        result = json.loads(response.read().decode("utf-8"))
        return result.get("message", {}).get("content", "")
