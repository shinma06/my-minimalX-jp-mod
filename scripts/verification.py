#!/usr/bin/env python3
"""Validate reproducible GUI cases; acceptance requires observed evidence for one build."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {'pending', 'blocked', 'fail', 'pass'}


def validate(data, *, candidate=None, artifact_hash=None):
    errors = []
    if data.get('schema_version') != 1 or data.get('reference_product_id') != '9WZDNCRFJ3PT':
        errors.append('Expected schema_version 1 and Windows Media Player product 9WZDNCRFJ3PT')
    cases = data.get('cases')
    if not isinstance(cases, list) or not cases:
        return errors + ['At least one case is required']
    ids = set()
    for case in cases:
        if not isinstance(case, dict):
            errors.append('Case must be an object')
            continue
        identifier = case.get('id')
        if not isinstance(identifier, str) or not re.fullmatch(r'UI-[0-9]{3}', identifier) or identifier in ids:
            errors.append('Missing, invalid or duplicate case id')
        ids.add(str(identifier))
        for key in ('title', 'initial_state', 'expected'):
            if not isinstance(case.get(key), str) or not case[key].strip():
                errors.append(f'{identifier}: {key} is required')
        if not isinstance(case.get('steps'), list) or not case['steps'] or not all(isinstance(s, str) and s.strip() for s in case['steps']):
            errors.append(f'{identifier}: nonempty steps are required')
        if case.get('required_execution') != 'computer_use':
            errors.append(f'{identifier}: computer_use is required by the project request')
        result = case.get('result', {})
        if not isinstance(result, dict):
            errors.append(f'{identifier}: result must be an object')
            continue
        status = result.get('status')
        if status not in STATUSES:
            errors.append(f'{identifier}: invalid result status')
        for key in ('owner', 'next_action'):
            if not isinstance(result.get(key), str) or not result[key].strip():
                errors.append(f'{identifier}: {key} is required')
        if status == 'pass':
            for key in ('observed_at', 'reference_version', 'vlc_version', 'environment', 'fixture_sha256'):
                if not isinstance(result.get(key), str) or not result[key].strip():
                    errors.append(f'{identifier}: pass requires {key}')
            for key, length in (('source_sha', 40), ('artifact_sha256', 64), ('fixture_sha256', 64)):
                if not re.fullmatch('[0-9a-f]{' + str(length) + '}', result.get(key, '')):
                    errors.append(f'{identifier}: pass requires valid {key}')
            evidence = result.get('evidence')
            if not isinstance(evidence, list) or not evidence or not all(isinstance(e, str) and e.strip() for e in evidence):
                errors.append(f'{identifier}: pass requires evidence references')
            if result.get('differences') != []:
                errors.append(f'{identifier}: pass requires no unresolved differences')
        if candidate is not None:
            if status != 'pass' or result.get('source_sha') != candidate or result.get('artifact_sha256') != artifact_hash:
                errors.append(f'{identifier}: not passed on the fixed candidate/artifact')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'accept'])
    parser.add_argument('--cases', type=Path, default=ROOT / 'docs/verification/cases.json')
    parser.add_argument('--candidate')
    parser.add_argument('--artifact', type=Path)
    args = parser.parse_args()
    digest = None
    if args.action == 'accept':
        if not re.fullmatch(r'[0-9a-f]{40}', args.candidate or '') or not args.artifact:
            parser.error('accept requires --candidate FULL_SHA and --artifact PATH')
        digest = hashlib.sha256(args.artifact.read_bytes()).hexdigest()
    data = json.loads(args.cases.read_text(encoding='utf-8'))
    errors = validate(data, candidate=args.candidate if args.action == 'accept' else None, artifact_hash=digest)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    counts = {status: sum(c['result']['status'] == status for c in data['cases']) for status in sorted(STATUSES)}
    print(json.dumps(counts))
    if args.action == 'validate':
        print('Case structure validated. Pending/blocked/fail are not GUI acceptance.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
