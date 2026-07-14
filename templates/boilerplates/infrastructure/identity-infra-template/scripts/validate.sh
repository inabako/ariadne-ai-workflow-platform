#!/usr/bin/env sh
set -eu

component="openldap"
environment="local"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --component) component="$2"; shift 2 ;;
    --environment) environment="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

test "$component" = "openldap"
echo "validate component=$component environment=$environment"
openldap/scripts/health-check.sh
openldap/scripts/validate-bind.sh
openldap/scripts/validate-user-search.sh
openldap/scripts/validate-group-search.sh

