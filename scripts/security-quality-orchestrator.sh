#!/usr/bin/env bash
# Security and Quality Orchestrator Script
# This script automates security scanning, linting, and quality checks
# Can be used portably across multiple repositories

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AUTO_FIX=${AUTO_FIX:-false}
AUTO_COMMIT=${AUTO_COMMIT:-false}
CREATE_PR=${CREATE_PR:-false}
MAX_ITERATIONS=${MAX_ITERATIONS:-10}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Setup all tools
setup_tools() {
    log_info "Setting up all required tools..."
    "${SCRIPT_DIR}/tooling/setup-tools.sh"
    log_success "Tools setup complete"
}

# Run pinact to update and pin GitHub Actions
update_pinned_actions() {
    log_info "Updating and pinning GitHub Actions..."
    if pinact run -u; then
        if git diff --quiet .github/workflows/; then
            log_success "GitHub Actions are up to date"
        else
            log_warning "GitHub Actions were updated"
            if [ "${AUTO_COMMIT}" = "true" ]; then
                git add .github/workflows/
                git commit -m "chore: update pinned GitHub Actions" || true
            fi
        fi
    else
        log_error "Failed to update GitHub Actions"
        return 1
    fi
}

# Run zizmor scan
scan_actions_security() {
    log_info "Scanning GitHub Actions with zizmor..."
    if [ -d .github/workflows ]; then
        if zizmor .github/workflows; then
            log_success "Zizmor scan passed"
        else
            log_error "Zizmor found security issues"
            if [ "${AUTO_FIX}" = "true" ]; then
                log_warning "Auto-fix enabled, but zizmor issues require manual review"
            fi
            return 1
        fi
    else
        log_warning "No .github/workflows directory found"
    fi
}

# Run hadolint on Dockerfiles
run_hadolint() {
    log_info "Running hadolint on Dockerfiles..."
    mapfile -t dockerfile_targets < <(find . -name "Dockerfile*" -type f -not -path "./.git/*" -not -path "./.tools/*" 2>/dev/null || true)
    if (( ${#dockerfile_targets[@]} > 0 )); then
        local errors=0
        for dockerfile in "${dockerfile_targets[@]}"; do
            if hadolint "${dockerfile}" 2>&1 | tee "hadolint-$(basename "${dockerfile}").txt"; then
                log_success "  ${dockerfile} passed"
            else
                log_error "  ${dockerfile} found issues"
                errors=$((errors + 1))
            fi
        done
        return ${errors}
    else
        log_info "No Dockerfiles found"
        return 0
    fi
}

# Run trivy security scan
run_trivy_scan() {
    log_info "Running Trivy security scan (SCA + SAST + Docker)..."
    local errors=0
    
    # Filesystem scan
    if trivy fs \
        --scanners vuln,secret,misconfig \
        --severity HIGH,CRITICAL \
        --exit-code 0 \
        --no-progress \
        --format table \
        "${ROOT_DIR}" > trivy-fs-report.txt 2>&1; then
        log_success "Trivy filesystem scan completed (no HIGH/CRITICAL issues)"
    else
        log_error "Trivy found HIGH or CRITICAL security issues in filesystem"
        cat trivy-fs-report.txt
        errors=$((errors + 1))
    fi
    
    # Docker compose config scan
    mapfile -t compose_files < <(find . -name "docker-compose*.yml" -o -name "docker-compose*.yaml" 2>/dev/null || true)
    if (( ${#compose_files[@]} > 0 )); then
        for compose_file in "${compose_files[@]}"; do
            log_info "  Scanning ${compose_file}..."
            if trivy config --severity HIGH,CRITICAL --exit-code 0 --no-progress --format table "${compose_file}" > "trivy-config-$(basename "${compose_file}").txt" 2>&1; then
                log_success "  ${compose_file} passed"
            else
                log_error "  ${compose_file} found issues"
                cat "trivy-config-$(basename "${compose_file}").txt"
                errors=$((errors + 1))
            fi
        done
    fi
    
    # Docker image scan (if docker is available)
    if command -v docker >/dev/null 2>&1; then
        mapfile -t dockerfile_targets < <(find . -name "Dockerfile*" -type f -not -path "./.git/*" 2>/dev/null || true)
        if (( ${#dockerfile_targets[@]} > 0 )); then
            mapfile -t docker_images < <(grep -h "^FROM" "${dockerfile_targets[@]}" 2>/dev/null | sed 's/^FROM //' | sed 's/ AS.*$//' | sort -u || true)
            if (( ${#docker_images[@]} > 0 )); then
                log_info "Scanning Docker base images..."
                for image in "${docker_images[@]}"; do
                    log_info "  Scanning ${image}..."
                    trivy image --severity HIGH,CRITICAL --exit-code 0 --no-progress --format table "${image}" > "trivy-image-$(echo "${image}" | tr '/:' '_').txt" 2>&1 || true
                done
            fi
        fi
    fi
    
    if [ ${errors} -gt 0 ]; then
        if [ "${AUTO_FIX}" = "true" ]; then
            log_warning "Auto-fix enabled, but security issues require manual remediation"
        fi
        return 1
    fi
    
    return 0
}

# Run linting tools
run_linters() {
    log_info "Running linters..."
    local errors=0

    # Actionlint
    log_info "  Running actionlint..."
    if [ -d .github/workflows ]; then
        if actionlint -color 2>&1 | tee actionlint-report.txt; then
            log_success "  actionlint passed"
        else
            log_error "  actionlint found issues"
            errors=$((errors + 1))
        fi
    fi

    # Shellcheck
    log_info "  Running shellcheck..."
    mapfile -t shellcheck_targets < <(find . -name "*.sh" -type f -not -path "./.git/*" -not -path "./.tools/*" 2>/dev/null || true)
    if (( ${#shellcheck_targets[@]} > 0 )); then
        if shellcheck "${shellcheck_targets[@]}" 2>&1 | tee shellcheck-report.txt; then
            log_success "  shellcheck passed"
        else
            log_error "  shellcheck found issues"
            if [ "${AUTO_FIX}" = "true" ]; then
                log_warning "  Some shellcheck issues may be auto-fixable"
            fi
            errors=$((errors + 1))
        fi
    fi

    # Ruff (Python)
    log_info "  Running ruff..."
    if command -v ruff >/dev/null 2>&1 || uv pip install --system ruff >/dev/null 2>&1; then
        if [ "${AUTO_FIX}" = "true" ]; then
            python -m ruff check --fix . 2>&1 | tee ruff-check-report.txt || true
            python -m ruff format . 2>&1 | tee ruff-format-report.txt || true
        else
            python -m ruff check . 2>&1 | tee ruff-check-report.txt || true
            python -m ruff format --check . 2>&1 | tee ruff-format-report.txt || true
        fi
        if [ "${PIPESTATUS[0]}" -eq 0 ] && [ "${PIPESTATUS[1]}" -eq 0 ]; then
            log_success "  ruff passed"
        else
            log_error "  ruff found issues"
            errors=$((errors + 1))
        fi
    fi

    return ${errors}
}

# Run pre-commit hooks
run_precommit() {
    log_info "Running pre-commit hooks..."
    if command -v pre-commit >/dev/null 2>&1; then
        if [ "${AUTO_FIX}" = "true" ]; then
            if pre-commit run --all-files; then
                log_success "Pre-commit hooks passed"
                return 0
            else
                log_error "Pre-commit hooks failed"
                return 1
            fi
        else
            if pre-commit run --all-files; then
                log_success "Pre-commit hooks passed"
                return 0
            else
                log_error "Pre-commit hooks failed"
                return 1
            fi
        fi
    else
        log_warning "pre-commit not installed, skipping"
        return 0
    fi
}

# Run quality gate
run_quality_gate() {
    log_info "Running quality gate..."
    if "${SCRIPT_DIR}/quality-gate.sh"; then
        log_success "Quality gate passed"
        return 0
    else
        log_error "Quality gate failed"
        return 1
    fi
}

# Main orchestration function
main() {
    cd "${ROOT_DIR}"

    log_info "Starting Security and Quality Orchestrator"
    log_info "Root directory: ${ROOT_DIR}"
    log_info "Auto-fix: ${AUTO_FIX}"
    log_info "Auto-commit: ${AUTO_COMMIT}"
    log_info "Create PR: ${CREATE_PR}"

    # Setup tools
    setup_tools

    # Track if we need to commit changes
    local needs_commit=false
    local iteration=0

    # Main loop - run until clean or max iterations
    while [ "${iteration}" -lt "${MAX_ITERATIONS}" ]; do
        iteration=$((iteration + 1))
        log_info "Iteration ${iteration}/${MAX_ITERATIONS}"

        # Update pinned actions
        if update_pinned_actions; then
            if ! git diff --quiet .github/workflows/ 2>/dev/null; then
                needs_commit=true
            fi
        fi

        # Run security scans
        local security_errors=0
        scan_actions_security || security_errors=$((security_errors + 1))
        run_hadolint || security_errors=$((security_errors + 1))
        run_trivy_scan || security_errors=$((security_errors + 1))

        # Run linters (with auto-fix if enabled)
        local lint_errors=0
        run_linters || lint_errors=$((lint_errors + 1))

        # Run pre-commit
        local precommit_errors=0
        run_precommit || precommit_errors=$((precommit_errors + 1))

        # Run quality gate
        local quality_errors=0
        run_quality_gate || quality_errors=$((quality_errors + 1))

        # Check if everything passed
        if [ ${security_errors} -eq 0 ] && [ ${lint_errors} -eq 0 ] && [ ${precommit_errors} -eq 0 ] && [ ${quality_errors} -eq 0 ]; then
            log_success "All checks passed!"

            # Commit changes if needed and enabled
            if [ "${needs_commit}" = "true" ] && [ "${AUTO_COMMIT}" = "true" ]; then
                log_info "Committing changes..."
                git add -A
                git commit -m "chore: apply security and quality fixes" || true
                needs_commit=false
            fi

            # Create PR if enabled
            if [ "${CREATE_PR}" = "true" ] && [ "${needs_commit}" = "false" ]; then
                log_info "All changes committed, skipping PR creation"
            elif [ "${CREATE_PR}" = "true" ]; then
                log_warning "PR creation not implemented yet (requires GitHub CLI or API)"
            fi

            return 0
        else
            log_warning "Some checks failed. Security errors: ${security_errors}, Lint errors: ${lint_errors}, Pre-commit errors: ${precommit_errors}, Quality errors: ${quality_errors}"

            if [ "${AUTO_FIX}" = "true" ] && [ "${iteration}" -lt "${MAX_ITERATIONS}" ]; then
                log_info "Auto-fix enabled, attempting to fix issues..."
                # Give tools a chance to auto-fix
                sleep 1
            else
                log_error "Maximum iterations reached or auto-fix disabled"
                return 1
            fi
        fi
    done

    log_error "Failed to resolve all issues after ${MAX_ITERATIONS} iterations"
    return 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --auto-fix)
            AUTO_FIX=true
            shift
            ;;
        --auto-commit)
            AUTO_COMMIT=true
            shift
            ;;
        --create-pr)
            CREATE_PR=true
            shift
            ;;
        --max-iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto-fix          Enable auto-fix for tools that support it"
            echo "  --auto-commit       Automatically commit fixes"
            echo "  --create-pr         Create a PR with fixes (not implemented)"
            echo "  --max-iterations N  Maximum number of fix iterations (default: 10)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"

