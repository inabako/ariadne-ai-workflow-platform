#!/usr/bin/env sh
set -eu

component="${1:-redis}"
test "$component" = "redis"
redis/scripts/backup.sh

