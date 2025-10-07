# Sample Terminal AI Session

```
$ python -m terminal_ai.cli "kill anything on port 3000" --no-exec
Command: lsof -i :3000 | awk 'NR>1 { print $2 }' | xargs kill -9
Why: Terminate processes listening on port 3000
```

Pass `--accept` to execute the command immediately or keep the default prompt to
confirm before running.
