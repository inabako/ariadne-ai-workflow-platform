#!/usr/bin/env sh
set -eu
mkdir -p ../../test-evidence/mysql/backup
docker compose -f ../docker-compose/compose.yaml exec -T mysql mysqldump -uroot -p"${MYSQL_ROOT_PASSWORD:-change-me-in-secret-source}" "${MYSQL_DATABASE:-app_db}" > "../../test-evidence/mysql/backup/mysql-backup.sql"
test -s "../../test-evidence/mysql/backup/mysql-backup.sql"

