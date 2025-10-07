"""Helpers for reading prompt templates from the repository."""

from __future__ import annotations

import os
from pathlib import Path

_ENV_VAR = "TERMINAL_AI_PROMPTS_DIR"


def _resolve_prompts_dir() -> Path:
    env_override = os.getenv(_ENV_VAR)
    if env_override:
        override_path = Path(env_override).expanduser()
        if override_path.is_dir():
            return override_path
        raise FileNotFoundError(
            f"Environment variable {_ENV_VAR} points to missing directory: {override_path}"
        )

    for parent in Path(__file__).resolve().parents:
        candidate = parent / "prompts"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        "Unable to locate the `prompts/` directory. Set `TERMINAL_AI_PROMPTS_DIR` or run from repo root."
    )


def load_prompt(name: str, *, directory: Path | None = None) -> str:
    """Return the contents of the named prompt template."""

    prompts_dir = directory or _resolve_prompts_dir()
    path = prompts_dir / name
    if not path.is_file():
        raise FileNotFoundError(f"Prompt template '{name}' not found in {prompts_dir}")
    return path.read_text(encoding="utf-8")
