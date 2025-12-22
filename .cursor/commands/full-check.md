---
description: "Run full quality gate with all checks (security, tests, coverage)"
---

Run the complete quality gate with all security scans, linting, tests, and coverage checks. This is the comprehensive check that should pass before committing.

## Usage

```bash
scripts/quality-gate.sh
```

## What It Checks

1. **Quick checks** (formatting, syntax)
2. **Security scans** (Trivy, Zizmor, Hadolint)
3. **Full linting** (Ruff, Shellcheck, Actionlint, Mypy if enabled)
4. **Emoji detection and removal** (MANDATORY)
   - Scan all code and documentation files for emojis
   - Remove any emojis found in code, comments, strings, or documentation
   - This check must pass before commit is allowed
5. **Tests** (pytest with coverage)
6. **Coverage threshold** (95% minimum)

## When to Use

- **Before commit**: Full validation before committing code
- **After major changes**: Verify everything still works
- **On branch switch**: Ensure branch is in good state
- **Periodic validation**: Every 30 minutes or after significant changes

## Exit Codes

- `0`: All checks passed
- `1`: One or more checks failed

## Performance

- **Target**: < 2 minutes (depends on test suite size)
- **Scope**: Entire codebase
- **Blocking**: Should block commit if fails

## Agent Requirements

**CRITICAL**: When running this check, agents MUST:
- Scan all code and documentation files for emojis
- Remove any emojis found in code, comments, strings, or documentation
- Treat emoji detection as a blocking issue (same severity as test failures)
- Verify emoji removal before considering the check complete

## Integration

This is the comprehensive check that enforces all quality gates. It runs after quick-check passes and before allowing commits.

