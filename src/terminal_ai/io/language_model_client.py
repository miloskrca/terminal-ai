"""Language model client abstractions used by Terminal AI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

try:
    import httpx
except ModuleNotFoundError:  # pragma: no cover - dependency is optional in tests
    httpx = None  # type: ignore[assignment]


class LanguageModelClient(Protocol):
    """Protocol describing the expected language model client behaviour."""

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        """Return the text completion for the provided prompts."""


@dataclass(slots=True)
class OpenAIChatClient:
    """Minimal synchronous client using OpenAI's chat completions API."""

    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if httpx is None:  # pragma: no cover - exercised only when dependency missing
            raise RuntimeError(
                "httpx is required for OpenAIChatClient. Install dependencies with"
                " `pip install -r requirements.txt` or add httpx manually."
            )

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        response = httpx.post(  # type: ignore[operator]
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        try:
            message = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:  # pragma: no cover - API contract change
            raise RuntimeError("Unexpected response from OpenAI API") from exc
        return message.strip()
