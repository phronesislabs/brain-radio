# Automatic Checks Guide

This guide explains how automatic checks work to provide fail-fast feedback and keep code quality high.

## Overview

The checks system provides **two-tier checking**:

1. **Quick Check** - Fast feedback (< 5 seconds)
   - Formatting and syntax only
   - Runs frequently (on file save, before commit)
   - Fail-fast principle

2. **Full Quality Gate** - Comprehensive validation (< 2 minutes)
   - All security scans, tests, coverage
   - Runs before commit, on branch switch
   - Blocks commits if fails

## Automatic Triggers

### 1. On File Save

**What**: Quick check runs when you save relevant files

**Files watched**:
- `.py` (Python)
- `.sh` (Shell scripts)
- `.yml`, `.yaml` (YAML configs)
- `Dockerfile*` (Docker files)
- `.github/workflows/*` (GitHub Actions)
- `pyproject.toml`, `package.json` (Dependencies)

**Action**: Runs `.checks/scripts/quick-check.sh`

**Behavior**: Non-blocking notification if issues found

### 2. Before Commit (Pre-Pre-Commit)

**What**: Two-stage check before git commit

**Stage 1**: Quick check (fail-fast)
- If fails → Block commit, show errors
- If passes → Continue to stage 2

**Stage 2**: Full quality gate
- If fails → Block commit, show errors
- If passes → Allow commit

**Installation**:
```bash
# Option 1: Use pre-commit framework (recommended)
pre-commit install

# Option 2: Install git hook directly
.checks/scripts/install-git-hooks.sh
```

### 3. Periodic Background Checks

**What**: Automatic checks every N seconds or after N file changes

**Default**: Every 5 seconds OR after 10 file changes

**Action**: Runs quick check in background

**Usage**:
```bash
# Start file watcher
.checks/scripts/watch-and-check.sh

# Customize interval
CHECK_INTERVAL=10 FILE_CHANGE_THRESHOLD=5 .checks/scripts/watch-and-check.sh
```

### 4. On Branch Switch

**What**: Full quality gate when switching branches

**Purpose**: Ensure branch is in good state

**Action**: Runs `.checks/scripts/quality-gate.sh`

### 5. On Dependency Changes

**What**: Security scans when dependencies change

**Triggered by**: Changes to `pyproject.toml`, `package.json`, `requirements*.txt`, `Dockerfile*`

**Action**: Runs Trivy and pip-audit (if enabled)

## Fail-Fast Principles

### Priority Order

1. **Formatting issues** → Auto-fix silently (ruff format)
2. **Syntax errors** → Show immediately, block commit
3. **Linting issues** → Show warning, allow continue (but fix before commit)
4. **Security issues (HIGH/CRITICAL)** → Block commit immediately
5. **Test failures** → Block commit immediately
6. **Coverage below threshold** → Block commit immediately

### Quick Check (Fast Path)

Runs in < 5 seconds:
- Python formatting (ruff format --check)
- Shell script syntax (shellcheck)
- GitHub Actions syntax (actionlint)

**Purpose**: Catch common issues immediately

### Full Quality Gate (Comprehensive)

Runs in < 2 minutes:
- All quick checks
- Security scans (Trivy, Zizmor, Hadolint)
- Full linting (Ruff, Shellcheck, Actionlint, Mypy)
- Tests with coverage
- Coverage threshold enforcement

**Purpose**: Ensure everything passes before commit

## Cursor Integration

### Rules

- **`.cursor/rules/auto-checks.mdc`**: Defines when to run checks automatically
- **`.cursor/rules/autofix-branch.mdc`**: Special behavior for auto-fix branches

### Commands

- **`quick-check`**: Run fast checks manually
- **`full-check`**: Run comprehensive checks manually
- **`watch-checks`**: Start file watcher for continuous checking
- **`checks-scan`**: Full orchestrator with auto-fix

## Usage Examples

### During Development

```bash
# Terminal 1: Start file watcher
.checks/scripts/watch-and-check.sh

# Terminal 2: Edit files normally
# Quick checks run automatically in background
```

### Before Committing

```bash
# Quick check first (fast)
.checks/scripts/quick-check.sh

# If passes, run full check
.checks/scripts/quality-gate.sh

# Then commit
git commit -m "your message"
```

### Manual Trigger

```bash
# Quick feedback
.checks/scripts/quick-check.sh

# Full validation
.checks/scripts/quality-gate.sh

# With auto-fix
.checks/scripts/orchestrator.sh --auto-fix
```

## Configuration

All behavior is configurable via `checks-config.yaml`:

```yaml
quality_gate:
  tools:
    ruff: true      # Enable/disable specific tools
    mypy: false
    # ...
```

## Benefits

1. **Fail-Fast**: Catch issues immediately, not at commit time
2. **Short Feedback Loops**: < 5 seconds for quick checks
3. **Non-Intrusive**: Background checks don't interrupt workflow
4. **Deterministic**: Same checks run at same triggers
5. **Comprehensive**: Full validation before commit

## Troubleshooting

### Quick checks too slow
- Reduce file scope in quick-check.sh
- Disable non-essential tools

### Too many notifications
- Increase CHECK_INTERVAL
- Increase FILE_CHANGE_THRESHOLD

### Checks not running automatically
- Install pre-commit hooks: `pre-commit install`
- Or install git hooks: `.checks/scripts/install-git-hooks.sh`
- Start file watcher manually: `.checks/scripts/watch-and-check.sh`

