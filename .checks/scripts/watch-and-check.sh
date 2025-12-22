#!/usr/bin/env bash
# File Watcher with Automatic Checks
# Watches for file changes and runs quick checks automatically
# Provides fail-fast feedback on file changes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "${SCRIPT_DIR}/../../.checks" ]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
elif [ -d "${SCRIPT_DIR}/../../../.checks" ]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
else
    ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

cd "${ROOT_DIR}"

QUICK_CHECK="${SCRIPT_DIR}/quick-check.sh"
CHECK_INTERVAL=${CHECK_INTERVAL:-5}  # Check every N seconds
FILE_CHANGE_THRESHOLD=${FILE_CHANGE_THRESHOLD:-10}  # Run check after N file changes

# Track file changes
CHANGED_FILES=0
LAST_CHECK_TIME=$(date +%s)

# Files to watch (patterns used in fswatch/inotifywait includes)
# shellcheck disable=SC2034
WATCH_PATTERNS=(
    "*.py"
    "*.sh"
    "*.yml"
    "*.yaml"
    "Dockerfile*"
    ".github/workflows/*.yml"
    ".github/workflows/*.yaml"
    "pyproject.toml"
    "package.json"
)

should_run_check() {
    local current_time
    current_time=$(date +%s)
    local time_since_check=$((current_time - LAST_CHECK_TIME))
    
    # Run if enough time has passed OR enough files changed
    if [ "${time_since_check}" -ge "${CHECK_INTERVAL}" ] || [ "${CHANGED_FILES}" -ge "${FILE_CHANGE_THRESHOLD}" ]; then
        return 0
    fi
    return 1
}

run_quick_check() {
    if [ -f "${QUICK_CHECK}" ]; then
        echo "[$(date +%H:%M:%S)] Running quick checks..."
        if "${QUICK_CHECK}"; then
            echo "[$(date +%H:%M:%S)] PASS: Quick checks passed"
        else
            echo "[$(date +%H:%M:%S)] FAIL: Quick checks failed - fix issues before committing"
        fi
        CHANGED_FILES=0
        LAST_CHECK_TIME=$(date +%s)
    fi
}

# Check if fswatch or inotifywait is available
if command -v fswatch >/dev/null 2>&1; then
    echo "Watching for file changes (checking every ${CHECK_INTERVAL}s or after ${FILE_CHANGE_THRESHOLD} changes)..."
    echo "Press Ctrl+C to stop"
    
    fswatch -r -m poll_monitor \
        --include='\.py$' \
        --include='\.sh$' \
        --include='\.yml$' \
        --include='\.yaml$' \
        --include='Dockerfile' \
        --include='pyproject\.toml$' \
        --include='package\.json$' \
        --exclude='\.git' \
        --exclude='\.checks' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        "${ROOT_DIR}" | while read -r _file; do
        CHANGED_FILES=$((CHANGED_FILES + 1))
        if should_run_check; then
            run_quick_check
        fi
    done
elif command -v inotifywait >/dev/null 2>&1; then
    echo "Watching for file changes (checking every ${CHECK_INTERVAL}s or after ${FILE_CHANGE_THRESHOLD} changes)..."
    echo "Press Ctrl+C to stop"
    
    inotifywait -m -r --format '%w%f' \
        -e modify,create,delete \
        --include='\.py$' \
        --include='\.sh$' \
        --include='\.yml$' \
        --include='\.yaml$' \
        --include='Dockerfile' \
        --exclude='\.git' \
        --exclude='\.checks' \
        "${ROOT_DIR}" 2>/dev/null | while read -r _file; do
        CHANGED_FILES=$((CHANGED_FILES + 1))
        if should_run_check; then
            run_quick_check
        fi
    done
else
    echo "No file watcher available (fswatch or inotifywait required)"
    echo "Falling back to periodic checks every ${CHECK_INTERVAL} seconds..."
    
    while true; do
        sleep "${CHECK_INTERVAL}"
        if [ "${CHANGED_FILES}" -gt 0 ]; then
            run_quick_check
        fi
    done
fi

