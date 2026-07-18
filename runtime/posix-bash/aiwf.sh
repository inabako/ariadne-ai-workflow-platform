#!/usr/bin/env bash
set -Eeuo pipefail

export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8
if [[ -z "${LANG:-}" ]]; then
  export LANG=C.UTF-8
fi

command_name="${1:-help}"
if (($# > 0)); then
  shift
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd -- "$script_dir/../.." && pwd -P)"
runtime_root="$repo_root/runtime"
ctl_path="$runtime_root/common/ctl.py"
bom_tool_path="$runtime_root/tools/utf8_bom.py"
spec_sync_path="$runtime_root/tools/pytest_ut_spec_sync.py"
spec_path="$repo_root/docs/reference/runtime-pytest-ut/case-specification.md"

assert_aiwf_repo_root() {
  if [[ ! -f "$ctl_path" ]]; then
    printf 'runtime/common/ctl.py was not found. Run this script from the Ariadne repository checkout.\n' >&2
    exit 1
  fi
  if [[ ! -d "$repo_root/.git" ]]; then
    printf '.git was not found under the resolved repository root: %s\n' "$repo_root" >&2
    exit 1
  fi
}

get_uv_path() {
  if command -v uv >/dev/null 2>&1; then
    command -v uv
    return 0
  fi
  printf 'uv was not found on PATH. Install uv or add it to PATH before running Ariadne runtime.\n' >&2
  exit 127
}

invoke_uv() {
  local working_directory="$1"
  shift
  local uv_path
  uv_path="$(get_uv_path)"
  (
    cd "$working_directory"
    "$uv_path" "$@"
  )
}

show_help() {
  cat <<EOF
Ariadne POSIX bash runtime

Usage:
  ./runtime/posix-bash/aiwf.sh ctl <aiwfctl-args>
  ./runtime/posix-bash/aiwf.sh doctor [aiwfctl-doctor-args]
  ./runtime/posix-bash/aiwf.sh pytest [pytest-args]
  ./runtime/posix-bash/aiwf.sh spec-check
  ./runtime/posix-bash/aiwf.sh bom-scan [utf8_bom scan args]
  ./runtime/posix-bash/aiwf.sh bom-strip [utf8_bom strip args]

Resolved paths:
  Repo root    : $repo_root
  Runtime root : $runtime_root

Linux / WSL / macOS:
  AI workflows on Linux, WSL, or macOS should start here first, then delegate through aiwfctl.
EOF
}

assert_aiwf_repo_root

case "$command_name" in
  help)
    show_help
    ;;
  ctl)
    invoke_uv "$repo_root" run --project "$runtime_root" python "$ctl_path" --repo-root "$repo_root" "$@"
    ;;
  doctor)
    invoke_uv "$repo_root" run --project "$runtime_root" python "$ctl_path" --repo-root "$repo_root" doctor "$@"
    ;;
  pytest)
    invoke_uv "$runtime_root" run pytest "$@"
    ;;
  spec-check)
    invoke_uv "$repo_root" run --project "$runtime_root" python "$spec_sync_path" --spec "$spec_path" --runtime-root "$runtime_root" check "$@"
    ;;
  bom-scan)
    invoke_uv "$repo_root" run --project "$runtime_root" python "$bom_tool_path" --repo-root "$repo_root" scan "$@"
    ;;
  bom-strip)
    invoke_uv "$repo_root" run --project "$runtime_root" python "$bom_tool_path" --repo-root "$repo_root" strip "$@"
    ;;
  *)
    printf 'Unknown command: %s\n\n' "$command_name" >&2
    show_help >&2
    exit 2
    ;;
esac
