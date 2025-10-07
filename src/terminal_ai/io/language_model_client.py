"""Language model client abstractions used by Terminal AI."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


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
        ...


@dataclass(slots=True)
class OpenAIChatClient:
    """Minimal synchronous client using OpenAI's chat completions API."""

    model: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout: float = 30.0

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
    ) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:  # type: ignore[arg-type]
                raw_body = response.read()
        except urllib.error.HTTPError as exc:  # pragma: no cover - network path
            detail = exc.read().decode("utf-8", "ignore") if hasattr(exc, "read") else ""
            raise RuntimeError(
                f"OpenAI API error: {exc.code} {exc.reason}. {detail}".strip()
            ) from exc
        except urllib.error.URLError as exc:  # pragma: no cover - network path
            raise RuntimeError(f"Failed to reach OpenAI API: {exc.reason if hasattr(exc, 'reason') else exc}") from exc

        data = json.loads(raw_body.decode("utf-8"))

        try:
            raw_message = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:  # pragma: no cover - API contract change
            raise RuntimeError("Unexpected response from OpenAI API") from exc

        if not isinstance(raw_message, str):
            raise RuntimeError("OpenAI API returned non-text content")
        return raw_message.strip()
