#!/usr/bin/env sh
set -eu
echo "Start PostgreSQL compose unit. Copy env.example to an approved env file before shared use."
docker compose -f ../docker-compose/compose.yaml up -d

