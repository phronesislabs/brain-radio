#!/usr/bin/env bash
# Install Git Hooks
# Installs pre-commit hook that runs checks before commits

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

GIT_HOOKS_DIR="${ROOT_DIR}/.git/hooks"
PRE_COMMIT_HOOK="${GIT_HOOKS_DIR}/pre-commit"
HOOK_SCRIPT="${SCRIPT_DIR}/pre-commit-hook.sh"

if [ ! -d "${GIT_HOOKS_DIR}" ]; then
    echo "ERROR: .git/hooks directory not found. Are you in a git repository?"
    exit 1
fi

# Install pre-commit hook
if [ -f "${HOOK_SCRIPT}" ]; then
    ln -sf "../../.checks/scripts/pre-commit-hook.sh" "${PRE_COMMIT_HOOK}"
    chmod +x "${PRE_COMMIT_HOOK}"
    echo "PASS: Pre-commit hook installed"
    echo "   Quick checks will run before commits (fail-fast)"
    echo "   Full quality gate will run if quick checks pass"
else
    echo "ERROR: pre-commit-hook.sh not found"
    exit 1
fi

