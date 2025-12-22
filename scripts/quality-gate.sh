#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "${ROOT_DIR}/scripts/tooling/ensure-tools.sh"

cd "${ROOT_DIR}"

# Install project and test dependencies
if [[ -f pyproject.toml ]]; then
  # Try [test] extra first, fallback to basic editable install
  uv pip install --system -e ".[test]" 2>/dev/null || uv pip install --system -e .
else
  # If no pyproject.toml yet, install tools needed for quality gates
  uv pip install --system pytest ruff
fi

pinact run --check

actionlint -color

mapfile -t shellcheck_targets < <(rg --files -g "*.sh" "${ROOT_DIR}")
if (( ${#shellcheck_targets[@]} > 0 )); then
  shellcheck "${shellcheck_targets[@]}"
fi

zizmor .github/workflows

trivy fs \
  --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --no-progress \
  "${ROOT_DIR}"

python -m ruff check .
python -m ruff format --check .

python -m pytest
