#!/usr/bin/env sh
set -eu
sh common/scripts/collect-evidence.sh "${1:-test-evidence/database}"

