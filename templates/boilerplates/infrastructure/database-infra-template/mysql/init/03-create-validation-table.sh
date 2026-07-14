#!/usr/bin/env sh
set -eu

database="${MYSQL_DATABASE:-app_db}"

mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$database" <<SQL
CREATE TABLE IF NOT EXISTS validation_probe (
  id INT AUTO_INCREMENT PRIMARY KEY,
  probe_key VARCHAR(128) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
SQL

