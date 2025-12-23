#!/usr/bin/env bash
# Checks Installation Script
# Installs checks tools into a repository

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Installing checks tools..."

# Create checks directory in repo root if it doesn't exist
CHECKS_DIR="${REPO_ROOT}/.checks"
if [ ! -d "${CHECKS_DIR}" ]; then
    mkdir -p "${CHECKS_DIR}"
fi

# Copy scripts
echo "  Copying scripts..."
cp -r "${SCRIPT_DIR}/scripts" "${CHECKS_DIR}/" || {
    echo "ERROR: Failed to copy scripts"
    exit 1
}

# Copy templates
echo "  Copying templates..."
cp -r "${SCRIPT_DIR}/templates" "${CHECKS_DIR}/" || {
    echo "ERROR: Failed to copy templates"
    exit 1
}

# Create config file if it doesn't exist
CONFIG_FILE="${REPO_ROOT}/checks-config.yaml"
if [ ! -f "${CONFIG_FILE}" ]; then
    echo "  Creating checks-config.yaml..."
    cp "${CHECKS_DIR}/templates/checks-config.yaml.example" "${CONFIG_FILE}"
    echo "  Please customize ${CONFIG_FILE} for your repository"
else
    echo "  checks-config.yaml already exists, skipping"
fi

# Make scripts executable
chmod +x "${CHECKS_DIR}/scripts/"*.sh
chmod +x "${CHECKS_DIR}/scripts/tooling/"*.sh

echo "SUCCESS: Checks tools installed to ${CHECKS_DIR}"
echo ""
echo "Next steps:"
echo "  1. Customize ${CONFIG_FILE} for your repository"
echo "  2. Run: .checks/scripts/orchestrator.sh --auto-fix"
echo "  3. Install pre-commit hooks if desired"

