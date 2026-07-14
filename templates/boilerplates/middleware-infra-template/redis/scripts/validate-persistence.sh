#!/usr/bin/env sh
set -eu

: "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"
container="${REDIS_CONTAINER:-redis}"
key="ariadne:validation:persistence"
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" set "$key" "persisted" >/dev/null
docker restart "$container" >/dev/null
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" get "$key" | grep '^persisted$'

