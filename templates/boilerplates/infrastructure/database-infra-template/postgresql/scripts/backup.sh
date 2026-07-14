#!/usr/bin/env sh
set -eu
mkdir -p ../../test-evidence/postgresql/backup
docker compose -f ../docker-compose/compose.yaml exec -T postgresql pg_dump -U "${POSTGRES_ADMIN_USER:-postgres_admin}" "${POSTGRES_DB:-app_db}" > "../../test-evidence/postgresql/backup/postgresql-backup.sql"
test -s "../../test-evidence/postgresql/backup/postgresql-backup.sql"

