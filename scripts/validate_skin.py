#!/usr/bin/env python3
"""Check source structure and a freshly built package; this is not a VLC GUI test."""
import importlib.util
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


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


def validate_package(source, archive):
    source = Path(source)
    expected = {p.relative_to(source).as_posix(): p.read_bytes() for p in source.rglob('*') if p.is_file()}
    with zipfile.ZipFile(archive) as package:
        if package.testzip() or len(package.namelist()) != len(expected) or set(package.namelist()) != set(expected):
            raise ValueError('Archive entries do not match source')
        for name, content in expected.items():
            if package.read(name) != content:
                raise ValueError('Archive content mismatch: ' + name)


def main():
    errors = validate_source(ROOT / 'src')
    if errors:
        raise SystemExit('\n'.join(errors))
    with tempfile.TemporaryDirectory() as tmp:
        archive = builder().build_vlt(output_dir=tmp)
        validate_package(ROOT / 'src', archive)
    print('VLC XML, referenced assets and fresh .vlt contents verified; GUI not evaluated.')


if __name__ == '__main__':
    main()
