# SSL Certificate Fix - curl Migration

## Problem

The setup scripts (`setup-tools.sh`) were using Python's `urllib.request.urlopen()` which failed with SSL certificate verification errors on macOS because Python couldn't access the system's certificate store.

## Solution

Replaced Python's `urllib.request` with `curl` for all HTTP downloads. `curl` uses the system's certificate store, which is properly configured on both macOS and Linux.

## Compatibility

### ✅ Works Out of the Box

- **macOS**: `curl` is installed by default
- **Ubuntu/Debian**: `curl` is installed by default
- **CI/CD (GitHub Actions)**: Ubuntu runners have `curl` by default

### ⚠️ Requires Installation

- **Docker containers** (if running setup scripts inside):
  - Debian/Ubuntu-based: `RUN apt-get update && apt-get install -y curl`
  - Alpine-based: `RUN apk add --no-cache curl`
  
- **Minimal Linux distributions**: May need to install `curl` manually

## Current Usage

The setup scripts are **NOT** currently run inside application Docker containers. They run on:

1. **Host machine** (macOS/Linux) - `curl` available by default
2. **CI runners** (Ubuntu) - `curl` available by default
3. **DevContainers** (if configured) - may need `curl` added to base image

## Changes Made

1. **`fetch_latest_release()`**: Uses `curl` to fetch GitHub API responses
2. **`download_and_extract()`**: Downloads files using `curl`, then extracts with Python
3. **`ensure_hadolint()`**: Downloads binary directly using `curl`
4. **Added curl check**: Scripts now verify `curl` is available and provide helpful error messages

## Files Updated

- `scripts/tooling/setup-tools.sh`
- `.checks/scripts/tooling/setup-tools.sh`
- `SECURITY_SETUP.md` (documentation)

## Testing

The scripts have been syntax-checked and are ready to use. They will:

1. Check for `curl` availability on startup
2. Provide helpful error messages if `curl` is missing
3. Work correctly on macOS, Ubuntu, and other Linux distributions with `curl` installed

## Future Considerations

If you need to run setup scripts inside Docker containers:

1. Add `curl` to your Dockerfile:
   ```dockerfile
   RUN apt-get update && apt-get install -y curl
   ```

2. Or use a base image that includes `curl` (most Debian/Ubuntu-based images do)

3. The scripts will automatically detect if `curl` is missing and provide installation instructions

