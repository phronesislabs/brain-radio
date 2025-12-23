# Docker Build Testing

## Problem: Build Failures Not Caught

**Issue**: Dockerfiles can pass static analysis (Hadolint) but still fail to build when actually executed.

**Example**: The `frontend/Dockerfile.dev` attempted to create a user with GID 1000, but `node:18-alpine` already has a user with that GID, causing the build to fail with:

```
addgroup: gid '1000' in use
```

## Why This Wasn't Caught

1. **Static Analysis Only**: We only ran Hadolint (static linting) on Dockerfiles, which checks for best practices and security issues but doesn't actually build the images.

2. **No Build Tests**: There was no automated test that actually attempted to build all Dockerfiles to verify they work.

3. **Manual Testing Gap**: The startup script (`start.sh`) was the first place where Dockerfiles were actually built, meaning users discovered build failures.

## Solution: Docker Build Testing

### Implementation

1. **Build Test Script**: Created `scripts/test-docker-builds.sh` that:
   - Finds all Dockerfiles in the project
   - Attempts to build each one
   - Reports which builds succeed or fail
   - Cleans up test images after validation

2. **Quality Gate Integration**: Added Docker build testing to `.checks/scripts/quality-gate.sh`:
   - Runs after Hadolint (static analysis)
   - Fails the quality gate if any Dockerfile fails to build
   - Provides clear error messages

3. **CI Integration**: The quality gate is already called in `.github/workflows/ci.yml`, so Docker build tests now run automatically on every push and PR.

### Running Manually

```bash
# Test all Dockerfiles
./scripts/test-docker-builds.sh

# Or as part of full quality gate
.checks/scripts/quality-gate.sh
```

### Prevention Strategy

**Three-Layer Defense**:

1. **Static Analysis** (Hadolint): Catches syntax errors, security issues, best practice violations
2. **Build Testing** (test-docker-builds.sh): Verifies Dockerfiles actually build successfully
3. **Integration Testing** (docker-compose): Verifies services start and work together

**When to Run**:

- **Before Committing**: Run `./scripts/test-docker-builds.sh` locally
- **In CI**: Automatically runs as part of quality gate
- **In Pre-commit Hooks**: Could be added to pre-commit hooks for immediate feedback

## Fix Applied

The `frontend/Dockerfile.dev` was fixed to use the existing `node` user from `node:18-alpine` instead of trying to create a new user with GID 1000:

```dockerfile
# Use existing node user (node:18-alpine has node user with UID 1000)
RUN chown -R node:node /app
USER node
```

This is simpler, more reliable, and follows the principle of using existing users when available.

## Best Practices

1. **Always test builds**: Don't rely solely on static analysis
2. **Use existing users**: When base images provide users, use them instead of creating new ones
3. **Test in CI**: Ensure build tests run automatically in CI/CD pipelines
4. **Fail fast**: Catch build issues before users encounter them

## Related Files

- `scripts/test-docker-builds.sh` - Docker build test script
- `.checks/scripts/quality-gate.sh` - Quality gate that includes build tests
- `.github/workflows/ci.yml` - CI workflow that runs quality gate
- `frontend/Dockerfile.dev` - Fixed Dockerfile example

