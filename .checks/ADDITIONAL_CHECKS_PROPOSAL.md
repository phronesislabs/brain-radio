# Additional Checks Proposal

Based on analysis of modern Python projects (including Astral uv patterns) and industry best practices, here are additional checks we could add to the checks system.

## Currently Implemented

- Security scanning (Trivy, Zizmor, Hadolint)
- Linting (Ruff, Shellcheck, Actionlint)
- Code formatting (Ruff format)
- Test coverage enforcement (95% threshold)
- GitHub Actions security (Pinact, Zizmor)
- Docker security (Hadolint, Trivy)

## Proposed Additional Checks

### 1. Type Checking (mypy)

**Tool**: mypy (already in dev dependencies)

**Why**: Catches type errors before runtime, improves code quality

**Implementation**:
```bash
# Add to quality-gate.sh
if [ "${TOOL_MYPY}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Running mypy type checking..."
    python -m mypy src/ || {
        echo "ERROR: mypy found type errors"
        exit 1
    }
fi
```

**Config addition**:
```yaml
tools:
  mypy: true
```

**Status**: Free, open-source, already in dependencies

---

### 2. Python Security Linting (Bandit)

**Tool**: bandit

**Why**: Specialized Python security linter, catches common security issues

**Implementation**:
```bash
# Install: uv pip install --system bandit[toml]
if [ "${TOOL_BANDIT}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Running bandit security scan..."
    bandit -r src/ -f json -o bandit-report.json || {
        echo "ERROR: bandit found security issues"
        exit 1
    }
fi
```

**Config addition**:
```yaml
tools:
  bandit: true
  bandit_severity: "HIGH"  # Only fail on HIGH/CRITICAL
```

**Status**: Free, open-source, Python-specific security

---

### 3. Documentation Coverage (pydocstyle)

**Tool**: pydocstyle (formerly pep257)

**Why**: Ensures code is properly documented

**Implementation**:
```bash
# Install: uv pip install --system pydocstyle
if [ "${TOOL_PYDOCSTYLE}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Checking documentation coverage..."
    pydocstyle src/ --convention=google || {
        echo "WARNING: pydocstyle found documentation issues"
        # Could be warning instead of error
    }
fi
```

**Config addition**:
```yaml
tools:
  pydocstyle: true
  pydocstyle_fail_on_error: false  # Optional: make it a warning
```

**Status**: Free, open-source

---

### 4. Dependency License Checking (pip-licenses)

**Tool**: pip-licenses

**Why**: Ensures all dependencies have acceptable licenses

**Implementation**:
```bash
# Install: uv pip install --system pip-licenses
if [ "${TOOL_LICENSE_CHECK}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Checking dependency licenses..."
    pip-licenses --with-authors --with-urls --format=json > licenses.json
    # Check against allowed licenses list
fi
```

**Config addition**:
```yaml
tools:
  license_check: true
  allowed_licenses:
    - "MIT"
    - "Apache-2.0"
    - "BSD-3-Clause"
```

**Status**: Free, open-source

---

### 5. Code Complexity Analysis (radon)

**Tool**: radon

**Why**: Identifies overly complex code that's hard to maintain

**Implementation**:
```bash
# Install: uv pip install --system radon
if [ "${TOOL_RADON}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Analyzing code complexity..."
    radon cc src/ --min B --show-complexity || {
        echo "WARNING: radon found high complexity code"
    }
fi
```

**Config addition**:
```yaml
tools:
  radon: true
  radon_max_complexity: 10  # Fail if complexity > 10
```

**Status**: Free, open-source

---

### 6. Dead Code Detection (vulture)

**Tool**: vulture

**Why**: Finds unused code that can be removed

**Implementation**:
```bash
# Install: uv pip install --system vulture
if [ "${TOOL_VULTURE}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Detecting dead code..."
    vulture src/ --min-confidence 80 || {
        echo "WARNING: vulture found potentially unused code"
    }
fi
```

**Config addition**:
```yaml
tools:
  vulture: true
  vulture_min_confidence: 80
```

**Status**: Free, open-source

---

### 7. Import Sorting and Organization (isort)

**Tool**: isort (though Ruff can handle this)

**Why**: Ensures consistent import organization

**Status**: Already handled by Ruff, but could add explicit check

---

### 8. JSON/YAML/TOML Schema Validation

**Tool**: Custom validation scripts

**Why**: Ensures config files are valid

**Implementation**: Already partially done via pre-commit hooks, but could add explicit validation

**Status**: Already implemented via pre-commit

---

### 9. Dependency Update Checking (pip-audit)

**Tool**: pip-audit

**Why**: Alternative/additional to Trivy for Python-specific vulnerabilities

**Implementation**:
```bash
# Install: uv pip install --system pip-audit
if [ "${TOOL_PIP_AUDIT}" = "true" ] && [ "${PYTHON_ENABLED}" = "true" ]; then
    echo "Auditing Python dependencies..."
    pip-audit --desc --format json || {
        echo "ERROR: pip-audit found vulnerabilities"
        exit 1
    }
fi
```

**Status**: Free, open-source, Python-specific

---

### 10. Performance Regression Detection (pytest-benchmark)

**Tool**: pytest-benchmark

**Why**: Detects performance regressions in tests

**Status**: More advanced, may not fit all projects

---

## Recommended Priority

### High Priority (Should Add)

1. **mypy** - Type checking is essential for Python projects
2. **bandit** - Python-specific security scanning complements Trivy
3. **pip-audit** - Python-specific vulnerability scanning

### Medium Priority (Nice to Have)

4. **pydocstyle** - Documentation quality (can be warning-only)
5. **radon** - Code complexity (can be warning-only)
6. **license_check** - Important for compliance

### Low Priority (Optional)

7. **vulture** - Dead code detection (can be noisy)
8. **pytest-benchmark** - Performance testing (project-specific)

## Implementation Notes

- All proposed tools are **free and open-source**
- All fit into the existing checks framework
- Can be enabled/disabled via config
- Most can be added as optional warnings initially
- Tools should be added to `setup-tools.sh` or installed via uv

## Coverage Enforcement Verification

**Coverage enforcement is working correctly:**
- Coverage threshold is checked after tests run
- Script exits with code 1 if coverage < threshold
- Handles missing coverage.xml file
- Uses line-rate from coverage.xml
- Default threshold is 95% (configurable)

**Improvements made:**
- Added check for coverage.xml existence
- Improved error handling for malformed XML
- Better error messages

