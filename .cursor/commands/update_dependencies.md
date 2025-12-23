---
description: "Update all project dependencies to latest stable versions with strict version pinning"
---

# Update Dependencies

**Note**: This project uses **Renovate** for automated dependency management (see `renovate.json` and [docs/RENOVATE_SETUP.md](docs/RENOVATE_SETUP.md)). Renovate automatically creates PRs for dependency updates with proper version pinning. This command is for manual one-time updates or when Renovate is not available.

Comprehensive dependency update workflow that identifies and updates all dependencies, dev tools, frameworks, and Docker images to their latest stable versions. Uses CLI tools first, then API calls, then web searches as fallback. Never uses "latest" tags - always pins to exact version numbers.

## Usage

**Recommended**: Use Renovate for automated dependency updates. Install the GitHub App at <https://github.com/apps/renovate>

**Manual updates** (on-demand Renovate execution):

```bash
# Update all dependencies (triggers Renovate workflow)
update-dependencies

# Dry run (check what would be updated without creating PRs)
update-dependencies --dry-run

# Include major version updates
update-dependencies --include-major

# Or run the script directly:
./scripts/run-renovate.sh
./scripts/run-renovate.sh --dry-run
./scripts/run-renovate.sh --include-major
```

**Prerequisites:**

- GitHub CLI (`gh`) must be installed and authenticated: `gh auth login`
- Script must be executable: `chmod +x scripts/run-renovate.sh` (if not already)

## Options

- `--dry-run`: Run in dry-run mode (no PRs created, shows what would be updated)
- `--include-major`: Include major version updates (default: only patch and minor)
- `--timeout SECONDS`: Maximum time to wait for workflow completion (default: 600 seconds)

**Note**: The workflow updates all dependency types (Python, npm, Docker, GitHub Actions) based on `renovate.json` configuration. Individual type selection is not supported - use Renovate's package rules in `renovate.json` to control what gets updated.

## Execution Steps

When the user invokes this command:

1. **Run Renovate Workflow**: Execute the local script that triggers the GitHub Actions workflow
   - Run `./scripts/run-renovate.sh` (or with `--dry-run` for testing)
   - The script will:
     - Trigger the `renovate-manual.yml` workflow via GitHub CLI
     - Poll for workflow completion
     - Display results and any created PRs
   - This leverages Renovate's built-in auto-fix capabilities instead of manual updates
   - **If the script fails or GitHub CLI is unavailable**, proceed with manual discovery below

2. **Discovery Phase** (Fallback - only if Renovate workflow unavailable): Identify all dependencies in the project
   - Scan `pyproject.toml`, `setup.py`, `requirements*.txt` for Python dependencies
   - Scan `package.json`, `package-lock.json` for npm dependencies
   - Scan all `Dockerfile*` files for base images and system packages
   - Scan `docker-compose*.yml` files for service images
   - Scan `.github/workflows/*.yml` for GitHub Actions versions
   - Scan scripts and tooling files for dev tool versions
   - Create comprehensive inventory of all dependencies

3. **Version Check Phase** (Fallback): Determine latest stable versions for each dependency
   - **Priority 1 - CLI Tools**: Use native package manager commands
     - Python: `uv pip list --outdated` or `pip index versions <package>`
     - npm: `npm outdated` or `npm view <package> versions --json`
     - Docker: `docker manifest inspect <image>:latest` to get digest, then find version tags
   - **Priority 2 - API Calls**: Query official registries
     - PyPI: `curl -s https://pypi.org/pypi/<package>/json | jq .info.version`
     - npm: `curl -s https://registry.npmjs.org/<package> | jq '.["dist-tags"].latest'`
     - Docker Hub: `curl -s https://hub.docker.com/v2/repositories/<org>/<image>/tags/?page_size=100 | jq .results[].name`
     - GitHub Releases: `curl -s https://api.github.com/repos/<org>/<repo>/releases/latest | jq .tag_name`
   - **Priority 3 - Web Search**: Only if CLI/API unavailable
     - Search for official release pages and changelogs
     - Extract version numbers from official documentation
   - Verify all versions exist and are stable (not pre-release unless needed)

4. **Update Phase** (Fallback): Update all dependency files with pinned versions
   - Update `pyproject.toml` with exact versions (`==` for Python)
   - Update `package.json` with exact versions (no `^` or `~`)
   - Update all `Dockerfile*` files with versioned base images
   - Update `docker-compose*.yml` files if they specify image versions
   - Update GitHub Actions versions in workflow files
   - Update dev tool versions in scripts and config files
   - Regenerate lock files (`package-lock.json`, etc.) if present
   - **NEVER use "latest" tag** - always pin to exact version

5. **Verification Phase** (Fallback): Verify updates are correct
   - Check that all updated versions exist in registries
   - Verify no "latest" tags remain in any file
   - Check for syntax errors in updated files
   - Run dependency install test (dry run if possible)

6. **Testing Phase** (Fallback): Ensure updates don't break functionality
   - Run `pytest` or equivalent test suite
   - Run `npm test` for frontend if applicable
   - Run linting and formatting checks
   - Run quality gate script if available
   - Fix any breaking changes if tests fail

7. **Documentation Phase** (Fallback): Document what was updated
   - Create summary of all updated dependencies
   - Note any breaking changes or required code updates
   - Update changelog if project maintains one

## How It Works

The command follows a strict priority order for discovering versions:

1. **CLI Tools First**: Uses native package manager commands because they're fastest and most reliable

   ```bash
   # Python
   uv pip list --outdated
   pip index versions fastapi
   
   # npm
   npm outdated
   npm view react versions --json
   
   # Docker
   docker manifest inspect python:3.11-slim
   ```

2. **API Calls Second**: Falls back to official registry APIs when CLI tools don't provide enough info

   ```bash
   # PyPI API
   curl -s https://pypi.org/pypi/fastapi/json | jq .info.version
   
   # npm registry API
   curl -s https://registry.npmjs.org/react | jq '.["dist-tags"].latest'
   
   # Docker Hub API
   curl -s "https://hub.docker.com/v2/repositories/library/python/tags/?page_size=100" | jq .results[].name
   ```

3. **Web Search Last**: Only when CLI/API unavailable or insufficient

   - Searches official documentation and release pages
   - Extracts version numbers from changelogs
   - Verifies versions from official sources

The command updates all dependency types:

- **Python packages**: `pyproject.toml`, `requirements*.txt`
- **npm packages**: `package.json`, `package-lock.json`
- **Docker images**: All `Dockerfile*` files, `docker-compose*.yml`
- **System packages**: `apt-get`, `apk`, `yum` in Dockerfiles
- **Dev tools**: Linters, formatters, test frameworks
- **CI/CD tools**: GitHub Actions, other workflow tools
- **Build tools**: setuptools, wheel, build versions

## Examples

### Example 1: Update All Dependencies

```bash
update-dependencies
```

This will:

1. Run `./scripts/run-renovate.sh` to trigger the Renovate workflow
2. The workflow will:
   - Scan all dependencies (Python, npm, Docker, GitHub Actions)
   - Check for latest versions
   - Create PRs with pinned versions
   - Auto-fix lockfiles and configuration files
3. The script will poll for completion and display results
4. Review and merge the created PRs

### Example 2: Dry Run

```bash
update-dependencies --dry-run
```

This runs:

```bash
./scripts/run-renovate.sh --dry-run
```

The workflow will run in dry-run mode, showing what would be updated without creating PRs. Check the workflow logs for details.

### Example 3: Python Only

```bash
update-dependencies --python-only
```

Updates only Python dependencies in `pyproject.toml` and related files.

### Example 4: Docker Only

```bash
update-dependencies --docker-only
```

Updates only Docker base images in all `Dockerfile*` files.

## Implementation Details

The command should:

1. **Primary Method - Use Renovate Workflow**:
   - Execute `./scripts/run-renovate.sh` using `run_terminal_cmd`
   - Pass `--dry-run` flag if user requested dry-run mode
   - Pass `--include-major` flag if user wants major updates
   - Wait for script completion and report results
   - The script handles workflow triggering, polling, and result reporting

2. **Fallback Method** (only if Renovate workflow unavailable):
   - **Use `todo_write`** to track progress through discovery, update, and verification phases
   - **Use `read_file`** to read all dependency files
   - **Use `run_terminal_cmd`** to execute CLI tools for version checking
   - **Use `web_search`** as fallback when CLI/API unavailable
   - **Use `search_replace`** to update dependency files with exact versions
   - **Use `run_terminal_cmd`** to run tests after updates
   - **Report results** in a clear summary format

## Error Handling

- **If CLI tool fails**: Fall back to API calls
- **If API call fails**: Fall back to web search
- **If version not found**: Skip that dependency and report warning
- **If tests fail**: Report failures and suggest manual review
- **If lock file conflicts**: Regenerate lock files

## Security Considerations

- Verify package integrity before updating
- Check for security advisories
- Prefer security updates even if not latest
- Update vulnerable dependencies as priority

## Automated Dependency Management

This project uses **Renovate** for automated dependency updates:

- **Renovate GitHub App**: Free, automatically creates PRs for dependency updates (weekly schedule)
- **Manual Renovate Workflow**: Run Renovate on-demand via `./scripts/run-renovate.sh`
- **Configuration**: See `renovate.json` for settings
- **Documentation**: See [docs/RENOVATE_SETUP.md](docs/RENOVATE_SETUP.md) for setup and usage
- **Workflow**: See [.github/workflows/renovate.yml](.github/workflows/renovate.yml) for manual execution
- **Benefits**:

  - Automatic version pinning (exact versions, no ranges)
  - Docker image updates with digest pinning
  - Auto-merge for safe updates (patches, dev dependencies)
  - Built-in auto-fix for lockfiles and configuration files
  - Weekly schedule with PR limits
  - Semantic commits

**This command uses the Renovate workflow by default** to leverage Renovate's built-in auto-fix capabilities. The manual fallback method is only used if:

- GitHub CLI is unavailable
- Workflow execution fails
- User explicitly requests manual updates

## Related Rules

- [dependency_updates.mdc](mdc:.cursor/rules/dependency_updates.mdc): Dependency update guidelines
- [cursor_rules.mdc](mdc:.cursor/rules/cursor_rules.mdc): Rule formatting guidelines
- [autofix-branch.mdc](mdc:.cursor/rules/autofix-branch.mdc): Auto-fix branch workflow
- [docs/RENOVATE_SETUP.md](docs/RENOVATE_SETUP.md): Renovate setup and configuration
- [docs/RENOVATE_MANUAL_WORKFLOW.md](docs/RENOVATE_MANUAL_WORKFLOW.md): Manual Renovate workflow execution guide
