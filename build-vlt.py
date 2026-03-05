#!/usr/bin/env python3
"""
src/ を ZIP 圧縮し、リポジトリ名.vlt として保存する。
既存の .vlt は上書きする。
"""
import zipfile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / "src"


def get_repo_name() -> str:
    """Git のリポジトリ名を取得。失敗時はカレントディレクトリ名を使う。"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(r.stdout.strip()).name
    except (subprocess.CalledProcessError, FileNotFoundError):
        return REPO_ROOT.name


def build_vlt(output_name: str | None = None) -> Path:
    """src/ の中身を ZIP 化し .vlt として保存。"""
    if not SRC_DIR.is_dir():
        print(f"エラー: {SRC_DIR} が見つかりません。", file=sys.stderr)
        sys.exit(1)

    name = (output_name or get_repo_name()).removesuffix(".vlt")
    out_path = REPO_ROOT / f"{name}.vlt"

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(SRC_DIR.rglob("*")):
            if f.is_file():
                arcname = f.relative_to(SRC_DIR)
                zf.write(f, arcname)

    print(f"作成しました: {out_path}")
    return out_path


if __name__ == "__main__":
    output_name = sys.argv[1] if len(sys.argv) > 1 else None
    build_vlt(output_name)
