#!/usr/bin/env sh
set -eu

app_user="${POSTGRES_APP_USER:-app_user}"
app_password="${POSTGRES_APP_PASSWORD:-change-me-in-secret-source}"
database="${POSTGRES_DB:-app_db}"

psql --username "$POSTGRES_USER" --dbname "$database" <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$app_user') THEN
    CREATE USER "$app_user" WITH PASSWORD '$app_password';
  END IF;
END
\$\$;
GRANT CONNECT ON DATABASE "$database" TO "$app_user";
SQL

