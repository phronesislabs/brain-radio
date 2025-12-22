# Security and Quality Setup Guide

This document describes the security and quality tooling setup for Brain-Radio.

## Quick Start

1. **Prerequisites:**
   - `curl` must be installed (available by default on macOS and Ubuntu)
   - `python3` must be available
   - `uv` is recommended for Python package management

2. **Install pre-commit:**
   ```bash
   uv pip install pre-commit
   ```

3. **Setup all security and quality tools:**
   ```bash
   .checks/scripts/tooling/setup-tools.sh
   ```
   
   **Note:** The setup scripts use `curl` for downloading tools. If running in a Docker container or minimal environment, ensure `curl` is installed:
   ```dockerfile
   RUN apt-get update && apt-get install -y curl
   ```

3. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Run the orchestrator to set everything up:**
   ```bash
   .checks/scripts/orchestrator.sh --auto-fix
   ```

## Tools Overview

### Package Management
- **uv**: Used instead of pip for all Python package management
  - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Usage: `uv pip install <package>`

### Security Scanners

#### Trivy
- **Purpose**: SCA (Software Composition Analysis) and SAST (Static Application Security Testing)
- **Scans**: Vulnerabilities, secrets, misconfigurations, Docker images, Docker compose configs
- **Severity**: Only HIGH and CRITICAL block commits
- **Install**: Via `setup-tools.sh` script
- **Usage**: 
  - Filesystem: `trivy fs --scanners vuln,secret,misconfig --severity HIGH,CRITICAL .`
  - Docker config: `trivy config --severity HIGH,CRITICAL docker-compose.yml`
  - Docker image: `trivy image --severity HIGH,CRITICAL <image>`

#### Hadolint
- **Purpose**: Dockerfile security and best practices linter
- **Scans**: All Dockerfile* files for security issues and best practices
- **Install**: Via `setup-tools.sh` script
- **Usage**: `hadolint Dockerfile`

#### Zizmor
- **Purpose**: GitHub Actions security scanner
- **Scans**: `.github/workflows/` for security issues
- **Install**: `uv tool install zizmor`
- **Usage**: `zizmor .github/workflows`

#### Pinact
- **Purpose**: GitHub Actions SHA-pinning
- **Ensures**: All GitHub Actions are SHA-pinned (not version tags)
- **Install**: Via `setup-tools.sh` script
- **Usage**: 
  - Check: `pinact run --check`
  - Update: `pinact run -u`

### Linters

#### Ruff
- **Purpose**: Python linting and formatting (replaces black, flake8, isort)
- **Install**: `uv pip install ruff`
- **Usage**: 
  - Lint: `ruff check .`
  - Format: `ruff format .`
  - Auto-fix: `ruff check --fix .`

#### Shellcheck
- **Purpose**: Shell script linting
- **Install**: Via `setup-tools.sh` script
- **Usage**: `shellcheck scripts/*.sh`

#### Actionlint
- **Purpose**: GitHub Actions workflow linting
- **Install**: Via `setup-tools.sh` script
- **Usage**: `actionlint -color`

#### Hadolint
- **Purpose**: Dockerfile security and best practices linting
- **Install**: Via `setup-tools.sh` script
- **Usage**: `hadolint Dockerfile`

## Pre-commit Hooks

Pre-commit hooks run automatically on every commit. They include:

- Trailing whitespace removal
- End-of-file fixes
- YAML/JSON/TOML validation
- Ruff linting and formatting (auto-fix enabled)
- Shellcheck
- Actionlint
- Hadolint (Dockerfile security)
- Trivy security scan (filesystem, Docker images, Docker configs)
- Pinact check
- Zizmor security scan
- Quality gate (tests + coverage)

**No code can be committed that fails pre-commit hooks.**

### Manual Pre-commit Run

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

## Quality Gate

The quality gate script (`scripts/quality-gate.sh`) runs:

1. Pinact check (GitHub Actions pinning)
2. Actionlint (workflow linting)
3. Shellcheck (shell script linting)
4. Hadolint (Dockerfile security)
5. Zizmor (GitHub Actions security)
6. Trivy (comprehensive security scan: filesystem, Docker images, Docker configs)
7. Ruff (Python linting and formatting)
8. Pytest (tests with coverage)
9. Coverage threshold check (≥95%)

Run manually:
```bash
./scripts/quality-gate.sh
```

## Checks Orchestrator

The orchestrator script (`.checks/scripts/orchestrator.sh`) automates the entire workflow:

```bash
# Basic run (no auto-fix)
.checks/scripts/orchestrator.sh

# With auto-fix enabled
.checks/scripts/orchestrator.sh --auto-fix

# With auto-commit (use with caution)
.checks/scripts/orchestrator.sh --auto-fix --auto-commit

# Custom max iterations
.checks/scripts/orchestrator.sh --auto-fix --max-iterations 5
```

The orchestrator:
- Ensures all tools are installed
- Updates and pins GitHub Actions
- Runs all security scans (including Docker components)
- Runs all linters (with auto-fix if enabled)
- Runs pre-commit hooks
- Runs quality gate
- Iterates until all checks pass or max iterations reached

## Docker Security Scanning

The security setup includes comprehensive Docker scanning:

### Hadolint
- Scans all `Dockerfile*` files for security best practices
- Checks for common vulnerabilities and misconfigurations
- Enforces Docker security guidelines

### Trivy Docker Scans
- **Docker Images**: Scans base images and built images for vulnerabilities
- **Docker Compose**: Scans `docker-compose*.yml` files for misconfigurations
- **Filesystem**: Scans the entire codebase including Docker-related files

### Docker Components Scanned
- `Dockerfile*` files (via hadolint)
- `docker-compose*.yml` files (via trivy config)
- Base images in Dockerfiles (via trivy image)
- Built Docker images (via trivy image, if available)

All Docker security issues with HIGH or CRITICAL severity will block commits.

## CI Workflows

The CI workflow (`.github/workflows/ci.yml`) runs:

1. **Test job**: Full quality gate
2. **Security scan job**: Trivy with SARIF upload to GitHub Security
3. **Lint job**: All linting tools

All jobs must pass for PRs to be mergeable.

## Dependabot

Dependabot is configured with "paranoid" security settings:

- Daily scans for Python (pip/uv), npm, and GitHub Actions
- Only security updates are automatically created
- Limits on open PRs (10 per ecosystem)
- All dependency PRs are labeled

Configuration: `.github/dependabot.yml`

## Auto-fix Branch Workflow

When working in auto-fix branches (e.g., `dependabot/*`, `chore/pinact`, `chore/security-*`):

1. Run `./scripts/quality-gate.sh` to identify issues
2. Fix test failures first
3. Fix linting/formatting issues
4. Fix security issues (HIGH/CRITICAL only)
5. Ensure coverage remains ≥95%
6. Run `pre-commit run --all-files`

See `.cursor/rules/autofix-branch.mdc` for the full agent rule.

## Troubleshooting

### Tools not found
Run `.checks/scripts/tooling/setup-tools.sh` to setup all required tools.

### Pre-commit hooks failing
1. Check which hook is failing: `pre-commit run --all-files`
2. Fix the issues manually or use auto-fix where available
3. Re-run: `pre-commit run --all-files`

### Coverage below threshold
- Add more tests to increase coverage
- Ensure all new code has tests
- Check coverage report: `pytest --cov=src/brain_radio --cov-report=html`

### Security issues found
- Review the Trivy or Zizmor output
- Fix HIGH and CRITICAL issues before committing
- Some issues may require dependency updates

### GitHub Actions not pinned
Run `pinact run -u` to update and pin all actions.

## Portable Setup

The checks system is designed to be portable across repositories. To use it in another repo:

1. Copy the `.checks/` directory to your repository
2. Copy `checks-config.yaml.example` to `checks-config.yaml` and customize
3. Copy `.pre-commit-config.yaml` (adjust as needed)
4. Copy `.github/dependabot.yml` (adjust as needed)
5. Run `.checks/scripts/orchestrator.sh --auto-fix`

Alternatively, extract `.checks/` to its own repository and include it as a submodule or copy it into new repositories.

