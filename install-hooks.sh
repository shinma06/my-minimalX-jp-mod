#!/bin/sh
# githooks を .git/hooks にコピーする（コミット前に .vlt を自動ビルドするため）
set -e
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
cp githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "pre-commit フックをインストールしました。これ以降、コミット前に .vlt が自動でビルドされます。"
