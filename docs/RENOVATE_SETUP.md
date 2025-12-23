# Renovate Setup

**Last updated: 2025-12-22**

## Overview

This project uses **Renovate** for automated dependency management. Renovate is a powerful, open-source tool that automatically creates pull requests to keep dependencies up to date.

## Why Renovate Instead of Dependabot?

**Renovate advantages:**
- ✅ **More ecosystems**: Supports Docker, Docker Compose, GitHub Actions, npm, pip, and more
- ✅ **Better version pinning**: Automatically pins exact versions (no `^` or `~`)
- ✅ **Docker image updates**: Can update Docker base images with specific tags
- ✅ **Flexible grouping**: Groups related updates intelligently
- ✅ **Better configuration**: More granular control over update behavior
- ✅ **Semantic commits**: Automatically uses conventional commit format
- ✅ **Auto-merge**: Can auto-merge safe updates (patches, dev dependencies)

**Dependabot limitations:**
- Only security updates (current config is "paranoid" mode)
- Limited Docker support
- Less flexible configuration
- No automatic version pinning

## Setup

### Option 1: GitHub App (Recommended)

1. Go to https://github.com/apps/renovate
2. Click "Install"
3. Select your repository
4. Renovate will automatically detect `renovate.json` and start working

### Option 2: Self-Hosted

If you prefer self-hosting:

```bash
# Using Docker
docker run -d \
  -e RENOVATE_TOKEN=your_github_token \
  -e RENOVATE_PLATFORM=github \
  -e RENOVATE_REPOSITORIES=your-org/brain-radio \
  renovate/renovate
```

## Configuration

The `renovate.json` file configures Renovate behavior:

### Key Settings

- **Version Pinning**: All dependencies are pinned to exact versions (no ranges)
- **Auto-merge**: Patches and dev dependencies auto-merge after CI passes
- **Schedule**: Runs weekly on Mondays before 4am UTC
- **PR Limits**: Max 5 concurrent PRs, 2 per hour
- **Docker**: Pins digests for reproducibility
- **Semantic Commits**: Uses `chore(deps):` prefix

### Update Types

- **Patches**: Auto-merge after CI passes
- **Minor**: Require manual review
- **Major**: Require manual review + status checks
- **Security**: Always create PRs immediately

## What Gets Updated

Renovate will automatically update:

1. **Python packages** (`pyproject.toml`)
   - Pins to exact versions: `fastapi==0.115.0`
   - Updates dev dependencies automatically

2. **npm packages** (`package.json`, `package-lock.json`)
   - Pins to exact versions: `"react": "18.3.1"`
   - Regenerates `package-lock.json`

3. **Docker images** (all `Dockerfile*` files)
   - Updates base images: `python:3.11.10-slim`
   - Pins digests for reproducibility

4. **Docker Compose** (`docker-compose*.yml`)
   - Updates service images if specified

5. **GitHub Actions** (`.github/workflows/*.yml`)
   - Updates action versions
   - Pins to SHAs (already handled by Pinact)

## Workflow

1. **Renovate creates PR**: Weekly schedule or when vulnerabilities detected
2. **CI runs**: Tests, linting, security scans
3. **Auto-merge** (if enabled): Patches auto-merge after CI passes
4. **Manual review** (if required): Major/minor updates need approval

## Branch Naming

Renovate creates branches with prefix `renovate/`:
- `renovate/all-minor-patch`
- `renovate/docker-python-3.x`
- `renovate/npm-react-18.x`

## Disabling Dependabot

Since Renovate is more comprehensive, you can disable Dependabot:

1. Delete `.github/dependabot.yml`, or
2. Keep it for security-only updates (complementary)

## Manual Updates

For manual dependency updates, use:

```bash
# Check what Renovate would update
renovate --dry-run

# Or use the update-dependencies command
update-dependencies
```

## Troubleshooting

### Renovate not running

1. Check GitHub App is installed: https://github.com/settings/installations
2. Verify `renovate.json` exists in repository root
3. Check Renovate logs in GitHub Actions (if self-hosted)

### Too many PRs

Adjust in `renovate.json`:
```json
{
  "prConcurrentLimit": 3,
  "prHourlyLimit": 1
}
```

### Want more frequent updates

Change schedule:
```json
{
  "schedule": ["before 4am every day"]
}
```

## Related

- [Renovate Documentation](https://docs.renovatebot.com/)
- [Renovate GitHub App](https://github.com/apps/renovate)
- [Dependency Updates Rule](.cursor/rules/dependency_updates.mdc)

