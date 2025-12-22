#!/usr/bin/env bash
# Git Pre-Commit Hook
# Runs quick check first (fail-fast), then full quality gate
# Install: ln -s ../../.checks/scripts/pre-commit-hook.sh .git/hooks/pre-commit

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
QUALITY_GATE="${SCRIPT_DIR}/quality-gate.sh"

echo "Running pre-commit checks..."

# Stage 1: Quick check (fail-fast)
if [ -f "${QUICK_CHECK}" ]; then
    echo "  [1/2] Quick check (formatting, syntax)..."
    if "${QUICK_CHECK}"; then
        echo "  PASS: Quick checks passed"
    else
        echo "  FAIL: Quick checks failed"
        echo ""
        echo "Fix formatting and syntax issues first, then try committing again."
        echo "Run: .checks/scripts/quick-check.sh"
        exit 1
    fi
fi

# Stage 2: Full quality gate
if [ -f "${QUALITY_GATE}" ]; then
    echo "  [2/2] Full quality gate (security, tests, coverage)..."
    if "${QUALITY_GATE}"; then
        echo "  PASS: Quality gate passed"
    else
        echo "  FAIL: Quality gate failed"
        echo ""
        echo "Fix all issues before committing."
        echo "Run: .checks/scripts/quality-gate.sh"
        exit 1
    fi
fi

echo "PASS: All pre-commit checks passed"
exit 0

