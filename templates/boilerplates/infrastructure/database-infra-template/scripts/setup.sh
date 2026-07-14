#!/usr/bin/env sh
set -eu
engine="${1:-postgresql}"
case "$engine" in
  postgresql) docker compose -f postgresql/docker-compose/compose.yaml up -d ;;
  mysql) docker compose -f mysql/docker-compose/compose.yaml up -d ;;
  *) echo "unsupported engine: $engine" >&2; exit 2 ;;
esac

