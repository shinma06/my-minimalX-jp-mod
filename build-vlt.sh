#!/usr/bin/env bash
# src を zip 化して リポジトリ名.vlt で上書きする
cd "$(dirname "$0")"
exec python3 build-vlt.py "$@"
