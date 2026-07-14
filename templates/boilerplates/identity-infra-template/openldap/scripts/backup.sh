#!/usr/bin/env sh
set -eu

: "${LDAP_BASE_DN:?LDAP_BASE_DN is required}"
: "${LDAP_ADMIN_PASSWORD:?LDAP_ADMIN_PASSWORD is required}"
container="${LDAP_CONTAINER:-openldap}"
backup_dir="${BACKUP_DIR:-./evidence/openldap-backup}"
mkdir -p "$backup_dir"
docker exec "$container" slapcat > "$backup_dir/directory.ldif"
docker exec "$container" slapcat -n 0 > "$backup_dir/config.ldif"
test -s "$backup_dir/directory.ldif"
test -s "$backup_dir/config.ldif"
echo "openldap backup created: $backup_dir"

