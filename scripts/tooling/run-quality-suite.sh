#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

MODE="${1:---check}"

source "${ROOT_DIR}/scripts/tooling/ensure-tools.sh"

cd "${ROOT_DIR}"

if [[ -f pyproject.toml ]]; then
  uv pip install --system -e ".[test]" 2>/dev/null || uv pip install --system -e .
else
  uv pip install --system pytest ruff
fi

if [[ "${MODE}" == "--fix" ]]; then
  pinact run -u
  python -m ruff check --fix .
  python -m ruff format .
else
  pinact run --check
fi

actionlint -color

mapfile -t shellcheck_targets < <(rg --files -g "*.sh" "${ROOT_DIR}")
if (( ${#shellcheck_targets[@]} > 0 )); then
  shellcheck "${shellcheck_targets[@]}"
fi

zizmor .github/workflows

bandit -r src -lll

trivy fs \
  --scanners vuln,secret,misconfig,license \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --no-progress \
  "${ROOT_DIR}"

python -m ruff check .
python -m ruff format --check .

python -m pytest
