"""Utilities for executing shell commands safely."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(slots=True)
class CommandExecutionResult:
    """Represents the outcome of a shell command execution."""

    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0


class CommandRunner:
    """Simple wrapper around ``subprocess.run`` with sensible defaults."""

    def __init__(self, shell: str = "/bin/bash", dry_run: bool = False) -> None:
        self.shell = shell
        self.dry_run = dry_run

    def execute(
        self,
        command: str,
        *,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> CommandExecutionResult:
        if self.dry_run:
            return CommandExecutionResult(command=command, returncode=0, stdout="", stderr="")

        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            executable=self.shell,
            cwd=str(cwd) if cwd else None,
            env=full_env,
            check=False,
        )
        return CommandExecutionResult(
            command=command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
