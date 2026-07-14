#!/usr/bin/env sh
set -eu

backup_file="${1:-./evidence/redis-backup/dump.rdb}"
container="${REDIS_CONTAINER:-redis}"
test -s "$backup_file"
docker cp "$backup_file" "$container:/data/dump.rdb"
docker restart "$container" >/dev/null
echo "redis restore file applied: $backup_file"

