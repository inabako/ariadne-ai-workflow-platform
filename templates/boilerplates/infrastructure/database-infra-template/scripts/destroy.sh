#!/usr/bin/env sh
set -eu
engine="${1:-postgresql}"
case "$engine" in
  postgresql) docker compose -f postgresql/docker-compose/compose.yaml down ;;
  mysql) docker compose -f mysql/docker-compose/compose.yaml down ;;
  *) echo "unsupported engine: $engine" >&2; exit 2 ;;
esac
echo "Volumes are preserved. Remove volumes only after explicit human approval."

