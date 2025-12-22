#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="${ROOT_DIR}/.tools"
BIN_DIR="${TOOLS_DIR}/bin"

mkdir -p "${BIN_DIR}"
export PATH="${BIN_DIR}:${PATH}"

fetch_latest_release() {
  python - "$1" <<'PY'
import json, sys, urllib.request
repo = sys.argv[1]
with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/releases/latest") as response:
    data = json.load(response)
print(data["tag_name"])
PY
}

download_and_extract() {
  local url="$1"
  local dest_dir="$2"
  local strip_components="${3:-0}"
  python - "${url}" "${dest_dir}" "${strip_components}" <<'PY'
import io, tarfile, sys, urllib.request
url = sys.argv[1]
dest = sys.argv[2]
strip = int(sys.argv[3])
with urllib.request.urlopen(url) as response:
    data = response.read()
with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:
    members = tar.getmembers()
    if strip:
        for member in members:
            parts = member.name.split("/", strip)
            member.name = parts[-1] if len(parts) > strip else parts[0]
    tar.extractall(dest, members=members)
PY
}

ensure_pinact() {
  if command -v pinact >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release suzuki-shunsuke/pinact)"
  local url="https://github.com/suzuki-shunsuke/pinact/releases/download/${version}/pinact_linux_amd64.tar.gz"
  download_and_extract "${url}" "${BIN_DIR}"
  chmod +x "${BIN_DIR}/pinact"
}

ensure_actionlint() {
  if command -v actionlint >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release rhysd/actionlint)"
  local url="https://github.com/rhysd/actionlint/releases/download/${version}/actionlint_${version#v}_linux_amd64.tar.gz"
  download_and_extract "${url}" "${BIN_DIR}"
  chmod +x "${BIN_DIR}/actionlint"
}

ensure_shellcheck() {
  if command -v shellcheck >/dev/null 2>&1; then
    return
  fi
  local version
  version="$(fetch_latest_release koalaman/shellcheck)"
  local url="https://github.com/koalaman/shellcheck/releases/download/${version}/shellcheck-${version}.linux.x86_64.tar.xz"
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
  local url="https://github.com/aquasecurity/trivy/releases/download/${version}/trivy_${version#v}_Linux-64bit.tar.gz"
  download_and_extract "${url}" "${BIN_DIR}"
  chmod +x "${BIN_DIR}/trivy"
}

ensure_zizmor() {
  if command -v zizmor >/dev/null 2>&1; then
    return
  fi
  uv tool install zizmor
}

ensure_pinact
ensure_actionlint
ensure_shellcheck
ensure_trivy
ensure_zizmor
