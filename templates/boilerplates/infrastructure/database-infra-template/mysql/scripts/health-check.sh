#!/usr/bin/env sh
set -eu
docker compose -f ../docker-compose/compose.yaml exec mysql mysqladmin ping -h localhost -uroot -p"${MYSQL_ROOT_PASSWORD:-change-me-in-secret-source}"

