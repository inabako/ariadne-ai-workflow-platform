#!/usr/bin/env sh
set -eu
test -s "../../test-evidence/postgresql/backup/postgresql-backup.sql"
docker compose -f ../docker-compose/compose.yaml exec -T postgresql psql -U "${POSTGRES_ADMIN_USER:-postgres_admin}" "${POSTGRES_DB:-app_db}" < "../../test-evidence/postgresql/backup/postgresql-backup.sql"

