#!/usr/bin/env bash
# Script to trigger Renovate workflow and poll for results
#
# Usage:
#   ./scripts/run-renovate.sh [--dry-run] [--include-major] [--timeout SECONDS]
#
# Options:
#   --dry-run        Run in dry-run mode (no PRs created)
#   --include-major   Include major version updates
#   --timeout        Maximum time to wait for workflow completion (default: 600 seconds)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DRY_RUN="false"
INCLUDE_MAJOR="false"
TIMEOUT=600
WORKFLOW_NAME="renovate.yml"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --include-major)
      INCLUDE_MAJOR="true"
      shift
      ;;
    --timeout)
      TIMEOUT="$2"
      shift 2
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Usage: $0 [--dry-run] [--include-major] [--timeout SECONDS]"
      exit 1
      ;;
  esac
done

# Check if gh CLI is installed and authenticated
if ! command -v gh &> /dev/null; then
  echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
  echo "Install it from: https://cli.github.com/"
  exit 1
fi

if ! gh auth status &> /dev/null; then
  echo -e "${RED}Error: GitHub CLI is not authenticated${NC}"
  echo "Run: gh auth login"
  exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
  echo -e "${RED}Error: Could not determine repository${NC}"
  echo "Make sure you're in a git repository and gh is configured"
  exit 1
fi

echo -e "${BLUE}Repository: ${REPO}${NC}"
echo -e "${BLUE}Workflow: ${WORKFLOW_NAME}${NC}"
echo -e "${BLUE}Dry Run: ${DRY_RUN}${NC}"
echo -e "${BLUE}Include Major: ${INCLUDE_MAJOR}${NC}"
echo -e "${BLUE}Timeout: ${TIMEOUT} seconds${NC}"
echo ""

# Trigger the workflow
echo -e "${YELLOW}Triggering Renovate workflow...${NC}"
WORKFLOW_OUTPUT=$(gh workflow run "$WORKFLOW_NAME" \
  --repo "$REPO" \
  --field "dry_run=$DRY_RUN" \
  --field "include_major=$INCLUDE_MAJOR" \
  2>&1)

echo "$WORKFLOW_OUTPUT"

# Extract run ID from output or wait and get it
RUN_ID=$(echo "$WORKFLOW_OUTPUT" | grep -oE 'Created workflow_dispatch event for workflow file [0-9]+' | grep -oE '[0-9]+' || echo "")

if [ -z "$RUN_ID" ]; then
  # Try alternative method to get run ID - wait a moment for workflow to start
  echo -e "${YELLOW}Waiting for workflow to start...${NC}"
  sleep 3
  RUN_ID=$(gh run list --workflow "$WORKFLOW_NAME" --limit 1 --json databaseId,status --jq '.[0].databaseId' 2>/dev/null || echo "")
fi

if [ -z "$RUN_ID" ] || [ "$RUN_ID" == "null" ]; then
  echo -e "${RED}Error: Could not get workflow run ID${NC}"
  echo "Check if the workflow exists and you have permission to trigger it"
  exit 1
fi

echo -e "${GREEN}Workflow triggered successfully!${NC}"
echo -e "${BLUE}Run ID: ${RUN_ID}${NC}"
echo -e "${BLUE}View run: https://github.com/${REPO}/actions/runs/${RUN_ID}${NC}"
echo ""

# Poll for completion
echo -e "${YELLOW}Waiting for workflow to complete...${NC}"
START_TIME=$(date +%s)
ELAPSED=0
LAST_STATUS=""

while [ $ELAPSED -lt $TIMEOUT ]; do
  RUN_STATUS=$(gh run view "$RUN_ID" --repo "$REPO" --json status,conclusion --jq -r '.status' 2>/dev/null || echo "unknown")
  RUN_CONCLUSION=$(gh run view "$RUN_ID" --repo "$REPO" --json status,conclusion --jq -r '.conclusion // "none"' 2>/dev/null || echo "none")
  STATUS="${RUN_STATUS}/${RUN_CONCLUSION}"
  
  if [ "$STATUS" != "$LAST_STATUS" ]; then
    echo -e "${BLUE}[$(date +%H:%M:%S)] Status: ${STATUS}${NC}"
    LAST_STATUS="$STATUS"
  fi
  
  # Check if completed
  if [ "$RUN_STATUS" = "completed" ]; then
    if [ "$RUN_CONCLUSION" = "success" ]; then
    echo ""
    echo -e "${GREEN}✓ Workflow completed successfully!${NC}"
    echo ""
    
    # Get summary
    echo -e "${BLUE}Fetching run summary...${NC}"
    gh run view "$RUN_ID" --repo "$REPO" --log || true
    
    # Check for created PRs
    echo ""
    echo -e "${BLUE}Checking for created pull requests...${NC}"
    PRS=$(gh pr list --repo "$REPO" --head "renovate/" --json number,title,state --jq '.[] | "\(.number): \(.title) (\(.state))"' 2>/dev/null || echo "")
    
    if [ -n "$PRS" ]; then
      echo -e "${GREEN}Created/Updated Pull Requests:${NC}"
      echo "$PRS" | while IFS= read -r pr; do
        echo "  - $pr"
      done
    else
      if [ "$DRY_RUN" == "true" ]; then
        echo -e "${YELLOW}Dry run mode: No PRs created${NC}"
      else
        echo -e "${YELLOW}No new PRs found (may already exist or no updates needed)${NC}"
      fi
    fi
    
      exit 0
    else
      # Completed but not success (failure, cancelled, etc.)
      echo ""
      echo -e "${RED}✗ Workflow completed with status: ${RUN_CONCLUSION}${NC}"
      echo -e "${BLUE}Status: ${STATUS}${NC}"
      echo ""
      echo -e "${YELLOW}Last 50 lines of logs:${NC}"
      gh run view "$RUN_ID" --repo "$REPO" --log --tail 50 || true
      exit 1
    fi
  fi
  
  sleep 5
  ELAPSED=$(($(date +%s) - START_TIME))
done

echo ""
echo -e "${RED}✗ Timeout after ${TIMEOUT} seconds${NC}"
echo -e "${BLUE}Workflow may still be running. Check: https://github.com/${REPO}/actions/runs/${RUN_ID}${NC}"
exit 1

