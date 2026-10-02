#!/usr/bin/env python3
"""Build a reproducible VLC skin; the distribution name is stable across worktrees."""
import argparse
from pathlib import Path
import zipfile

REPO_ROOT = Path(__file__).resolve().parent
SRC_DIR = REPO_ROOT / 'src'
ARTIFACT_NAME = 'My-MinimalX-JPMod.vlt'


def build_vlt(output_name=None, *, source_dir=SRC_DIR, output_dir=REPO_ROOT):
    source_dir, output_dir = Path(source_dir), Path(output_dir)
    if not (source_dir / 'theme.xml').is_file():
        raise ValueError('Source must contain theme.xml')
    name = (output_name or ARTIFACT_NAME).removesuffix('.vlt') + '.vlt'
    if Path(name).name != name or '/' in name or '\\' in name:
        raise ValueError('Output name must be a filename; use --output-dir for directories')
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / name
    if out_path.resolve().is_relative_to(source_dir.resolve()):
        raise ValueError('Output must be outside the source directory')
    files = sorted((p for p in source_dir.rglob('*') if p.is_file()),
                   key=lambda p: p.relative_to(source_dir).as_posix().encode('utf-8'))
    if any(p.is_symlink() or not p.resolve().is_relative_to(source_dir.resolve()) for p in files):
        raise ValueError('Source must not contain external or symlinked files')
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            entry = zipfile.ZipInfo(path.relative_to(source_dir).as_posix(), (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, path.read_bytes(), compresslevel=9)
    return out_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', nargs='?')
    parser.add_argument('--output-dir', type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    print(build_vlt(args.name, output_dir=args.output_dir))
