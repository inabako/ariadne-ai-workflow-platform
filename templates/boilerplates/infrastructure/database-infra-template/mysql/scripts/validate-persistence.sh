#!/usr/bin/env sh
set -eu
key="mysql-persistence-probe"
docker compose -f ../docker-compose/compose.yaml exec -T mysql mysql -uroot -p"${MYSQL_ROOT_PASSWORD:-change-me-in-secret-source}" "${MYSQL_DATABASE:-app_db}" -e "INSERT IGNORE INTO validation_probe(probe_key) VALUES ('$key');"
docker compose -f ../docker-compose/compose.yaml restart mysql
docker compose -f ../docker-compose/compose.yaml exec -T mysql mysql -uroot -p"${MYSQL_ROOT_PASSWORD:-change-me-in-secret-source}" "${MYSQL_DATABASE:-app_db}" -e "SELECT probe_key FROM validation_probe WHERE probe_key = '$key';"

