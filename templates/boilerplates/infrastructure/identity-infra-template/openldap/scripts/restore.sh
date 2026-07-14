#!/usr/bin/env sh
set -eu

backup_file="${1:-./evidence/openldap-backup/directory.ldif}"
test -s "$backup_file"
echo "restore requires an approved maintenance window and stopped slapd process: $backup_file"
echo "Use slapadd in the copied target repository after approval."

