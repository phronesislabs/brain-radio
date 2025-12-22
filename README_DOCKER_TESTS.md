# Docker-Based Testing and Execution

All code execution, including tests, linting, and other Python operations, **must run inside Docker containers**, not on the local OS.

## Why Docker-Only Execution?

- **Consistency**: Same environment locally and in production
- **Reproducibility**: No "works on my machine" issues
- **Isolation**: No conflicts with local Python installations
- **CI/CD Alignment**: Local development matches CI exactly

## Test Strategy: Runtime vs Build-Time

This project uses **runtime testing** (separate test container) rather than build-time testing (tests in Dockerfile). See [docs/DOCKER_TEST_STRATEGY.md](docs/DOCKER_TEST_STRATEGY.md) for a detailed comparison.

**Why runtime testing?**
- ✅ Fast iteration during development (TDD workflow)
- ✅ Flexible - run specific tests easily
- ✅ Better debugging experience
- ✅ Matches our quality gate approach

**Optional build-time testing** is available via `Dockerfile.backend.production` for production image validation.

## Running Tests

### Quick Test Run

```bash
# Run all tests
./scripts/test-docker.sh

# Run specific test file
./scripts/test-docker.sh dev pytest tests/test_researcher.py

# Run with specific pytest arguments
./scripts/test-docker.sh dev pytest tests/test_researcher.py::test_focus_protocol_rejects_vocals -v
```

### Using Docker Compose Directly

```bash
# Build test container
docker-compose build test

# Run tests
docker-compose --profile test run --rm test

# Run specific test
docker-compose --profile test run --rm test pytest tests/test_researcher.py -v

# Run with coverage
docker-compose --profile test run --rm test pytest --cov=src/brain_radio --cov-report=html
```

## Running Other Python Commands

Use the `run-docker.sh` script to run any Python command in Docker:

```bash
# Run ruff linting
./scripts/run-docker.sh dev python -m ruff check .

# Run ruff formatting check
./scripts/run-docker.sh dev python -m ruff format --check .

# Run mypy type checking
./scripts/run-docker.sh dev python -m mypy src/

# Run any Python script
./scripts/run-docker.sh dev python -c "print('Hello from Docker')"
```

## Quality Gate

The quality gate script (`scripts/quality-gate.sh`) automatically runs all checks in Docker:

```bash
./scripts/quality-gate.sh
```

This will:
1. Run security scans (Trivy, Zizmor, Hadolint)
2. Run linting (Ruff, Shellcheck, Actionlint) - **Ruff runs in Docker**
3. Run tests with coverage - **Tests run in Docker**
4. Check coverage threshold (95%)

## Development Workflow

### Before Making Changes

```bash
# Start development containers
docker-compose -f docker-compose.dev.yml up -d

# Run tests to verify current state
./scripts/test-docker.sh dev
```

### During Development

```bash
# Run specific test while developing
./scripts/test-docker.sh dev pytest tests/test_researcher.py::test_specific_test -v

# Check linting
./scripts/run-docker.sh dev python -m ruff check src/

# Auto-fix linting issues
./scripts/run-docker.sh dev python -m ruff check --fix src/
./scripts/run-docker.sh dev python -m ruff format src/
```

### Before Committing

```bash
# Run full quality gate (everything in Docker)
./scripts/quality-gate.sh
```

## CI/CD

The GitHub Actions CI workflow uses Docker for all test execution:

- Tests run in Docker containers
- Ruff linting runs in Docker
- Coverage is collected from Docker containers

See `.github/workflows/ci.yml` for details.

## Test Container Details

The test container (`Dockerfile.test`) includes:
- Python 3.11
- All project dependencies (`[dev]` extra)
- Test dependencies (pytest, coverage, etc.)
- Source code mounted as volumes for live editing

## Coverage Reports

Coverage reports are generated in the `coverage/` directory:

```bash
# HTML coverage report
open coverage/htmlcov/index.html

# XML coverage report (for CI)
cat coverage/coverage.xml
```

## Troubleshooting

### Container Not Building

```bash
# Rebuild test container
docker-compose build --no-cache test
```

### Tests Failing in Docker but Not Locally

This shouldn't happen if you're following Docker-only execution, but if it does:

1. Check Docker container logs: `docker-compose --profile test run --rm test pytest -v`
2. Verify dependencies are installed: `docker-compose --profile test run --rm test pip list`
3. Check Python version: `docker-compose --profile test run --rm test python --version`

### Coverage Not Generating

```bash
# Ensure coverage directory exists
mkdir -p coverage

# Run tests with explicit coverage output
docker-compose --profile test run --rm test pytest --cov=src/brain_radio --cov-report=xml --cov-report=html
```

## Migration from Local Execution

If you have existing scripts or workflows that run Python code locally:

1. **Replace direct Python calls** with `./scripts/run-docker.sh dev <command>`
2. **Replace pytest calls** with `./scripts/test-docker.sh dev pytest <args>`
3. **Update CI/CD** to use Docker (already done in `.github/workflows/ci.yml`)

## Examples

### Old Way (Don't Do This)
```bash
# ❌ DON'T: Running locally
python -m pytest tests/
python -m ruff check .
```

### New Way (Do This)
```bash
# ✅ DO: Running in Docker
./scripts/test-docker.sh dev pytest tests/
./scripts/run-docker.sh dev python -m ruff check .
```

## Benefits

1. **No Local Python Setup Required**: Just Docker
2. **Consistent Environment**: Same Python version, same dependencies
3. **Easy CI/CD**: Same commands work in CI
4. **Isolated**: No conflicts with other projects
5. **Reproducible**: Anyone can run the same tests with the same results

