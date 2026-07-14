#!/usr/bin/env sh
set -eu

component="${1:-redis}"
common/scripts/collect-evidence.sh "$component"

