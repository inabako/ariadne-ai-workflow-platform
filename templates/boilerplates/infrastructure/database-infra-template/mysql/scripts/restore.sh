#!/usr/bin/env sh
set -eu
test -s "../../test-evidence/mysql/backup/mysql-backup.sql"
docker compose -f ../docker-compose/compose.yaml exec -T mysql mysql -uroot -p"${MYSQL_ROOT_PASSWORD:-change-me-in-secret-source}" "${MYSQL_DATABASE:-app_db}" < "../../test-evidence/mysql/backup/mysql-backup.sql"

