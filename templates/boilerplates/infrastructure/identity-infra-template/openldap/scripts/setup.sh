#!/usr/bin/env sh
set -eu

environment="${1:-local}"
echo "setting up openldap identity for environment=${environment}"
docker compose -f openldap/docker-compose/compose.yaml --env-file openldap/docker-compose/env.example up -d

