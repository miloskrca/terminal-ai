# Terminal AI

Natural-language assistant for generating and running terminal commands.

## Editable install

```
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Set `OPENAI_API_KEY` before invoking the CLI:

```
export OPENAI_API_KEY=sk-...
python -m terminal_ai.cli "kill anything on port 3000"
```

## Build a standalone `.pyz`

Create a single-file archive that embeds the CLI and prompt template:

```
tmpdir=$(mktemp -d) && \
  rsync -a src/ "$tmpdir/app/" && \
  python -m zipapp "$tmpdir/app" \
    -m terminal_ai.cli.__main__:main \
    -o terminal_ai_cli.pyz && \
  rm -rf "$tmpdir"
```

Distribute `terminal_ai_cli.pyz` together with the runtime requirement:

```
pip install httpx
```

## Shell aliases

### zsh / bash

Add to `~/.zshrc` or `~/.bashrc`:

```
alias d='python ~/bin/terminal_ai_cli.pyz --accept'
```

Reload the shell (`source ~/.zshrc`) and run `d clear laravel caches`. Skip
`--accept` if you want to confirm destructive commands interactively.

### fish

Create an alias in `~/.config/fish/config.fish`:

```
alias d "python ~/bin/terminal_ai_cli.pyz --accept"
```

Fish reads environment variables differently; set the key in
`~/.config/fish/conf.d/openai.fish`:

```
set -x OPENAI_API_KEY sk-...
```

### Windows PowerShell

Add this to your profile (run `notepad $PROFILE`):

```
$env:OPENAI_API_KEY = "sk-..."
Set-Alias d "python" -Option Constant
Function Invoke-TerminalAI { param([Parameter(ValueFromRemainingArguments=$true)][String[]]$Args)
    python C:\path\to\terminal_ai_cli.pyz --accept @Args
}
Set-Alias d Invoke-TerminalAI
```

Restart the shell and run `d "is there anything running on port 8080"`.

## Example session

See `examples/sample_session.md` for a walkthrough.
