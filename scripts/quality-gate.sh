#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

source "${ROOT_DIR}/scripts/tooling/setup-tools.sh"

cd "${ROOT_DIR}"

# Install project and test dependencies
if [[ -f pyproject.toml ]]; then
  # Try [test] extra first, fallback to basic editable install
  uv pip install --system -e ".[test]" 2>/dev/null || uv pip install --system -e .
else
  # If no pyproject.toml yet, install tools needed for quality gates
  uv pip install --system pytest ruff
fi

# Pinact check - ensure GitHub Actions are SHA-pinned
echo "Checking GitHub Actions pinning..."
pinact run --check

# Actionlint - lint GitHub Actions workflows
echo "Linting GitHub Actions workflows..."
if [ -d .github/workflows ]; then
  actionlint -color || {
    echo "ERROR: actionlint found issues in GitHub Actions workflows"
    exit 1
  }
fi

# Shellcheck - lint shell scripts
echo "Linting shell scripts..."
shellcheck_targets=()
while IFS= read -r file; do
  [ -n "$file" ] && shellcheck_targets+=("$file")
done <<< "$(find . -name "*.sh" -type f -not -path "./.git/*" -not -path "./.tools/*" 2>/dev/null || true)"
if (( ${#shellcheck_targets[@]} > 0 )); then
  shellcheck "${shellcheck_targets[@]}" || {
    echo "ERROR: shellcheck found issues in shell scripts"
    exit 1
  }
fi

# Zizmor - security scan GitHub Actions
echo "Scanning GitHub Actions for security issues..."
if [ -d .github/workflows ]; then
  zizmor .github/workflows || {
    echo "ERROR: zizmor found security issues in GitHub Actions"
    exit 1
  }
fi

# Hadolint - Dockerfile security linting
echo "Linting Dockerfiles for security issues..."
dockerfile_targets=()
while IFS= read -r file; do
  [ -n "$file" ] && dockerfile_targets+=("$file")
done <<< "$(find . -name "Dockerfile*" -type f -not -path "./.git/*" -not -path "./.tools/*" 2>/dev/null || true)"
if (( ${#dockerfile_targets[@]} > 0 )); then
  for dockerfile in "${dockerfile_targets[@]}"; do
    hadolint "${dockerfile}" || {
      echo "ERROR: hadolint found security issues in ${dockerfile}"
      exit 1
    }
  done
fi

# Trivy - comprehensive security scan (SCA + SAST) including Docker
echo "Running Trivy security scan (filesystem, Docker images, and configs)..."
trivy fs \
  --scanners vuln,secret,misconfig \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  --no-progress \
  "${ROOT_DIR}" || {
  echo "ERROR: Trivy found HIGH or CRITICAL security issues"
  exit 1
}

# Trivy - scan Docker images if they exist
echo "Scanning Docker images for vulnerabilities..."
if command -v docker >/dev/null 2>&1; then
  # Scan base images used in Dockerfiles
  docker_images=()
  while IFS= read -r image; do
    docker_images+=("$image")
  done < <(grep -h "^FROM" "${dockerfile_targets[@]}" 2>/dev/null | sed 's/^FROM //' | sed 's/ AS.*$//' | sort -u || true)
  if (( ${#docker_images[@]} > 0 )); then
    for image in "${docker_images[@]}"; do
      echo "  Scanning base image: ${image}"
      trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress "${image}" || true
    done
  fi
  
  # Scan built images if they exist
  if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "brain-radio"; then
    echo "Scanning built brain-radio images..."
    docker images --format "{{.Repository}}:{{.Tag}}" | grep "brain-radio" | while read -r image; do
      echo "  Scanning image: ${image}"
      trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress "${image}" || true
    done
  fi
fi

# Trivy - scan docker-compose files
echo "Scanning docker-compose files for misconfigurations..."
compose_files=()
while IFS= read -r file; do
  [ -n "$file" ] && compose_files+=("$file")
done <<< "$(find . \( -name "docker-compose*.yml" -o -name "docker-compose*.yaml" \) 2>/dev/null || true)"
if (( ${#compose_files[@]} > 0 )); then
  for compose_file in "${compose_files[@]}"; do
    trivy config --severity HIGH,CRITICAL --exit-code 1 -q "${compose_file}" || {
      echo "ERROR: Trivy found HIGH or CRITICAL issues in ${compose_file}"
      exit 1
    }
  done
fi

# Ruff - Python linting and formatting (run in Docker)
echo "Running ruff checks in Docker container..."
docker-compose build test >/dev/null 2>&1 || true
docker-compose --profile test run --rm test python -m ruff check . || {
  echo "ERROR: ruff found linting issues"
  exit 1
}
docker-compose --profile test run --rm test python -m ruff format --check . || {
  echo "ERROR: ruff found formatting issues"
  exit 1
}

# Pytest - run tests with coverage in Docker
echo "Running tests in Docker container..."
mkdir -p coverage
if "${ROOT_DIR}/scripts/test-docker.sh" docker-compose.yml --cov=src/brain_radio --cov-report=term-missing --cov-report=xml:coverage/coverage.xml --cov-report=html:coverage/htmlcov -v; then
  echo "Tests passed"
else
  echo "ERROR: Tests failed"
  exit 1
fi

# Check coverage threshold (95%)
echo "Checking test coverage..."
COVERAGE_THRESHOLD=95
COVERAGE_XML="${ROOT_DIR}/coverage/coverage.xml"
if [ -f "${COVERAGE_XML}" ]; then
  COVERAGE=$(python3 -c "import xml.etree.ElementTree as ET; import os; tree = ET.parse('${COVERAGE_XML}'); root = tree.getroot(); print(root.attrib.get('line-rate', '0'))" 2>/dev/null || echo "0")
  COVERAGE_PCT=$(python3 -c "print(int(float('${COVERAGE}') * 100))" 2>/dev/null || echo "0")
else
  # Try to get coverage from container
  COVERAGE=$(docker-compose --profile test run --rm test python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage/coverage.xml'); root = tree.getroot(); print(root.attrib.get('line-rate', '0'))" 2>/dev/null || echo "0")
  COVERAGE_PCT=$(python3 -c "print(int(float('${COVERAGE}') * 100))" 2>/dev/null || echo "0")
fi

if [ "${COVERAGE_PCT}" -lt "${COVERAGE_THRESHOLD}" ]; then
  echo "ERROR: Test coverage is ${COVERAGE_PCT}%, but required threshold is ${COVERAGE_THRESHOLD}%"
  exit 1
fi

echo "SUCCESS: All quality gates passed!"
echo "   - Coverage: ${COVERAGE_PCT}%"
