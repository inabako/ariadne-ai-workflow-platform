#!/usr/bin/env sh
set -eu

: "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"
container="${REDIS_CONTAINER:-redis}"
backup_dir="${BACKUP_DIR:-./evidence/redis-backup}"
mkdir -p "$backup_dir"
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" save >/dev/null
docker cp "$container:/data/dump.rdb" "$backup_dir/dump.rdb"
test -s "$backup_dir/dump.rdb"
echo "redis backup created: $backup_dir/dump.rdb"

