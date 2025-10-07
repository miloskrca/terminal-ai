# Repository Guidelines

## Project Structure & Module Organization
Runtime code lives in `src/terminal_ai/` and mirrors the runtime concerns:
- `agents/` contains language-to-command agents (e.g., `translate_command_agent.py`).
- `cli/` exposes command-line entrypoints such as `command_cli.py` and `__main__.py`.
- `io/` holds integrations (model clients, prompt loader, command runner).
Reusable prompt templates default to the embedded copy, but override files belong in
`prompts/`. Tests mirror the package tree under `tests/` with agent and CLI suites, and
fixture assets go to `tests/fixtures/`. Example transcripts reside in `examples/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` – prepare an isolated environment.
- `pip install -e .` – install the package in editable mode; pulls in runtime deps.
- `pytest` – run all unit tests; configured via `pyproject.toml` to pick up `src/`.
- `python -m terminal_ai.cli "task"` – execute the primary CLI against OpenAI.
- `python -m zipapp <staging_dir> -m terminal_ai.cli.__main__:main -o terminal_ai_cli.pyz` –
  build the distributable pyz (see README for staging helper script).

## Coding Style & Naming Conventions
Target Python 3.11. Keep modules ASCII unless a dependency requires otherwise. Format with
`black` (88 cols) and lint via `ruff`. Agents use verb-based filenames (`translate_command_agent.py`)
and PascalCase class names ending in `Agent`. CLI modules end with `_cli.py`, and parser functions
prefer `verb_noun` naming.

## Testing Guidelines
Use `pytest`; integration for the CLI uses monkeypatching rather than network calls. Name files
`test_<module>.py` aligned with `src/terminal_ai/`. Maintain high coverage on core logic (>=85%) and
mark slow flows with `@pytest.mark.slow` when needed. Run `pytest -k name` for focused loops.

## Commit & Pull Request Guidelines
Commit messages follow `type(scope): summary`, e.g., `feat(cli): embed default prompt`. Reference
issues in the body and note prompt or model updates explicitly. PRs should include a brief summary,
verification commands (`pytest`, `python -m terminal_ai.cli ...`), and screenshots or terminal
casts whenever CLI output changes. Open drafts once tests and linting pass to surface work early.

## Security & Configuration Tips
Never commit API keys; document required variables in `.env.example` if added. Default model is
configurable through `TERMINAL_AI_MODEL`; prompt overrides via `TERMINAL_AI_PROMPTS_DIR`. Bundle
third-party model changes in separate branches and record rate-limit assumptions in PR descriptions.
