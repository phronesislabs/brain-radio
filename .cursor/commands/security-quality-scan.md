---
description: "Run comprehensive security and quality scans, process output, and remediate findings"
---

Run the security and quality orchestrator script with auto-fix enabled, process all output, and automatically remediate findings where possible.

## Steps

1. **Ensure all tools are installed:**
   ```bash
   scripts/tooling/setup-tools.sh
   ```

2. **Run the orchestrator with auto-fix:**
   ```bash
   scripts/security-quality-orchestrator.sh --auto-fix
   ```

3. **Process the output and identify issues:**
   - Review all report files generated (*-report.txt, hadolint-*.txt, trivy-*.txt)
   - Categorize issues by type: security, linting, formatting, tests, coverage
   - Prioritize HIGH and CRITICAL security issues

4. **Remediate findings automatically where possible:**
   - **Ruff issues**: Auto-fix with `ruff check --fix . && ruff format .`
   - **Shellcheck issues**: Review and fix manually (some may be auto-fixable)
   - **Actionlint issues**: Fix workflow syntax errors
   - **Hadolint issues**: Apply Dockerfile security best practices
   - **Trivy vulnerabilities**: Update dependencies, fix misconfigurations
   - **Zizmor issues**: Fix GitHub Actions security problems
   - **Test failures**: Fix broken tests
   - **Coverage issues**: Add missing tests

5. **For issues requiring manual intervention:**
   - Security vulnerabilities in dependencies: Update to patched versions
   - Dockerfile security issues: Apply hadolint recommendations
   - Docker compose misconfigurations: Fix based on Trivy findings
   - Test failures: Debug and fix test code

6. **Run pre-commit hooks to verify fixes:**
   ```bash
   pre-commit run --all-files
   ```

7. **Run quality gate to ensure everything passes:**
   ```bash
   scripts/quality-gate.sh
   ```

8. **Iterate until all checks pass:**
   - If issues remain, go back to step 2
   - Maximum iterations: 10 (configurable)

## Output Processing

The orchestrator generates several report files:
- `trivy-fs-report.txt` - Filesystem security scan results
- `trivy-config-*.txt` - Docker compose config scan results
- `trivy-image-*.txt` - Docker image scan results
- `hadolint-*.txt` - Dockerfile linting results
- `actionlint-report.txt` - GitHub Actions linting results
- `shellcheck-report.txt` - Shell script linting results
- `ruff-check-report.txt` - Python linting results
- `ruff-format-report.txt` - Python formatting results

Process each report:
1. Extract HIGH and CRITICAL issues
2. Group by file and issue type
3. Apply fixes in order: security → linting → formatting → tests
4. Verify fixes don't introduce new issues

## Auto-remediation Strategy

**Automatic fixes:**
- Python formatting (ruff format)
- Python linting (ruff check --fix)
- Trailing whitespace, end-of-file fixes
- YAML/JSON formatting

**Semi-automatic fixes (with review):**
- Dependency updates for security vulnerabilities
- Dockerfile improvements based on hadolint
- Shell script improvements based on shellcheck

**Manual fixes required:**
- Complex security vulnerabilities
- Test logic errors
- Architecture/design issues

## Success Criteria

All checks must pass:
- No HIGH or CRITICAL security issues
- All linters pass (ruff, shellcheck, actionlint, hadolint)
- All tests pass
- Coverage >= 95%
- Pre-commit hooks pass
- Quality gate passes

