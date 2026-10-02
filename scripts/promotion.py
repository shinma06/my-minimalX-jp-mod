#!/usr/bin/env python3
"""Bind GUI acceptance to a fixed source, base, complete case set and shipped skin."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from verification import validate
from validate_skin import validate_git_package

CASE_PATH = 'docs/verification/cases.json'
MANIFEST_PATH = 'docs/verification/promotion.json'
LEGACY_BASE = '3c3cb11b9d290351b72be8bdb06549d24cddd4aa'


def base_case_ids(repo, base):
    # The observed pre-harness main has no case registry. Its first promotion still
    # requires the entire initial acceptance set; unknown missing registries fail.
    if base == LEGACY_BASE:
        return {f'UI-{number:03}' for number in range(1, 11)}
    return {c['id'] for c in read_json(repo, base, CASE_PATH)['cases']}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def read_json(repo, sha, path):
    return json.loads(git(repo, 'show', f'{sha}:{path}').decode('utf-8'))


def ancestor(repo, older, newer):
    if subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', older, newer],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        raise ValueError('Candidate/base/HEAD ancestry is inconsistent')


def artifact_digest(repo, candidate):
    """Read Git blobs as data only. Do not execute build scripts from a PR."""
    return hashlib.sha256(validate_git_package(repo, candidate)).hexdigest()


def manifest(repo, candidate, base):
    for sha in (candidate, base):
        if not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('Full candidate and base SHAs are required')
    ancestor(repo, base, candidate)
    cases = read_json(repo, candidate, CASE_PATH)
    errors = validate(cases)
    if errors:
        raise ValueError('\n'.join(errors))
    return {'schema_version': 1, 'candidate_sha': candidate, 'base_sha': base,
            'artifact_sha256': artifact_digest(repo, candidate),
            'case_ids': sorted(c['id'] for c in cases['cases']),
            'commits': git(repo, 'rev-list', '--reverse', f'{base}..{candidate}').decode().splitlines()}


def verify(repo, *, head, base, cases, candidate_record, develop):
    if not isinstance(candidate_record, dict):
        raise ValueError('Promotion manifest must be an object')
    candidate = candidate_record.get('candidate_sha')
    expected = manifest(repo, candidate, base)
    if candidate_record != expected:
        raise ValueError('Promotion manifest does not match current base, commits, cases or artifact')
    if not expected['commits']:
        raise ValueError('Promotion has no candidate commits')
    ancestor(repo, candidate, head)
    ancestor(repo, candidate, develop)
    changed = set(filter(None, git(repo, 'diff', '--name-only', '--no-renames', '-z', candidate, head).decode('utf-8').split('\0')))
    if changed - {CASE_PATH, MANIFEST_PATH}:
        raise ValueError('Candidate changed after freeze; only case results and promotion manifest may change')
    original = read_json(repo, candidate, CASE_PATH)
    definitions = lambda data: [{k: v for k, v in c.items() if k != 'result'} for c in data['cases']]
    if definitions(cases) != definitions(original):
        raise ValueError('Case definitions changed after candidate freeze')
    # A previously required case cannot disappear during promotion.
    if not base_case_ids(repo, base) <= set(expected['case_ids']):
        raise ValueError('Candidate removed a base case; review the case retirement separately')
    errors = validate(cases, candidate=candidate, artifact_hash=expected['artifact_sha256'])
    if errors:
        raise ValueError('\n'.join(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--output', type=Path, default=Path(MANIFEST_PATH))
    args = parser.parse_args()
    data = manifest(Path.cwd(), args.candidate, args.base)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print('Candidate recorded; run Computer Use and independent review before promotion.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
