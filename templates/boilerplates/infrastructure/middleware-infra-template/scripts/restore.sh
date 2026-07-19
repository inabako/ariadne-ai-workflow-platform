#!/usr/bin/env sh
set -eu

component="${1:-redis}"
backup_file="${2:-./evidence/redis-backup/dump.rdb}"
test "$component" = "redis"
redis/scripts/restore.sh "$backup_file"

