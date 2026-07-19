#!/usr/bin/env sh
set -eu

component="${1:-openldap}"
test "$component" = "openldap"
docker compose -f openldap/docker-compose/compose.yaml --env-file openldap/docker-compose/env.example down

