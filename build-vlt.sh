#!/usr/bin/env bash
# src を zip 化して配布用の固定名で出力する
cd "$(dirname "$0")"
exec bash scripts/python.sh build-vlt.py "$@"
