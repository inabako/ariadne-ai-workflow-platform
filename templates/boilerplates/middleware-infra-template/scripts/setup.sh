#!/usr/bin/env sh
set -eu

component="redis"
environment="local"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --component) component="$2"; shift 2 ;;
    --environment) environment="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

test "$component" = "redis"
echo "setup component=$component environment=$environment"
docker compose -f redis/docker-compose/compose.yaml --env-file redis/docker-compose/env.example up -d

