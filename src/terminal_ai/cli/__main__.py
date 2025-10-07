"""Entry-point for ``python -m terminal_ai.cli``."""

from __future__ import annotations

import sys

from terminal_ai.cli.command_cli import main

if __name__ == "__main__":
    raise SystemExit(main())
