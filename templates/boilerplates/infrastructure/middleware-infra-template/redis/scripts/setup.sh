#!/usr/bin/env sh
set -eu

environment="${1:-local}"
echo "setting up redis middleware for environment=${environment}"
docker compose -f redis/docker-compose/compose.yaml --env-file redis/docker-compose/env.example up -d

