# Checks

Portable security and quality checking tools for repositories.

## Quick Start

1. **Setup tools:**
   ```bash
   .checks/scripts/tooling/setup-tools.sh
   ```

2. **Configure for your repository:**
   - Copy `templates/checks-config.yaml.example` to `checks-config.yaml` in repo root
   - Customize the configuration for your project

3. **Run checks:**
   ```bash
   .checks/scripts/orchestrator.sh --auto-fix
   ```

## Structure

```
.checks/
|-- scripts/
|   |-- quality-gate.sh       # Full quality gate (comprehensive)
|   |-- quick-check.sh       # Quick checks (fast feedback)
|   |-- orchestrator.sh      # Orchestrator with auto-fix
|   |-- watch-and-check.sh   # File watcher for automatic checks
|   |-- pre-commit-hook.sh   # Git pre-commit hook
|   |-- install-git-hooks.sh # Install git hooks
|   `-- tooling/
|       `-- setup-tools.sh   # Tool setup
|-- templates/
|   `-- checks-config.yaml.example
|-- AUTO_CHECKS_GUIDE.md     # Automatic checks guide
`-- install.sh               # Installation script
```

## Configuration

Configuration is done via `checks-config.yaml` in the repository root. See `templates/checks-config.yaml.example` for all options.

Key configuration areas:
- **coverage**: Test coverage thresholds and paths
- **python**: Python-specific settings (package paths, install commands)
- **docker**: Docker scanning configuration
- **tools**: Enable/disable specific tools

## Tools

The checks system uses:
- **pinact**: GitHub Actions SHA-pinning
- **actionlint**: GitHub Actions linting
- **shellcheck**: Shell script linting
- **zizmor**: GitHub Actions security scanning
- **hadolint**: Dockerfile security linting
- **trivy**: Comprehensive security scanning (SCA + SAST + Docker)
- **ruff**: Python linting and formatting
- **pytest**: Python testing (with coverage)

## Usage

### Run all checks
```bash
.checks/scripts/orchestrator.sh --auto-fix
```

### Run quality gate only
```bash
.checks/scripts/quality-gate.sh
```

### Setup tools
```bash
.checks/scripts/tooling/setup-tools.sh
```

### Quick check (fast feedback)
```bash
.checks/scripts/quick-check.sh
```

### Watch files and auto-check
```bash
.checks/scripts/watch-and-check.sh
```

### Install git hooks (pre-commit checks)
```bash
.checks/scripts/install-git-hooks.sh
```

## Portability

This system is designed to be portable across repositories:

1. **Self-contained**: All scripts are in `.checks/`
2. **Config-driven**: Behavior controlled by `checks-config.yaml`
3. **Tool detection**: Automatically detects available tools
4. **Flexible paths**: Works from various directory structures

## Integration

### Pre-commit Hooks

The pre-commit config runs a two-stage check:
1. **Quick check** first (fail-fast, < 5 seconds)
2. **Full quality gate** if quick check passes

This provides immediate feedback while ensuring comprehensive validation.

Install hooks:
```bash
# Option 1: Pre-commit framework (recommended)
pre-commit install

# Option 2: Direct git hook
.checks/scripts/install-git-hooks.sh
```

### Automatic Checks

The system supports automatic checking for fail-fast feedback:

- **On file save**: Quick checks run automatically (via file watcher)
- **Before commit**: Two-stage check (quick → full)
- **Periodic**: Background checks every N seconds
- **On branch switch**: Full quality gate

See `AUTO_CHECKS_GUIDE.md` for details.

### CI/CD

Use in CI workflows:
```yaml
- name: Run checks
  run: .checks/scripts/quality-gate.sh
```

### DevContainer

Add to `.devcontainer/devcontainer.json`:
```json
{
  "postCreateCommand": ".checks/scripts/tooling/setup-tools.sh"
}
```

## Extracting to Separate Repo

To extract this to its own repository:

1. Copy `.checks/` directory to new repo
2. Add installation instructions
3. Create template repository structure
4. Document configuration options

The system is already structured for this - just copy the `.checks/` directory.

