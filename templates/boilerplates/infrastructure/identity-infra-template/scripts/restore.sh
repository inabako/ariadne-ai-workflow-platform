#!/usr/bin/env sh
set -eu

component="${1:-openldap}"
backup_file="${2:-./evidence/openldap-backup/directory.ldif}"
test "$component" = "openldap"
openldap/scripts/restore.sh "$backup_file"

