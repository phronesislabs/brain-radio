#!/usr/bin/env bash
# Run arbitrary Python commands inside Docker container

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# Determine which docker-compose file to use
COMPOSE_FILE="${1:-docker-compose.yml}"
if [ "${COMPOSE_FILE}" = "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
fi

# Get command to run (everything after compose file)
shift || true
COMMAND="${*:-}"

if [ -z "${COMMAND}" ]; then
    echo "Usage: $0 [dev|docker-compose.yml] <command>"
    echo "Example: $0 dev python -m ruff check ."
    echo "Example: $0 dev pytest tests/test_researcher.py"
    exit 1
fi

echo "Running command in Docker container: ${COMMAND}"
echo "Using compose file: ${COMPOSE_FILE}"

# Build test container if needed
docker-compose -f "${COMPOSE_FILE}" build test >/dev/null 2>&1 || true

# Run command
docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test "${COMMAND}"

