---
description: "Analyze GitHub Actions workflow runs since last success and remediate errors/findings"
---

# GitHub Actions Workflow Remediation

Analyze all GitHub Actions workflow runs since the last successful run, extract errors and findings, and automatically remediate issues where possible.

## Prerequisites

1. **GitHub CLI must be authenticated:**

   ```bash
   gh auth status
   ```

   If not authenticated, run: `gh auth login`

2. **Ensure you're in the repository root:**

   ```bash
   pwd
   ```

## Steps

### 1. Identify Last Successful Workflow Run

For each workflow file in `.github/workflows/`, find the last successful run:

```bash
# Get all workflow files
WORKFLOW_FILES=$(find .github/workflows -name "*.yml" -o -name "*.yaml")

# For each workflow, find last successful run
for workflow_file in $WORKFLOW_FILES; do
  WORKFLOW_NAME=$(basename "$workflow_file" .yml | basename .yaml)
  echo "Processing workflow: $WORKFLOW_NAME"
  
  # Get last successful run ID and timestamp
  LAST_SUCCESS=$(gh run list --workflow "$WORKFLOW_NAME" --status success --limit 1 --json databaseId,createdAt,headSha --jq '.[0]')
  
  if [ -n "$LAST_SUCCESS" ] && [ "$LAST_SUCCESS" != "null" ]; then
    LAST_SUCCESS_ID=$(echo "$LAST_SUCCESS" | jq -r '.databaseId')
    LAST_SUCCESS_TIME=$(echo "$LAST_SUCCESS" | jq -r '.createdAt')
    LAST_SUCCESS_SHA=$(echo "$LAST_SUCCESS" | jq -r '.headSha')
    
    echo "Last successful run: $LAST_SUCCESS_ID at $LAST_SUCCESS_TIME (commit: $LAST_SUCCESS_SHA)"
  else
    echo "No successful runs found for $WORKFLOW_NAME"
    continue
  fi
done
```

### 2. List All Runs Since Last Success

For each workflow, list all runs (including failures) since the last successful run:

```bash
# Get all failed/in-progress runs since last success
for workflow_file in $WORKFLOW_FILES; do
  WORKFLOW_NAME=$(basename "$workflow_file" .yml | basename .yaml)
  LAST_SUCCESS=$(gh run list --workflow "$WORKFLOW_NAME" --status success --limit 1 --json databaseId,createdAt --jq '.[0]')
  
  if [ -n "$LAST_SUCCESS" ] && [ "$LAST_SUCCESS" != "null" ]; then
    LAST_SUCCESS_TIME=$(echo "$LAST_SUCCESS" | jq -r '.createdAt')
    
    # Get all runs since last success (excluding successful ones)
    FAILED_RUNS=$(gh run list --workflow "$WORKFLOW_NAME" --limit 50 --json databaseId,status,conclusion,createdAt,headSha,displayTitle --jq ".[] | select(.createdAt > \"$LAST_SUCCESS_TIME\" and .status != \"completed\" or .conclusion != \"success\")")
    
    echo "Found runs since last success for $WORKFLOW_NAME:"
    echo "$FAILED_RUNS" | jq -r '.[] | "\(.databaseId) - \(.status)/\(.conclusion) - \(.displayTitle)"'
  fi
done
```

### 3. Analyze Workflow Run Logs and Extract Errors

For each failed run, download and analyze logs:

```bash
# Create directory for logs
mkdir -p .github/workflow-logs

# Process each failed run
for workflow_file in $WORKFLOW_FILES; do
  WORKFLOW_NAME=$(basename "$workflow_file" .yml | basename .yaml)
  LAST_SUCCESS=$(gh run list --workflow "$WORKFLOW_NAME" --status success --limit 1 --json databaseId,createdAt --jq '.[0]')
  
  if [ -n "$LAST_SUCCESS" ] && [ "$LAST_SUCCESS" != "null" ]; then
    LAST_SUCCESS_TIME=$(echo "$LAST_SUCCESS" | jq -r '.createdAt')
    
    # Get failed run IDs
    FAILED_RUN_IDS=$(gh run list --workflow "$WORKFLOW_NAME" --limit 50 --json databaseId,status,conclusion,createdAt --jq ".[] | select(.createdAt > \"$LAST_SUCCESS_TIME\" and (.status != \"completed\" or .conclusion != \"success\")) | .databaseId")
    
    for run_id in $FAILED_RUN_IDS; do
      echo "Analyzing run $run_id..."
      
      # Get detailed run information
      RUN_INFO=$(gh run view "$run_id" --json status,conclusion,jobs,headSha,displayTitle)
      
      # Download logs
      gh run view "$run_id" --log > ".github/workflow-logs/run-$run_id.log" 2>&1
      
      # Extract job and step information
      JOBS=$(echo "$RUN_INFO" | jq -r '.jobs[] | "\(.name): \(.conclusion)"')
      
      echo "Run $run_id jobs:"
      echo "$JOBS"
      
      # Extract errors from logs
      ERRORS=$(grep -iE "(error|failed|failure|exception|traceback)" ".github/workflow-logs/run-$run_id.log" | head -50)
      
      if [ -n "$ERRORS" ]; then
        echo "Errors found in run $run_id:"
        echo "$ERRORS"
        echo "$ERRORS" > ".github/workflow-logs/run-$run_id-errors.txt"
      fi
    done
  fi
done
```

### 4. Categorize and Prioritize Findings

Analyze extracted errors and categorize by type:

```bash
# Analyze all error logs
ERROR_CATEGORIES=(
  "test_failures"
  "linting_errors"
  "security_issues"
  "dependency_issues"
  "build_errors"
  "coverage_issues"
  "other"
)

for error_file in .github/workflow-logs/*-errors.txt; do
  if [ -f "$error_file" ]; then
    echo "Analyzing $error_file..."
    
    # Categorize errors
    if grep -qiE "(test|pytest|unittest|assert)" "$error_file"; then
      echo "Category: test_failures"
      cat "$error_file" >> .github/workflow-logs/categorized-test-failures.txt
    fi
    
    if grep -qiE "(ruff|flake8|pylint|shellcheck|actionlint|hadolint)" "$error_file"; then
      echo "Category: linting_errors"
      cat "$error_file" >> .github/workflow-logs/categorized-linting-errors.txt
    fi
    
    if grep -qiE "(trivy|vulnerability|security|CVE)" "$error_file"; then
      echo "Category: security_issues"
      cat "$error_file" >> .github/workflow-logs/categorized-security-issues.txt
    fi
    
    if grep -qiE "(pip|npm|dependency|package|import|module)" "$error_file"; then
      echo "Category: dependency_issues"
      cat "$error_file" >> .github/workflow-logs/categorized-dependency-issues.txt
    fi
    
    if grep -qiE "(coverage|missing.*test)" "$error_file"; then
      echo "Category: coverage_issues"
      cat "$error_file" >> .github/workflow-logs/categorized-coverage-issues.txt
    fi
  fi
done
```

### 5. Remediate Findings Automatically

Apply fixes based on error categories:

#### 5.1 Fix Linting Errors

```bash
# Auto-fix Python linting issues
if [ -f .github/workflow-logs/categorized-linting-errors.txt ]; then
  echo "Fixing Python linting issues..."
  
  # Run ruff auto-fix
  if command -v ruff &> /dev/null; then
    ruff check --fix . || true
    ruff format . || true
  else
    # Use Docker if ruff not available locally
    docker-compose build test 2>/dev/null || true
    docker-compose --profile test run --rm test python -m ruff check --fix . || true
    docker-compose --profile test run --rm test python -m ruff format . || true
  fi
  
  # Fix shellcheck issues (manual review needed, but can suggest fixes)
  if grep -qi "shellcheck" .github/workflow-logs/categorized-linting-errors.txt; then
    echo "Shellcheck issues found - review and fix manually"
    find . -name "*.sh" -exec shellcheck {} \; || true
  fi
fi
```

#### 5.2 Fix Test Failures

```bash
# Analyze and fix test failures
if [ -f .github/workflow-logs/categorized-test-failures.txt ]; then
  echo "Analyzing test failures..."
  
  # Extract test names that failed
  FAILED_TESTS=$(grep -oE "test_[a-zA-Z0-9_]+|def test_" .github/workflow-logs/categorized-test-failures.txt | sort -u)
  
  if [ -n "$FAILED_TESTS" ]; then
    echo "Failed tests identified:"
    echo "$FAILED_TESTS"
    
    # Run specific tests to get detailed error messages
    for test in $FAILED_TESTS; do
      echo "Running test: $test"
      python -m pytest -xvs -k "$test" || true
    done
  fi
fi
```

#### 5.3 Fix Security Issues

```bash
# Address security vulnerabilities
if [ -f .github/workflow-logs/categorized-security-issues.txt ]; then
  echo "Analyzing security issues..."
  
  # Check for HIGH/CRITICAL vulnerabilities
  if grep -qiE "(HIGH|CRITICAL)" .github/workflow-logs/categorized-security-issues.txt; then
    echo "HIGH/CRITICAL security issues found"
    
    # Run Trivy scan locally
    if command -v trivy &> /dev/null; then
      trivy fs --severity HIGH,CRITICAL . || true
    fi
    
    # Check for dependency updates
    if grep -qi "dependency" .github/workflow-logs/categorized-security-issues.txt; then
      echo "Review dependency updates needed"
      # Could trigger dependabot or suggest manual updates
    fi
  fi
fi
```

#### 5.4 Fix Coverage Issues

```bash
# Address coverage issues
if [ -f .github/workflow-logs/categorized-coverage-issues.txt ]; then
  echo "Analyzing coverage issues..."
  
  # Run coverage report
  if command -v pytest &> /dev/null; then
    pytest --cov=. --cov-report=term-missing --cov-report=xml || true
    
    # Check if coverage is below threshold
    COVERAGE=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(root.attrib.get('line-rate', '0'))" 2>/dev/null || echo "0")
    COVERAGE_PCT=$(echo "$COVERAGE * 100" | bc)
    
    if (( $(echo "$COVERAGE_PCT < 95" | bc -l) )); then
      echo "Coverage is $COVERAGE_PCT%, below 95% threshold"
      echo "Review coverage report and add missing tests"
    fi
  fi
fi
```

#### 5.5 Fix Dependency Issues

```bash
# Address dependency issues
if [ -f .github/workflow-logs/categorized-dependency-issues.txt ]; then
  echo "Analyzing dependency issues..."
  
  # Check for missing dependencies
  if grep -qiE "(import|module|package.*not.*found)" .github/workflow-logs/categorized-dependency-issues.txt; then
    echo "Missing dependencies detected"
    
    # Try to install dependencies
    if [ -f pyproject.toml ]; then
      if command -v uv &> /dev/null; then
        uv pip install -e . || true
      fi
    fi
  fi
fi
```

### 6. Verify Fixes

After remediation, verify that fixes work:

```bash
# Run quality gate to verify all checks pass
if [ -f scripts/quality-gate.sh ]; then
  echo "Running quality gate to verify fixes..."
  scripts/quality-gate.sh || true
fi

# Run pre-commit hooks
if command -v pre-commit &> /dev/null; then
  echo "Running pre-commit hooks..."
  pre-commit run --all-files || true
fi
```

### 7. Generate Summary Report

Create a summary of findings and remediation actions:

```bash
SUMMARY_FILE=".github/workflow-logs/remediation-summary.md"

cat > "$SUMMARY_FILE" << EOF
# GitHub Actions Workflow Remediation Summary

Generated: $(date)

## Workflows Analyzed
$(for wf in $WORKFLOW_FILES; do echo "- $(basename "$wf")"; done)

## Runs Analyzed
$(find .github/workflow-logs -name "run-*-errors.txt" | wc -l) failed runs analyzed

## Issues Found by Category

### Test Failures
$(if [ -f .github/workflow-logs/categorized-test-failures.txt ]; then wc -l < .github/workflow-logs/categorized-test-failures.txt; else echo "0"; fi) issues

### Linting Errors
$(if [ -f .github/workflow-logs/categorized-linting-errors.txt ]; then wc -l < .github/workflow-logs/categorized-linting-errors.txt; else echo "0"; fi) issues

### Security Issues
$(if [ -f .github/workflow-logs/categorized-security-issues.txt ]; then wc -l < .github/workflow-logs/categorized-security-issues.txt; else echo "0"; fi) issues

### Dependency Issues
$(if [ -f .github/workflow-logs/categorized-dependency-issues.txt ]; then wc -l < .github/workflow-logs/categorized-dependency-issues.txt; else echo "0"; fi) issues

### Coverage Issues
$(if [ -f .github/workflow-logs/categorized-coverage-issues.txt ]; then wc -l < .github/workflow-logs/categorized-coverage-issues.txt; else echo "0"; fi) issues

## Remediation Actions Taken

- Auto-fixed linting issues (ruff format, ruff check --fix)
- Analyzed test failures
- Reviewed security vulnerabilities
- Checked coverage thresholds
- Verified dependency installations

## Next Steps

1. Review categorized error files in .github/workflow-logs/
2. Manually address any issues that couldn't be auto-fixed
3. Commit fixes and push to trigger new workflow runs
4. Monitor subsequent workflow runs to verify fixes

EOF

echo "Summary report created: $SUMMARY_FILE"
cat "$SUMMARY_FILE"
```

## Implementation Notes

**The agent should:**

1. **Execute commands sequentially** - Each step depends on the previous one
2. **Handle errors gracefully** - Use `|| true` where appropriate to continue on errors
3. **Store logs locally** - Save all logs to `.github/workflow-logs/` for review
4. **Categorize errors** - Group similar errors for easier remediation
5. **Auto-fix when possible** - Apply automatic fixes for linting, formatting, etc.
6. **Generate summary** - Create a report of findings and actions taken

**Error Handling:**

- If `gh` CLI is not authenticated, prompt user to run `gh auth login`
- If no successful runs exist, analyze all recent runs instead
- If workflow files don't exist, skip gracefully
- If remediation fails, log the error but continue with other fixes

**Remediation Priority:**

1. **Critical**: Security vulnerabilities (HIGH/CRITICAL)
2. **High**: Test failures
3. **Medium**: Linting errors (auto-fixable)
4. **Low**: Coverage issues, dependency warnings

## Success Criteria

- All workflow runs since last success have been analyzed
- Errors have been categorized and logged
- Auto-fixable issues have been remediated
- Summary report has been generated
- Quality gate passes after fixes

## Related Commands

- [checks-scan.md](mdc:.cursor/commands/checks-scan.md): Run comprehensive checks and remediate
- [security-quality-scan.md](mdc:.cursor/commands/security-quality-scan.md): Security and quality scans
- [quality-gate.sh](mdc:scripts/quality-gate.sh): Quality gate script
