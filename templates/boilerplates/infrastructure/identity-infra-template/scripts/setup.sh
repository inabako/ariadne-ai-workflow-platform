#!/usr/bin/env sh
set -eu

component="openldap"
environment="local"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --component) component="$2"; shift 2 ;;
    --environment) environment="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

test "$component" = "openldap"
echo "setup component=$component environment=$environment"
docker compose -f openldap/docker-compose/compose.yaml --env-file openldap/docker-compose/env.example up -d

