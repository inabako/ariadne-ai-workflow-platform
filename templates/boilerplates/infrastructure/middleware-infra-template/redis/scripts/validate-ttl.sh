#!/usr/bin/env sh
set -eu

: "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"
container="${REDIS_CONTAINER:-redis}"
key="ariadne:validation:ttl"
ttl="${REDIS_TEST_TTL_SECONDS:-2}"
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" setex "$key" "$ttl" "expires" >/dev/null
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" ttl "$key" | grep -E '^[0-9]+$'
sleep "$ttl"
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" exists "$key" | grep '^0$'

