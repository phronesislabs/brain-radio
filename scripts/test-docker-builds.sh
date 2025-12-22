#!/usr/bin/env bash
# Test that all Dockerfiles can actually build
# This catches build-time errors before users try to run the app

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FAILED=0
PASSED=0
SKIPPED=0

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Docker Build Test                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Find all Dockerfiles
mapfile -t dockerfiles < <(find . -name "Dockerfile*" -type f -not -path "./.git/*" -not -path "./.checks/*" -not -path "./node_modules/*" -not -path "./frontend/node_modules/*" 2>/dev/null | sort)

if [ ${#dockerfiles[@]} -eq 0 ]; then
    echo -e "${YELLOW}No Dockerfiles found${NC}"
    exit 0
fi

echo -e "Found ${#dockerfiles[@]} Dockerfile(s) to test"
echo ""

# Test each Dockerfile
for dockerfile in "${dockerfiles[@]}"; do
    dockerfile_dir=$(dirname "${dockerfile}")
    dockerfile_name=$(basename "${dockerfile}")
    build_context="${dockerfile_dir}"
    
    # Determine image name
    if [[ "${dockerfile}" == *"Dockerfile.dev"* ]]; then
        image_name="brain-radio-test-$(basename "${dockerfile_dir}")-dev"
    elif [[ "${dockerfile}" == *"Dockerfile.test"* ]]; then
        image_name="brain-radio-test"
    elif [[ "${dockerfile}" == *"Dockerfile.backend"* ]]; then
        image_name="brain-radio-backend-test"
    elif [[ "${dockerfile}" == *"frontend"* ]]; then
        image_name="brain-radio-frontend-test"
    else
        image_name="brain-radio-$(basename "${dockerfile_dir}")-test"
    fi
    
    # Clean up image name
    image_name=$(echo "${image_name}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g' | sed 's/--*/-/g')
    
    echo -e "${BLUE}Testing: ${dockerfile}${NC}"
    echo -e "  Context: ${build_context}"
    echo -e "  Image: ${image_name}"
    
    # Special handling for frontend Dockerfiles
    if [[ "${dockerfile}" == *"frontend"* ]]; then
        # Check if package.json exists
        if [ ! -f "${build_context}/package.json" ]; then
            echo -e "  ${YELLOW}SKIP: package.json not found${NC}"
            SKIPPED=$((SKIPPED + 1))
            echo ""
            continue
        fi
    fi
    
    # Build the image
    if docker build \
        --file "${dockerfile}" \
        --tag "${image_name}:test" \
        --quiet \
        "${build_context}" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Build successful${NC}"
        PASSED=$((PASSED + 1))
        
        # Clean up test image
        docker rmi "${image_name}:test" >/dev/null 2>&1 || true
    else
        echo -e "  ${RED}✗ Build failed${NC}"
        FAILED=$((FAILED + 1))
        
        # Show build output for debugging
        echo -e "  ${YELLOW}Build output:${NC}"
        if docker build \
            --file "${dockerfile}" \
            --tag "${image_name}:test" \
            "${build_context}" 2>&1 | tail -20; then
            # If it succeeds on retry, mark as passed
            echo -e "  ${GREEN}✓ Build successful on retry${NC}"
            PASSED=$((PASSED + 1))
            FAILED=$((FAILED - 1))
            docker rmi "${image_name}:test" >/dev/null 2>&1 || true
        fi
    fi
    echo ""
done

# Summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Build Test Summary                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${GREEN}Passed: ${PASSED}${NC}"
if [ ${SKIPPED} -gt 0 ]; then
    echo -e "  ${YELLOW}Skipped: ${SKIPPED}${NC}"
fi
if [ ${FAILED} -gt 0 ]; then
    echo -e "  ${RED}Failed: ${FAILED}${NC}"
    echo ""
    echo -e "${RED}ERROR: Some Dockerfiles failed to build${NC}"
    echo "This should be caught before committing. Run this test locally:"
    echo "  ./scripts/test-docker-builds.sh"
    exit 1
else
    echo -e "  ${GREEN}All Dockerfiles build successfully!${NC}"
    exit 0
fi

