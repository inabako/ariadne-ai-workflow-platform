#!/usr/bin/env sh
set -eu
key="postgresql-persistence-probe"
schema="${POSTGRES_SCHEMA:-app}"
docker compose -f ../docker-compose/compose.yaml exec -T postgresql psql -U "${POSTGRES_ADMIN_USER:-postgres_admin}" "${POSTGRES_DB:-app_db}" -c "INSERT INTO \"$schema\".validation_probe(probe_key) VALUES ('$key') ON CONFLICT (probe_key) DO NOTHING;"
docker compose -f ../docker-compose/compose.yaml restart postgresql
docker compose -f ../docker-compose/compose.yaml exec -T postgresql psql -U "${POSTGRES_ADMIN_USER:-postgres_admin}" "${POSTGRES_DB:-app_db}" -c "SELECT probe_key FROM \"$schema\".validation_probe WHERE probe_key = '$key';"
