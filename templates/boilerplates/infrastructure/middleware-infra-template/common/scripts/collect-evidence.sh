#!/usr/bin/env sh
set -eu

component="${1:-redis}"
evidence_dir="${EVIDENCE_DIR:-./evidence/$component}"
mkdir -p "$evidence_dir"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$evidence_dir/collected-at.txt"
echo "component=$component" > "$evidence_dir/component.txt"
echo "secret_values=redacted" > "$evidence_dir/redaction.txt"

