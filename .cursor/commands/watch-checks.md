---
description: "Watch files and run quick checks automatically on changes"
---

Start a file watcher that automatically runs quick checks when files change. Provides continuous fail-fast feedback.

## Usage

```bash
# Start watching (runs checks every 5 seconds or after 10 file changes)
# Note: This requires a watch script. If not available, use the orchestrator:
scripts/security-quality-orchestrator.sh --auto-fix --watch

# Or manually run checks periodically
while true; do
  scripts/quality-gate.sh --quick
  sleep 5
done
```

## Behavior

- **Watches**: Python, shell, YAML, Dockerfile, and config files
- **Triggers**: 
  - Every N seconds (default: 5)
  - After N file changes (default: 10)
- **Action**: Runs quick checks
- **Output**: Non-blocking notifications

## When to Use

- **During active development**: Continuous feedback
- **Before committing**: Ensure code is clean
- **Background monitoring**: Keep code quality high

## Requirements

- `fswatch` (macOS) or `inotifywait` (Linux)
- Falls back to periodic checks if not available

## Integration

This provides the "pre-pre-commit" continuous checking. Run it in a separate terminal while developing for immediate feedback.

