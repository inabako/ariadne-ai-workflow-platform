#!/usr/bin/env sh
set -eu

: "${LDAP_BASE_DN:?LDAP_BASE_DN is required}"
: "${LDAP_ADMIN_PASSWORD:?LDAP_ADMIN_PASSWORD is required}"
container="${LDAP_CONTAINER:-openldap}"
for file in openldap/ldif/*.ldif; do
  if [ "$(basename "$file")" = "00-base.ldif" ]; then
    if docker exec "$container" ldapsearch -x -H ldap://localhost -b "$LDAP_BASE_DN" -D "cn=admin,$LDAP_BASE_DN" -w "$LDAP_ADMIN_PASSWORD" -s base dn >/dev/null 2>&1; then
      echo "base dn already exists; skipping $file"
      continue
    fi
  fi
  echo "applying $file"
  docker exec -i "$container" ldapadd -x -H ldap://localhost -D "cn=admin,$LDAP_BASE_DN" -w "$LDAP_ADMIN_PASSWORD" < "$file"
done
