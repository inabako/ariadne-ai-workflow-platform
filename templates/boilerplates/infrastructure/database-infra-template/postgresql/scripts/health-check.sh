#!/usr/bin/env sh
set -eu
docker compose -f ../docker-compose/compose.yaml exec postgresql pg_isready -U "${POSTGRES_ADMIN_USER:-postgres_admin}" -d "${POSTGRES_DB:-app_db}"

