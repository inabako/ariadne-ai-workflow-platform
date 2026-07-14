#!/usr/bin/env sh
set -eu

: "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"
container="${REDIS_CONTAINER:-redis}"
key="ariadne:validation:read-write"
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" set "$key" "ok" >/dev/null
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" get "$key" | grep '^ok$'

