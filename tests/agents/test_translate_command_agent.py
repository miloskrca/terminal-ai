from __future__ import annotations

from pathlib import Path

import pytest

from terminal_ai.agents.translate_command_agent import (
    CommandParsingError,
    CommandRequest,
    TranslateCommandAgent,
)


class _StubClient:
    def __init__(self, response: str) -> None:
        self._response = response

    def complete(self, *, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        assert "shell" in system_prompt.lower()
        assert user_prompt
        return self._response


def _agent(response: str) -> TranslateCommandAgent:
    template = "Shell: {shell} | CWD: {cwd}"
    return TranslateCommandAgent(model_client=_StubClient(response), system_prompt_template=template)


def test_returns_suggestion_with_command() -> None:
    agent = _agent(
        '{"command": "ls -la", "explanation": "List files", "requires_confirmation": false, "follow_up": ""}'
    )
    request = CommandRequest(instruction="list files", cwd=Path("/tmp"))
    suggestion = agent.suggest(request)
    assert suggestion.command == "ls -la"
    assert suggestion.explanation == "List files"
    assert suggestion.follow_up == ""
    assert suggestion.requires_confirmation is False


def test_enforces_confirmation_for_destructive_command() -> None:
    agent = _agent(
        '{"command": "rm -rf ~/Downloads/cache", "explanation": "Remove cache", "requires_confirmation": false, "follow_up": ""}'
    )
    suggestion = agent.suggest(CommandRequest(instruction="clear cache"))
    assert suggestion.requires_confirmation is True


def test_allows_follow_up_only_payload() -> None:
    agent = _agent(
        '{"command": "", "explanation": "", "requires_confirmation": false, "follow_up": "Which project?"}'
    )
    suggestion = agent.suggest(CommandRequest(instruction="deploy"))
    assert suggestion.command == ""
    assert suggestion.follow_up == "Which project?"


@pytest.mark.parametrize("response", ["No JSON here", "[invalid json]"])
def test_raises_when_response_missing_json(response: str) -> None:
    agent = _agent(response)
    with pytest.raises(CommandParsingError):
        agent.suggest(CommandRequest(instruction="noop"))
