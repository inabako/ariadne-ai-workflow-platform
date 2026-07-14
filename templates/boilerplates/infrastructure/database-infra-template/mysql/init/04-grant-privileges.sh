#!/usr/bin/env sh
set -eu

database="${MYSQL_DATABASE:-app_db}"
app_user="${MYSQL_APP_USER:-app_user}"

mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<SQL
REVOKE ALL PRIVILEGES, GRANT OPTION FROM '$app_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX ON \`$database\`.* TO '$app_user'@'%';
FLUSH PRIVILEGES;
SQL

