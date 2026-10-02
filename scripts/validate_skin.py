#!/usr/bin/env python3
"""Check source structure and shipped package contents; this is not a VLC GUI test."""
import importlib.util
import io
from pathlib import Path, PurePosixPath
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_NAME = 'My-MinimalX-JPMod.vlt'


def validate_source(source):
    source = Path(source)
    errors = []
    try:
        theme = ET.parse(source / 'theme.xml').getroot()
    except (OSError, ET.ParseError) as error:
        return ['theme.xml: ' + str(error)]
    if theme.tag != 'Theme' or theme.get('version') != '2.0':
        errors.append('Expected VLC Skins2 Theme version 2.0')
    ids = set()
    for element in theme.iter():
        identifier = element.get('id')
        if identifier:
            if identifier in ids:
                errors.append('Duplicate skin id: ' + identifier)
            ids.add(identifier)
        name = element.get('file')
        if name:
            asset = source / name
            if not asset.resolve().is_relative_to(source.resolve()) or not asset.is_file():
                errors.append('Missing or external asset: ' + name)
    return errors


def builder():
    spec = importlib.util.spec_from_file_location('build_vlt', ROOT / 'build-vlt.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_archive(expected, archive):
    """Compare unique member names and bytes, allowing ZIP encoding differences."""
    try:
        with zipfile.ZipFile(archive) as package:
            if len(package.namelist()) != len(expected) or set(package.namelist()) != set(expected):
                raise ValueError('Archive entries do not match source')
            for name, content in expected.items():
                if package.getinfo(name).compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    raise ValueError('Archive must use stored or deflated entries: ' + name)
                if package.read(name) != content:
                    raise ValueError('Archive content mismatch: ' + name)
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError, zlib.error) as error:
        raise ValueError('Cannot read package: ' + str(error)) from error


def validate_package(source, archive):
    source = Path(source)
    expected = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob('*') if p.is_file()}
    validate_archive(expected, archive)


def validate_git_package(repo, revision):
    """Validate and return the actual Git package blob without executing candidate code."""
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])

    expected = {}
    package = None
    records = git('ls-tree', '-r', '-z', revision, '--', 'src', ARTIFACT_NAME).split(b'\0')
    for record in filter(None, records):
        metadata, raw_name = record.split(b'\t', 1)
        mode, kind, blob = metadata.decode('ascii').split()
        name = raw_name.decode('utf-8')
        if mode not in {'100644', '100755'} or kind != 'blob':
            raise ValueError('Candidate source and package must contain ordinary files only')
        content = git('cat-file', 'blob', blob)
        if name == ARTIFACT_NAME:
            package = content
        else:
            relative = PurePosixPath(name).relative_to('src').as_posix()
            if '..' in PurePosixPath(relative).parts:
                raise ValueError('Candidate source must contain ordinary files only')
            expected[relative] = content
    if 'theme.xml' not in expected:
        raise ValueError('Candidate source must contain theme.xml')
    if package is None:
        raise ValueError('Candidate must track ' + ARTIFACT_NAME)
    validate_archive(expected, io.BytesIO(package))
    return package


def main():
    errors = validate_source(ROOT / 'src')
    if errors:
        raise SystemExit('\n'.join(errors))
    subprocess.run(['git', 'ls-files', '--error-unmatch', '--', ARTIFACT_NAME],
                   cwd=ROOT, stdout=subprocess.DEVNULL, check=True)
    validate_package(ROOT / 'src', ROOT / ARTIFACT_NAME)
    with tempfile.TemporaryDirectory() as tmp:
        archive = builder().build_vlt(source_dir=ROOT / 'src', output_dir=tmp)
        validate_package(ROOT / 'src', archive)
    print('VLC XML, referenced assets, tracked and fresh .vlt contents verified; GUI not evaluated.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
