---
description: "Run quick checks for fast feedback (formatting, syntax)"
---

Run quick, lightweight checks that provide immediate feedback without running full security scans or tests. Designed for frequent execution (on file save, before commit).

## Usage

```bash
scripts/quality-gate.sh --quick
```

Note: If a dedicated `quick-check.sh` script exists, use that instead. Otherwise, the quality gate script may support a `--quick` flag for faster checks.

## What It Checks

1. **Python formatting** (ruff format --check)
   - Fast syntax and formatting validation
   - Auto-fixable issues

2. **Shell script syntax** (shellcheck on changed files)
   - Syntax errors in shell scripts
   - Common shell script issues

3. **GitHub Actions syntax** (actionlint)
   - Workflow file syntax
   - Action configuration errors

4. **Emoji detection and removal** (MANDATORY)
   - Scan changed files for emojis
   - Remove any emojis found in code, comments, strings, or documentation
   - Fast check on modified files only

## When to Use

- **On file save**: Run automatically when editing relevant files
- **Before commit**: Quick validation before full quality gate
- **During editing**: Periodic background checks
- **After auto-fix**: Verify fixes didn't break anything

## Exit Codes

- `0`: All quick checks passed
- `1`: Issues found (formatting, syntax errors)

## Performance

- **Target**: < 5 seconds
- **Scope**: Only changed/relevant files
- **Non-blocking**: Can run in background

## Agent Requirements

**CRITICAL**: When running this check, agents MUST:
- Scan all changed files for emojis
- Remove any emojis found in code, comments, strings, or documentation
- Treat emoji detection as a blocking issue (same severity as syntax errors)
- Verify emoji removal before considering the check complete

## Integration

This is the "pre-pre-commit" check that runs before the full quality gate. It catches common issues early to keep feedback loops short.

