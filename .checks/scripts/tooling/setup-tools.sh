#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/.tools"
BIN_DIR="${TOOLS_DIR}/bin"

mkdir -p "${BIN_DIR}"
export PATH="${BIN_DIR}:${PATH}"

# Verify curl is available (required for downloads)
if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required but not found. Please install curl:" >&2
    echo "  - macOS: Already installed by default" >&2
    echo "  - Ubuntu/Debian: sudo apt-get install -y curl" >&2
    echo "  - Alpine: apk add --no-cache curl" >&2
    echo "  - Docker: Add 'curl' to your Dockerfile's apt-get/apk install command" >&2
    exit 1
fi

# Detect OS and architecture
detect_os() {
    case "$(uname -s)" in
        Linux*)
            echo "linux"
            ;;
        Darwin*)
            echo "darwin"
            ;;
        *)
            echo "linux"  # Default to linux
            ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64)
            echo "amd64"
            ;;
        arm64|aarch64)
            echo "arm64"
            ;;
        *)
            echo "amd64"  # Default to amd64
            ;;
    esac
}

OS="$(detect_os)"
ARCH="$(detect_arch)"

fetch_latest_release() {
  local repo="$1"
  curl -sSL "https://api.github.com/repos/${repo}/releases/latest" | \
    python3 -c "import json, sys; print(json.load(sys.stdin)['tag_name'])"
}

download_and_extract() {
  local url="$1"
  local dest_dir="$2"
  local strip_components="${3:-0}"
  local temp_file
  temp_file="$(mktemp)"
  
  # Download using curl (handles SSL certificates properly)
  curl -sSL -o "${temp_file}" "${url}"
  
  # Extract using Python (handles both tar and zip)
  python3 - "${temp_file}" "${dest_dir}" "${strip_components}" <<'PY'
import io, tarfile, sys, zipfile
temp_file = sys.argv[1]
dest = sys.argv[2]
strip = int(sys.argv[3])
with open(temp_file, 'rb') as f:
    data = f.read()
# Try tar first, then zip
try:
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:
        members = tar.getmembers()
        if strip:
            for member in members:
                parts = member.name.split("/", strip)
                member.name = parts[-1] if len(parts) > strip else parts[0]
        tar.extractall(dest, members=members)
except (tarfile.TarError, EOFError):
    # Try zip
    with zipfile.ZipFile(io.BytesIO(data)) as zip_file:
        zip_file.extractall(dest)
PY
  rm -f "${temp_file}"
}

ensure_pinact() {
  if command -v pinact >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release suzuki-shunsuke/pinact)"
  local arch_suffix
  if [ "${ARCH}" = "arm64" ]; then
    arch_suffix="arm64"
  else
    arch_suffix="amd64"
  fi
  local url="https://github.com/suzuki-shunsuke/pinact/releases/download/${version}/pinact_${OS}_${arch_suffix}.tar.gz"
  download_and_extract "${url}" "${BIN_DIR}"
  chmod +x "${BIN_DIR}/pinact"
}

ensure_actionlint() {
  if command -v actionlint >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release rhysd/actionlint)"
  local arch_suffix
  if [ "${ARCH}" = "arm64" ]; then
    arch_suffix="arm64"
  else
    arch_suffix="amd64"
  fi
  local url="https://github.com/rhysd/actionlint/releases/download/${version}/actionlint_${version#v}_${OS}_${arch_suffix}.tar.gz"
  download_and_extract "${url}" "${BIN_DIR}"
  chmod +x "${BIN_DIR}/actionlint"
}

ensure_shellcheck() {
  if command -v shellcheck >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release koalaman/shellcheck)"
  local arch_suffix
  if [ "${ARCH}" = "arm64" ]; then
    arch_suffix="aarch64"
  else
    arch_suffix="x86_64"
  fi
  local os_suffix
  if [ "${OS}" = "darwin" ]; then
    os_suffix="darwin"
  else
    os_suffix="linux"
  fi
  local url="https://github.com/koalaman/shellcheck/releases/download/${version}/shellcheck-${version}.${os_suffix}.${arch_suffix}.tar.xz"
  download_and_extract "${url}" "${TOOLS_DIR}"
  chmod +x "${TOOLS_DIR}/shellcheck-${version}/shellcheck"
  ln -sf "${TOOLS_DIR}/shellcheck-${version}/shellcheck" "${BIN_DIR}/shellcheck"
}

ensure_trivy() {
  if command -v trivy >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release aquasecurity/trivy)"
  local arch_suffix
  if [ "${ARCH}" = "arm64" ]; then
    arch_suffix="ARM64"
  else
    arch_suffix="64bit"
  fi
  local os_suffix
  if [ "${OS}" = "darwin" ]; then
    os_suffix="macOS"
  else
    os_suffix="Linux"
  fi
  local url="https://github.com/aquasecurity/trivy/releases/download/${version}/trivy_${version#v}_${os_suffix}-${arch_suffix}.tar.gz"
  download_and_extract "${url}" "${BIN_DIR}"
  chmod +x "${BIN_DIR}/trivy"
}

ensure_zizmor() {
  if command -v zizmor >/dev/null 2>&1; then
    return
  fi
  # zizmor is installed via uv tool
  if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv is required to install zizmor" >&2
    return 1
  fi
  uv tool install zizmor
}

ensure_hadolint() {
  if command -v hadolint >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release hadolint/hadolint)"
  local arch_suffix
  if [ "${ARCH}" = "arm64" ]; then
    arch_suffix="arm64"
  else
    arch_suffix="x86_64"
  fi
  local os_suffix
  if [ "${OS}" = "darwin" ]; then
    os_suffix="Darwin"
  else
    os_suffix="Linux"
  fi
  local url="https://github.com/hadolint/hadolint/releases/download/${version}/hadolint-${os_suffix}-${arch_suffix}"
  # Download binary directly using curl (handles SSL certificates properly)
  curl -sSL -o "${BIN_DIR}/hadolint" "${url}"
  chmod +x "${BIN_DIR}/hadolint"
}

ensure_pinact
ensure_actionlint
ensure_shellcheck
ensure_trivy
ensure_zizmor
ensure_hadolint
