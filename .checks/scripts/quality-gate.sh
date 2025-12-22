#!/usr/bin/env bash
# Portable Quality Gate Script
# Reads configuration from checks-config.yaml or uses defaults

set -euo pipefail

# Determine script location and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Try to find repo root by looking for .checks directory or git root
if [ -d "${SCRIPT_DIR}/../../.checks" ]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
elif [ -d "${SCRIPT_DIR}/../../../.checks" ]; then
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
else
    # Fallback: assume we're in .checks/scripts/ and repo root is two levels up
    ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
fi

CONFIG_FILE="${ROOT_DIR}/checks-config.yaml"
TOOLS_SCRIPT="${SCRIPT_DIR}/tooling/setup-tools.sh"

# Source tools script if it exists
if [ -f "${TOOLS_SCRIPT}" ]; then
    # shellcheck source=/dev/null
    source "${TOOLS_SCRIPT}"
fi

cd "${ROOT_DIR}"

# Load configuration with defaults
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

# Load configuration values
COVERAGE_ENABLED=$(load_config ".quality_gate.coverage.enabled" "true")
COVERAGE_THRESHOLD=$(load_config ".quality_gate.coverage.threshold" "95")
COVERAGE_PATHS=$(load_config ".quality_gate.coverage.paths" "src")
PYTHON_ENABLED=$(load_config ".quality_gate.python.enabled" "true")
DOCKER_ENABLED=$(load_config ".quality_gate.docker.enabled" "true")
DOCKER_IMAGE_PATTERN=$(load_config ".quality_gate.docker.image_name_pattern" "")
SCAN_BASE_IMAGES=$(load_config ".quality_gate.docker.scan_base_images" "true")
SCAN_BUILT_IMAGES=$(load_config ".quality_gate.docker.scan_built_images" "true")

TOOL_PINACT=$(load_config ".quality_gate.tools.pinact" "true")
TOOL_ACTIONLINT=$(load_config ".quality_gate.tools.actionlint" "true")
TOOL_SHELLCHECK=$(load_config ".quality_gate.tools.shellcheck" "true")
TOOL_ZIZMOR=$(load_config ".quality_gate.tools.zizmor" "true")
TOOL_HADOLINT=$(load_config ".quality_gate.tools.hadolint" "true")
TOOL_TRIVY=$(load_config ".quality_gate.tools.trivy" "true")
TOOL_RUFF=$(load_config ".quality_gate.tools.ruff" "true")
TOOL_PYTEST=$(load_config ".quality_gate.tools.pytest" "true")
TOOL_MYPY=$(load_config ".quality_gate.tools.mypy" "false")
TOOL_BANDIT=$(load_config ".quality_gate.tools.bandit" "false")
TOOL_PIP_AUDIT=$(load_config ".quality_gate.tools.pip_audit" "false")
TOOL_NPM=$(load_config ".quality_gate.tools.npm" "true")

# Install project dependencies if Python is enabled
if [ "${PYTHON_ENABLED}" = "true" ] && [ -f pyproject.toml ]; then
    INSTALL_CMD=$(load_config ".quality_gate.python.install_command" "uv pip install --system -e .[test]")
    TEST_EXTRA=$(load_config ".quality_gate.python.test_extra" "test")
    
    echo "Installing Python dependencies..."
    if [ -n "${TEST_EXTRA}" ]; then
        eval "${INSTALL_CMD}" 2>/dev/null || eval "${INSTALL_CMD//\[test\]/.}" || true
    else
        eval "${INSTALL_CMD}" 2>/dev/null || true
    fi
elif [ "${PYTHON_ENABLED}" = "true" ]; then
    FALLBACK_INSTALL=$(load_config ".quality_gate.python.fallback_install" "uv pip install --system pytest ruff")
    echo "Installing basic Python tools..."
    eval "${FALLBACK_INSTALL}" 2>/dev/null || true
fi

# Pinact check
if [ "${TOOL_PINACT}" = "true" ]; then
    echo "Checking GitHub Actions pinning..."
    pinact run --check || {
        echo "ERROR: pinact found unpinned GitHub Actions"
        exit 1
    }
fi

# Actionlint
if [ "${TOOL_ACTIONLINT}" = "true" ]; then
    echo "Linting GitHub Actions workflows..."
    if [ -d .github/workflows ]; then
        actionlint -color || {
            echo "ERROR: actionlint found issues in GitHub Actions workflows"
            exit 1
        }
    fi
fi

# Shellcheck
if [ "${TOOL_SHELLCHECK}" = "true" ]; then
    echo "Linting shell scripts..."
    mapfile -t shellcheck_targets < <(find . -name "*.sh" -type f -not -path "./.git/*" -not -path "./.tools/*" -not -path "./.checks/*" 2>/dev/null || true)
    if (( ${#shellcheck_targets[@]} > 0 )); then
        shellcheck "${shellcheck_targets[@]}" || {
            echo "ERROR: shellcheck found issues in shell scripts"
            exit 1
        }
    fi
fi

# Zizmor
if [ "${TOOL_ZIZMOR}" = "true" ]; then
    echo "Scanning GitHub Actions for security issues..."
    if [ -d .github/workflows ]; then
        zizmor .github/workflows || {
            echo "ERROR: zizmor found security issues in GitHub Actions"
            exit 1
        }
    fi
fi

# Hadolint
if [ "${TOOL_HADOLINT}" = "true" ] && [ "${DOCKER_ENABLED}" = "true" ]; then
    echo "Linting Dockerfiles for security issues..."
    mapfile -t dockerfile_targets < <(find . -name "Dockerfile*" -type f -not -path "./.git/*" -not -path "./.tools/*" -not -path "./.checks/*" 2>/dev/null || true)
    if (( ${#dockerfile_targets[@]} > 0 )); then
        for dockerfile in "${dockerfile_targets[@]}"; do
            hadolint "${dockerfile}" || {
                echo "ERROR: hadolint found security issues in ${dockerfile}"
                exit 1
            }
        done
    fi
    
    # Test that Dockerfiles actually build
    if [ -f "${ROOT_DIR}/scripts/test-docker-builds.sh" ]; then
        echo ""
        echo "Testing Dockerfile builds..."
        "${ROOT_DIR}/scripts/test-docker-builds.sh" || {
            echo "ERROR: Docker build test failed"
            exit 1
        }
    fi
fi

# Trivy filesystem scan
if [ "${TOOL_TRIVY}" = "true" ]; then
    echo "Running Trivy security scan..."
    trivy fs \
        --scanners vuln,secret,misconfig \
        --severity HIGH,CRITICAL \
        --exit-code 1 \
        --no-progress \
        "${ROOT_DIR}" || {
        echo "ERROR: Trivy found HIGH or CRITICAL security issues"
        exit 1
    }
fi

# Trivy Docker scans
if [ "${TOOL_TRIVY}" = "true" ] && [ "${DOCKER_ENABLED}" = "true" ] && command -v docker >/dev/null 2>&1; then
    mapfile -t dockerfile_targets < <(find . -name "Dockerfile*" -type f -not -path "./.git/*" -not -path "./.checks/*" 2>/dev/null || true)
    
    # Scan base images
    if [ "${SCAN_BASE_IMAGES}" = "true" ] && (( ${#dockerfile_targets[@]} > 0 )); then
        echo "Scanning Docker base images..."
        mapfile -t docker_images < <(grep -h "^FROM" "${dockerfile_targets[@]}" 2>/dev/null | sed 's/^FROM //' | sed 's/ AS.*$//' | sort -u || true)
        if (( ${#docker_images[@]} > 0 )); then
            for image in "${docker_images[@]}"; do
                echo "  Scanning base image: ${image}"
                trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress "${image}" || true
            done
        fi
    fi
    
    # Scan built images
    if [ "${SCAN_BUILT_IMAGES}" = "true" ] && [ -n "${DOCKER_IMAGE_PATTERN}" ]; then
        if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "${DOCKER_IMAGE_PATTERN}"; then
            echo "Scanning built images matching '${DOCKER_IMAGE_PATTERN}'..."
            docker images --format "{{.Repository}}:{{.Tag}}" | grep "${DOCKER_IMAGE_PATTERN}" | while read -r image; do
                echo "  Scanning image: ${image}"
                trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress "${image}" || true
            done
        fi
    fi
    
    # Scan docker-compose files
    echo "Scanning docker-compose files for misconfigurations..."
    mapfile -t compose_files < <(find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml" 2>/dev/null || true)
    if (( ${#compose_files[@]} > 0 )); then
        for compose_file in "${compose_files[@]}"; do
            trivy config --severity HIGH,CRITICAL --exit-code 1 --no-progress "${compose_file}" || {
                echo "ERROR: Trivy found HIGH or CRITICAL issues in ${compose_file}"
                exit 1
            }
        done
    fi
fi

# Ruff - run in Docker
if [ "${TOOL_RUFF}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Running ruff checks in Docker container..."
    # Build test container if needed
    docker-compose build test >/dev/null 2>&1 || true
    docker-compose --profile test run --rm test python -m ruff check . || {
        echo "ERROR: ruff found linting issues"
        exit 1
    }
    docker-compose --profile test run --rm test python -m ruff format --check . || {
        echo "ERROR: ruff found formatting issues"
        exit 1
    }
fi

# Mypy type checking - run in Docker
if [ "${TOOL_MYPY}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Running mypy type checking in Docker container..."
    docker-compose build test >/dev/null 2>&1 || true
    docker-compose --profile test run --rm test python -m mypy src/ || {
        echo "ERROR: mypy found type errors"
        exit 1
    }
fi

# Bandit security linting - run in Docker
if [ "${TOOL_BANDIT}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Running bandit security scan in Docker container..."
    docker-compose build test >/dev/null 2>&1 || true
    # shellcheck disable=SC2034
    BANDIT_SEVERITY=$(load_config ".quality_gate.tools.bandit_severity" "HIGH")
    docker-compose --profile test run --rm test sh -c "uv pip install --system 'bandit[toml]' >/dev/null 2>&1 && bandit -r src/ -ll -i -q" || {
        echo "ERROR: bandit found security issues"
        exit 1
    }
fi

# pip-audit dependency vulnerabilities - run in Docker
if [ "${TOOL_PIP_AUDIT}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Auditing Python dependencies in Docker container..."
    docker-compose build test >/dev/null 2>&1 || true
    docker-compose --profile test run --rm test sh -c "uv pip install --system pip-audit >/dev/null 2>&1 && pip-audit --desc --format json --output pip-audit-report.json" || {
        echo "ERROR: pip-audit found vulnerabilities"
        exit 1
    }
fi

# npm dependency checks
if [ "${TOOL_NPM}" = "true" ]; then
    check_npm_dependencies() {
        if [ -f "frontend/package.json" ]; then
            echo "Checking npm dependencies..."
            cd frontend || return 0
            
            # Check if node_modules exists, if not install dependencies
            if [ ! -d "node_modules" ]; then
                echo "Installing npm dependencies..."
                npm ci >/dev/null 2>&1 || npm install >/dev/null 2>&1 || {
                    echo "WARNING: Failed to install npm dependencies, skipping checks"
                    cd ..
                    return 0
                }
            fi
            
            # Check for deprecated packages
            if npm outdated 2>&1 | grep -q "deprecated"; then
                echo "WARNING: npm found deprecated packages:"
                npm outdated 2>&1 | grep "deprecated" || true
            fi
            
            # Check for vulnerabilities (moderate or higher)
            if ! npm audit --audit-level=moderate --dry-run >/dev/null 2>&1; then
                echo "ERROR: npm audit found moderate or higher severity vulnerabilities"
                npm audit --audit-level=moderate
                cd ..
                return 1
            fi
            
            cd ..
        fi
        return 0
    }

    # Run npm dependency checks
    check_npm_dependencies || {
        echo "ERROR: npm dependency checks failed"
        exit 1
    }
fi

# Pytest with coverage - run in Docker
if [ "${TOOL_PYTEST}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ] && [ "${COVERAGE_ENABLED}" = "true" ]; then
    echo "Running tests in Docker container..."
    COVERAGE_CMD=$(load_config ".quality_gate.coverage.command" "pytest")
    COVERAGE_ARGS=$(load_config ".quality_gate.coverage.args" "--cov --cov-report=term-missing --cov-report=xml")
    
    # Build coverage paths argument
    COV_PATHS=""
    if [ -f "${CONFIG_FILE}" ]; then
        # Try to get paths from config
        if command -v yq >/dev/null 2>&1; then
            COV_PATHS=$(yq eval '.quality_gate.coverage.paths[]' "${CONFIG_FILE}" 2>/dev/null | tr '\n' ' ' || echo "")
        fi
    fi
    
    if [ -z "${COV_PATHS}" ]; then
        COV_PATHS="${COVERAGE_PATHS}"
    fi
    
    # Create coverage directory
    mkdir -p "${ROOT_DIR}/coverage"
    
    # Build test container if needed
    docker-compose build test >/dev/null 2>&1 || true
    
    # Run tests with coverage in Docker
    if [ -n "${COV_PATHS}" ]; then
        docker-compose --profile test run --rm test python -m "${COVERAGE_CMD}" --cov="${COV_PATHS}" "${COVERAGE_ARGS}" || {
            echo "ERROR: Tests failed"
            exit 1
        }
    else
        docker-compose --profile test run --rm test python -m "${COVERAGE_CMD}" "${COVERAGE_ARGS}" || {
            echo "ERROR: Tests failed"
            exit 1
        }
    fi
    
    # Check coverage threshold
    echo "Checking test coverage..."
    if [ ! -f "coverage.xml" ]; then
        echo "ERROR: coverage.xml not found. Tests must generate coverage report."
        exit 1
    fi
    
    COVERAGE=$(python -c "
import xml.etree.ElementTree as ET
import sys
try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    line_rate = root.attrib.get('line-rate', '0')
    if not line_rate:
        # Try branch-rate as fallback
        line_rate = root.attrib.get('branch-rate', '0')
    print(line_rate)
except Exception as e:
    print('0', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null || echo "0")
    
    COVERAGE_PCT=$(python -c "
try:
    rate = float('${COVERAGE}')
    pct = int(rate * 100)
    print(pct)
except:
    print(0)
" 2>/dev/null || echo "0")
    
    if [ "${COVERAGE_PCT}" -lt "${COVERAGE_THRESHOLD}" ]; then
        echo "ERROR: Test coverage is ${COVERAGE_PCT}%, but required threshold is ${COVERAGE_THRESHOLD}%"
        echo "       Coverage must be at least ${COVERAGE_THRESHOLD}% to pass quality gates."
        exit 1
    fi
    
    echo "SUCCESS: All quality gates passed!"
    echo "   - Coverage: ${COVERAGE_PCT}%"
else
    echo "SUCCESS: All quality gates passed!"
fi

