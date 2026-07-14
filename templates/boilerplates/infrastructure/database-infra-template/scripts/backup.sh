#!/usr/bin/env sh
set -eu
engine="${1:-postgresql}"
case "$engine" in
  postgresql) sh postgresql/scripts/backup.sh ;;
  mysql) sh mysql/scripts/backup.sh ;;
  *) echo "unsupported engine: $engine" >&2; exit 2 ;;
esac

