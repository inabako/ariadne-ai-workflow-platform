#!/usr/bin/env sh
set -eu

component="${1:-redis}"
test "$component" = "redis"
docker compose -f redis/docker-compose/compose.yaml --env-file redis/docker-compose/env.example down

