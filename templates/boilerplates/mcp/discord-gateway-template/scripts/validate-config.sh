#!/usr/bin/env bash
set -euo pipefail
test -f config/gateway.example.yaml
test -f config/discord.example.yaml
test -f config/runtime.example.yaml

