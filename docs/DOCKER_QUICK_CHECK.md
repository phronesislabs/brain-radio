# Docker-Based Quick Check Setup

**Date**: 2025-12-22  
**Status**: ✅ **COMPLETE** - All checks run in Docker containers

## Overview

All quality checks (quick-check and full quality gate) now run inside Docker containers for consistency and reproducibility. This ensures the same environment is used for development, testing, and CI/CD.

## Changes Made

### 1. Updated `Dockerfile.test`

- Installs quality check tools during build using `setup-tools.sh`
- Tools are installed into `/app/.checks/.tools/bin/` (and `/app/.tools/bin/` if ROOT_DIR is set correctly)
- Adds tool directories to PATH via ENV variable

### 2. Updated `docker-compose.yml`

- Removed `.tools` volume mount (tools are installed in image)
- Added read-only mounts for `.checks`, `.github`, and `scripts` directories
- Test service uses the built image with pre-installed tools

### 3. Updated `.checks/scripts/quick-check.sh`

- All checks now run inside Docker containers
- Python formatting: `docker-compose --profile test run --rm test python -m ruff format --check .`
- Shell script linting: `docker-compose --profile test run --rm test shellcheck <files>`
- GitHub Actions linting: `docker-compose --profile test run --rm test actionlint`
- Emoji detection: Runs Python script in container

## Tools Installed

The following tools are automatically installed in the Docker container:

- **shellcheck**: Shell script linting
- **actionlint**: GitHub Actions workflow linting
- **pinact**: GitHub Actions SHA-pinning checker
- **trivy**: Security scanning
- **hadolint**: Dockerfile security linting
- **zizmor**: GitHub Actions security scanner
- **ruff**: Python linting and formatting (via pip/uv)

## Usage

### Run Quick Check

```bash
.checks/scripts/quick-check.sh
```

This will:
1. Build the test container if needed
2. Run all quick checks inside the container
3. Report results

### Run Full Quality Gate

```bash
scripts/quality-gate.sh
```

This runs comprehensive checks including:
- Security scans (Trivy, Zizmor, Hadolint)
- Linting (Ruff, Shellcheck, Actionlint)
- Tests (pytest with coverage)
- Coverage threshold check (95%)

## Benefits

1. **Consistency**: Same environment for all developers
2. **Reproducibility**: No "works on my machine" issues
3. **Isolation**: Tools don't pollute host system
4. **CI/CD Ready**: Same setup works in CI pipelines
5. **Version Control**: Tool versions are locked in Docker image

## Troubleshooting

### Tools Not Found

If tools aren't found, rebuild the container:
```bash
docker-compose -f docker-compose.yml build test
```

### Check Tool Installation

Verify tools are installed:
```bash
docker-compose -f docker-compose.yml --profile test run --rm test \
  bash -c "export PATH=\"/app/.tools/bin:/app/.checks/.tools/bin:/root/.local/bin:\${PATH}\" && \
  command -v shellcheck && shellcheck --version"
```

### Manual Tool Installation

If needed, tools can be installed manually in a running container:
```bash
docker-compose -f docker-compose.yml --profile test run --rm test \
  bash -c "cd /app && ROOT_DIR=/app .checks/scripts/tooling/setup-tools.sh"
```

## PATH Configuration

The container's PATH includes (in order):
1. `/app/.tools/bin` - Main tools directory
2. `/app/.checks/.tools/bin` - Tools installed by setup script
3. `/root/.local/bin` - UV tool installations (zizmor, etc.)
4. System PATH

This ensures all tools are found regardless of where they're installed.

