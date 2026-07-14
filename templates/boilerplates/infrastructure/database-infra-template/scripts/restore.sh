#!/usr/bin/env sh
set -eu
engine="${1:-postgresql}"
case "$engine" in
  postgresql) sh postgresql/scripts/restore.sh ;;
  mysql) sh mysql/scripts/restore.sh ;;
  *) echo "unsupported engine: $engine" >&2; exit 2 ;;
esac

