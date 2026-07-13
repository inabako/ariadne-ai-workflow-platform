#!/usr/bin/env sh
set -eu

database="${POSTGRES_DB:-app_db}"
schema="${POSTGRES_SCHEMA:-app}"

psql --username "$POSTGRES_USER" --dbname "$database" <<SQL
CREATE SCHEMA IF NOT EXISTS "$schema";
CREATE TABLE IF NOT EXISTS "$schema".validation_probe (
  id SERIAL PRIMARY KEY,
  probe_key TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
SQL

