"""Agent responsible for translating natural language into shell commands."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from terminal_ai.io.language_model_client import LanguageModelClient

_DESTRUCTIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"rm\s+-rf\b"),
    re.compile(r"rm\s+-fr\b"),
    re.compile(r"mkfs\b"),
    re.compile(r"dd\s+if=", re.IGNORECASE),
    re.compile(r"shutdown\b"),
    re.compile(r"reboot\b"),
)


@dataclass(slots=True)
class CommandRequest:
    """Represents a natural language instruction to convert to a shell command."""

    instruction: str
    cwd: Path | None = None
    shell: str = "/bin/bash"
    temperature: float = 0.0
    allow_destructive: bool = False


@dataclass(slots=True)
class CommandSuggestion:
    """Structured suggestion returned by the language model."""

    command: str
    explanation: str
    requires_confirmation: bool
    follow_up: str

    def with_confirmation(self, required: bool) -> "CommandSuggestion":
        return CommandSuggestion(
            command=self.command,
            explanation=self.explanation,
            requires_confirmation=required,
            follow_up=self.follow_up,
        )


class CommandParsingError(RuntimeError):
    """Raised when the model response cannot be parsed into a suggestion."""


class TranslateCommandAgent:
    """High-level agent orchestrating prompt construction and parsing."""

    def __init__(
        self,
        model_client: LanguageModelClient,
        *,
        system_prompt_template: str,
    ) -> None:
        self._model_client = model_client
        self._system_prompt_template = system_prompt_template

    def suggest(self, request: CommandRequest) -> CommandSuggestion:
        system_prompt = self._system_prompt_template.format(
            shell=request.shell,
            cwd=(str(request.cwd) if request.cwd else "~"),
        )
        raw_response = self._model_client.complete(
            system_prompt=system_prompt,
            user_prompt=request.instruction.strip(),
            temperature=request.temperature,
        )
        suggestion = self._parse_response(raw_response)
        if suggestion.command and not request.allow_destructive:
            suggestion = self._enforce_confirmation(suggestion)
        return suggestion

    @staticmethod
    def _parse_response(response_text: str) -> CommandSuggestion:
        try:
            payload = _extract_json_object(response_text)
        except ValueError as exc:  # pragma: no cover - defensive path
            raise CommandParsingError(str(exc)) from exc

        command = str(payload.get("command", "")).strip()
        explanation = str(payload.get("explanation", "")).strip()
        follow_up = str(payload.get("follow_up", "")).strip()
        requires_confirmation = bool(payload.get("requires_confirmation", False))

        if not command and not follow_up:
            raise CommandParsingError("Model returned empty command and follow_up")

        return CommandSuggestion(
            command=command,
            explanation=explanation,
            requires_confirmation=requires_confirmation,
            follow_up=follow_up,
        )

    @staticmethod
    def _enforce_confirmation(suggestion: CommandSuggestion) -> CommandSuggestion:
        if any(pattern.search(suggestion.command) for pattern in _DESTRUCTIVE_PATTERNS):
            return suggestion.with_confirmation(True)
        return suggestion


def _extract_json_object(response_text: str) -> dict[str, object]:
    """Return the first JSON object found in the response text."""

    start = response_text.find("{")
    end = response_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Response did not contain JSON object")
    candidate = response_text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Unable to decode JSON: {exc}") from exc


__all__ = [
    "CommandRequest",
    "CommandSuggestion",
    "CommandParsingError",
    "TranslateCommandAgent",
]
