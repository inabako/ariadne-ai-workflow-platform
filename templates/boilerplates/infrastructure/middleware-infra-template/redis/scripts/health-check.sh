#!/usr/bin/env sh
set -eu

: "${REDIS_PASSWORD:?REDIS_PASSWORD is required}"
container="${REDIS_CONTAINER:-redis}"
docker exec "$container" redis-cli -a "$REDIS_PASSWORD" ping | grep PONG

