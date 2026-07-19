#!/usr/bin/env sh
set -eu

app_user="${POSTGRES_APP_USER:-app_user}"
database="${POSTGRES_DB:-app_db}"
schema="${POSTGRES_SCHEMA:-app}"

psql --username "$POSTGRES_USER" --dbname "$database" <<SQL
GRANT USAGE ON SCHEMA "$schema" TO "$app_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA "$schema" TO "$app_user";
ALTER DEFAULT PRIVILEGES IN SCHEMA "$schema" GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "$app_user";
SQL

