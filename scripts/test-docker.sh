#!/usr/bin/env bash
# Run tests inside Docker container

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# Determine which docker-compose file to use
COMPOSE_FILE="${1:-docker-compose.yml}"
if [ "${COMPOSE_FILE}" = "dev" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
fi

# Parse additional pytest arguments
shift || true
PYTEST_ARGS="${*:-}"

echo "Running tests in Docker container..."
echo "Using compose file: ${COMPOSE_FILE}"
if [ -n "${PYTEST_ARGS}" ]; then
    echo "Pytest arguments: ${PYTEST_ARGS}"
fi

# Build test container if needed
docker-compose -f "${COMPOSE_FILE}" build test

# Run tests
if [ -n "${PYTEST_ARGS}" ]; then
    docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test pytest "${PYTEST_ARGS}"
else
    docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test
fi

# Coverage files are automatically copied via volume mount (./coverage:/app/coverage)
# Just ensure the directory exists
mkdir -p "${ROOT_DIR}/coverage"

echo "Tests completed!"

