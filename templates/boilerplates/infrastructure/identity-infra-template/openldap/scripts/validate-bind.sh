#!/usr/bin/env sh
set -eu

: "${LDAP_BASE_DN:?LDAP_BASE_DN is required}"
: "${LDAP_ADMIN_PASSWORD:?LDAP_ADMIN_PASSWORD is required}"
container="${LDAP_CONTAINER:-openldap}"
docker exec "$container" ldapwhoami -x -H ldap://localhost -D "cn=admin,$LDAP_BASE_DN" -w "$LDAP_ADMIN_PASSWORD" | grep "dn:cn=admin"

