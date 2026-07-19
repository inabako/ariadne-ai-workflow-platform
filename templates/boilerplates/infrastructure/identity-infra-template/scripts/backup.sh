#!/usr/bin/env sh
set -eu

component="${1:-openldap}"
test "$component" = "openldap"
openldap/scripts/backup.sh

