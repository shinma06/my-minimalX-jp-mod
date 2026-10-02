#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec bash scripts/python.sh scripts/bootstrap.py
