# Renovate Workflow

**Last updated: 2025-12-22**

## Overview

This project includes a GitHub Actions workflow to run Renovate with multiple trigger options:
- **Scheduled**: Runs automatically every Monday at 4:00 AM UTC (matches `renovate.json` schedule)
- **Manual**: Trigger on-demand via GitHub UI or CLI script
- **Workflow Call**: Can be invoked by other workflows

This allows you to trigger dependency updates immediately without waiting for the weekly schedule.

## Quick Start

```bash
# Run Renovate workflow (creates PRs for updates)
./scripts/run-renovate.sh

# Dry run (see what would be updated)
./scripts/run-renovate.sh --dry-run

# Include major version updates
./scripts/run-renovate.sh --include-major
```

## Prerequisites

1. **GitHub CLI installed and authenticated:**
   ```bash
   gh auth status
   ```
   If not authenticated: `gh auth login`

2. **Script is executable:**
   ```bash
   chmod +x scripts/run-renovate.sh
   ```

## How It Works

1. **Script triggers workflow**: `run-renovate.sh` uses `gh workflow run` to trigger `.github/workflows/renovate.yml`
2. **Workflow runs Renovate**: Uses the official `renovate/renovate` Docker image with auto-fix enabled
3. **Renovate creates PRs**: Automatically creates pull requests for dependency updates
4. **Script polls for completion**: Monitors workflow status and displays results

## Workflow Features

The `renovate.yml` workflow includes:

- **Auto-fix enabled**: Automatically fixes lockfiles, YAML, Python, npm, Docker, and GitHub Actions
- **Auto-merge**: Safe updates (patches, dev dependencies) can auto-merge after CI passes
- **Dry run mode**: Test updates without creating PRs
- **Major updates**: Optional flag to include major version updates
- **Full logging**: Debug-level logs for troubleshooting

## Script Options

```bash
./scripts/run-renovate.sh [OPTIONS]

Options:
  --dry-run        Run in dry-run mode (no PRs created)
  --include-major  Include major version updates
  --timeout SEC    Maximum wait time in seconds (default: 600)
```

## Workflow Inputs

The workflow accepts these inputs (set via script or GitHub UI):

- `dry_run`: `true` or `false` (default: `false`)
- `include_major`: `true` or `false` (default: `false`)

## Manual Workflow Trigger

You can also trigger the workflow manually via GitHub UI:

1. Go to **Actions** tab
2. Select **Renovate** workflow
3. Click **Run workflow**
4. Select options (dry run, include major)
5. Click **Run workflow**

**Note**: The workflow also runs automatically every Monday at 4:00 AM UTC via the schedule trigger.

## Auto-Fix Capabilities

The workflow enables Renovate's built-in auto-fix features:

- **Lockfiles**: Automatically updates `package-lock.json`, `poetry.lock`, etc.
- **YAML**: Fixes formatting and structure in YAML files
- **Python**: Updates `pyproject.toml`, `requirements.txt` with proper formatting
- **npm**: Updates `package.json` and regenerates `package-lock.json`
- **Docker**: Updates Dockerfile base images with proper tags
- **GitHub Actions**: Updates action versions and pins SHAs

## Output

The script provides:

1. **Workflow status**: Real-time updates on workflow progress
2. **Run URL**: Direct link to view workflow logs
3. **Created PRs**: List of pull requests created by Renovate
4. **Summary**: Final status and next steps

Example output:
```
Repository: your-org/brain-radio
Workflow: renovate.yml
Dry Run: false
Include Major: false
Timeout: 600 seconds

Triggering Renovate workflow...
Workflow triggered successfully!
Run ID: 1234567890
View run: https://github.com/your-org/brain-radio/actions/runs/1234567890

Waiting for workflow to complete...
[14:30:15] Status: in_progress/none
[14:32:45] Status: completed/success

✓ Workflow completed successfully!

Checking for created pull requests...
Created/Updated Pull Requests:
  - 42: chore(deps): update all-minor-patch (open)
  - 43: chore(deps): update docker-python-3.x (open)
```

## Troubleshooting

### Script fails: "GitHub CLI is not authenticated"
```bash
gh auth login
```

### Script fails: "Could not get workflow run ID"
- Check that the workflow file exists: `.github/workflows/renovate.yml`
- Verify you have permission to trigger workflows
- Try running the workflow manually via GitHub UI first

### Workflow fails: "Permission denied"
- The workflow needs `contents: write` permission to create PRs
- Check repository settings → Actions → General → Workflow permissions

### No PRs created
- Check workflow logs for errors
- Verify `renovate.json` exists and is valid
- Check if updates are already in existing PRs
- Try with `--include-major` if only major updates are available

### Workflow times out
- Increase timeout: `./scripts/run-renovate.sh --timeout 1200`
- Check workflow logs for long-running operations
- Large repositories may need more time

## Integration with Cursor

The `update_dependencies` command automatically uses this workflow:

```bash
# In Cursor, just run:
update-dependencies
```

The command will:
1. Execute `./scripts/run-renovate.sh`
2. Wait for completion
3. Report results and created PRs

## Related Documentation

- [Renovate Setup](RENOVATE_SETUP.md): General Renovate configuration
- [renovate.json](../renovate.json): Renovate configuration file
- [Workflow file](../.github/workflows/renovate.yml): Workflow definition

