#!/usr/bin/env sh
set -eu
output_dir="${1:-test-evidence/database}"
mkdir -p "$output_dir"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$output_dir/collected-at.txt"
echo "Collect DB validation outputs into $output_dir. Do not write secrets."

