#!/usr/bin/env python3
"""Preserve automatic skin packaging without incorporating unstaged source edits."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_skin import ARTIFACT_NAME, builder, validate_git_package, validate_source


def main():
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode().split('\0')
    rebuild = any(p.startswith('src/') or p == 'build-vlt.py' for p in staged)
    if not rebuild and ARTIFACT_NAME not in staged:
        return 0
    if rebuild:
        if subprocess.run(['git', 'diff', '--quiet', '--', 'src', 'build-vlt.py'], cwd=ROOT).returncode:
            raise ValueError('Unstaged skin/build changes exist; stage the intended complete source before commit')
        if subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--', 'src'], cwd=ROOT).strip():
            raise ValueError('Untracked source files exist; stage intended assets before packaging')
        errors = validate_source(ROOT / 'src')
        if errors:
            raise ValueError('\n'.join(errors))
        output = builder().build_vlt()
        subprocess.run(['git', 'add', '--', output.name], cwd=ROOT, check=True)
    tree = subprocess.check_output(['git', 'write-tree'], cwd=ROOT).decode().strip()
    validate_git_package(ROOT, tree)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
