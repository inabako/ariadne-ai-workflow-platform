#!/usr/bin/env bash
set -euo pipefail
mkdir -p evidence
python -m pytest | tee evidence/pytest.log

