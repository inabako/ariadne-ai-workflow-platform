#!/usr/bin/env sh
set -eu

component="${1:-openldap}"
common/scripts/collect-evidence.sh "$component"

