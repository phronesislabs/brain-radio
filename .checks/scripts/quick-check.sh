#!/usr/bin/env bash
# Quick Check Script - Fast feedback loop
# Runs lightweight checks that provide immediate feedback
# Designed to run frequently (on file save, before commit, etc.)
# All checks run inside Docker containers for consistency

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "${SCRIPT_DIR}/../../.checks" ]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
elif [ -d "${SCRIPT_DIR}/../../../.checks" ]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
else
    ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi

CONFIG_FILE="${ROOT_DIR}/checks-config.yaml"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"

cd "${ROOT_DIR}"

# Load configuration helper
load_config() {
    local key="$1"
    local default="$2"
    
    if [ -f "${CONFIG_FILE}" ] && command -v yq >/dev/null 2>&1; then
        yq eval "${key} // ${default}" "${CONFIG_FILE}" 2>/dev/null || echo "${default}"
    elif [ -f "${CONFIG_FILE}" ] && command -v python3 >/dev/null 2>&1; then
        python3 -c "
import yaml, sys
try:
    with open('${CONFIG_FILE}') as f:
        config = yaml.safe_load(f) or {}
    keys = '${key}'.split('.')
    value = config
    for k in keys:
        value = value.get(k, {}) if isinstance(value, dict) else None
        if value is None:
            break
    print(value if value is not None else '${default}')
except:
    print('${default}')
" 2>/dev/null || echo "${default}"
    else
        echo "${default}"
    fi
}

PYTHON_ENABLED=$(load_config ".quality_gate.python.enabled" "true")
TOOL_RUFF=$(load_config ".quality_gate.tools.ruff" "true")
TOOL_SHELLCHECK=$(load_config ".quality_gate.tools.shellcheck" "true")
TOOL_ACTIONLINT=$(load_config ".quality_gate.tools.actionlint" "true")

ERRORS=0

# Ensure Docker container is built
if ! docker-compose -f "${COMPOSE_FILE}" ps test >/dev/null 2>&1; then
    echo "Building test container..."
    docker-compose -f "${COMPOSE_FILE}" build test >/dev/null 2>&1 || true
fi

# Quick Python formatting check (fast) - runs in Docker
if [ "${TOOL_RUFF}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Quick check: Python formatting..."
    if docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test python -m ruff format --check . >/dev/null 2>&1; then
        echo "  [OK] Python formatting OK"
    else
        echo "  [FAIL] Formatting issues detected. Run: docker-compose --profile test run --rm test python -m ruff format ."
        ERRORS=$((ERRORS + 1))
    fi
fi

# Quick shell script lint (fast) - runs in Docker
if [ "${TOOL_SHELLCHECK}" = "true" ]; then
    echo "Quick check: Shell scripts..."
    # Find shell scripts and run shellcheck in container
    SHELL_FILES=$(find . -name "*.sh" -type f -not -path "./.git/*" -not -path "./.tools/*" -not -path "./.checks/*" 2>/dev/null | head -5 || true)
    if [ -n "${SHELL_FILES}" ]; then
        # Run shellcheck (tools are pre-installed in container)
        if docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test bash -c "\
            export PATH=\"/app/.tools/bin:/app/.checks/.tools/bin:/root/.local/bin:\${PATH}\" && \
            command -v shellcheck >/dev/null 2>&1 && shellcheck ${SHELL_FILES} >/dev/null 2>&1" 2>/dev/null; then
            echo "  [OK] Shell scripts OK"
        else
            echo "  [FAIL] Shell script issues detected. Run: docker-compose --profile test run --rm test shellcheck <file>"
            ERRORS=$((ERRORS + 1))
        fi
    fi
fi

# Quick GitHub Actions syntax (fast) - runs in Docker
if [ "${TOOL_ACTIONLINT}" = "true" ] && [ -d .github/workflows ]; then
    echo "Quick check: GitHub Actions..."
    # Run actionlint (tools are pre-installed in container)
    if docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test bash -c "\
        export PATH=\"/app/.tools/bin:/app/.checks/.tools/bin:/root/.local/bin:\${PATH}\" && \
        command -v actionlint >/dev/null 2>&1 && actionlint -no-color >/dev/null 2>&1" 2>/dev/null; then
        echo "  [OK] GitHub Actions OK"
    else
        echo "  [FAIL] GitHub Actions issues detected. Run: docker-compose --profile test run --rm test actionlint"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Emoji detection (MANDATORY) - runs in Docker
echo "Quick check: Emoji detection..."
if docker-compose -f "${COMPOSE_FILE}" --profile test run --rm test python3 -c "
import re
import sys
import os

emoji_pattern = re.compile(
    '['
    '\U0001F600-\U0001F64F'
    '\U0001F300-\U0001F5FF'
    '\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF'
    '\U00002702-\U000027B0'
    '\U000024C2-\U0001F251'
    ']+',
    flags=re.UNICODE
)

# Check changed files
changed_files = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '.tools' in root:
        continue
    for file in files:
        if file.endswith(('.py', '.sh', '.md', '.yml', '.yaml', '.ts', '.tsx', '.js', '.jsx')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if emoji_pattern.search(content):
                        print(f'ERROR: Emojis found in {filepath}', file=sys.stderr)
                        sys.exit(1)
            except:
                pass
sys.exit(0)
" 2>/dev/null; then
    echo "  [OK] No emojis found"
else
    echo "  [FAIL] Emojis detected in files (MANDATORY: must be removed)"
    ERRORS=$((ERRORS + 1))
fi

if [ ${ERRORS} -eq 0 ]; then
    echo "PASS: Quick checks passed"
    exit 0
else
    echo "FAIL: Quick checks found ${ERRORS} issue(s)"
    exit 1
fi

