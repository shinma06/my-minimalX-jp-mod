#!/usr/bin/env bash
# Shared runtime selection for Git for Windows, macOS and Linux.
set -euo pipefail
runtime="${HARNESS_PYTHON:-$(git config --get harness.python || true)}"
if [ -n "$runtime" ]; then exec "$runtime" "$@"; fi
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
    exec "$candidate" "$@"
  fi
done
if command -v py >/dev/null 2>&1 && py -3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' >/dev/null 2>&1; then
  exec py -3 "$@"
fi
echo 'Python 3.11+ required. Run bootstrap.py with Python or set HARNESS_PYTHON.' >&2
exit 1
