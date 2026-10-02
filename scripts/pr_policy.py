#!/usr/bin/env python3
"""Check PR routing and case tracking. Never grants independent-review approval."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from git_guard import BRANCH
from verification import validate
import promotion

TOOLING_FILES = {'AGENTS.md', 'CLAUDE.md', 'README.md', '.gitignore', '.gitattributes',
                 'build-vlt.py', 'build-vlt.sh', 'install-hooks.sh'}
TOOLING_DIRS = ('docs/', 'scripts/', 'tests/', '.github/', '.githooks/', 'githooks/',
                '.agents/', '.claude/', '.cursor/rules/', 'prompts/', 'examples/')


def fields(body):
    result = {}
    for line in body.splitlines():
        match = re.fullmatch(r'(Issue|Integration|Verification|GUI|GUI reason):\s*(.+)', line.strip())
        if match:
            if match[1] in result:
                raise ValueError('Duplicate PR field: ' + match[1])
            result[match[1]] = match[2].strip()
    if set(result) != {'Issue', 'Integration', 'Verification', 'GUI', 'GUI reason'}:
        raise ValueError('PR requires Issue, Integration, Verification, GUI and GUI reason fields')
    return result


def validate_pr(pr, paths, cases, promotion_check=None):
    meta = fields(pr.get('body') or '')
    match = BRANCH.fullmatch(pr['head']['ref'])
    if not match or meta['Issue'] != '#' + match[2]:
        raise ValueError('Branch and Issue field must use the same real Issue number')
    if meta['Verification'] != 'docs/verification/cases.json':
        raise ValueError('Use the canonical case registry')
    errors = validate(cases)
    if errors:
        raise ValueError('\n'.join(errors))
    target = pr['base']['ref']
    integration = meta['Integration']
    if meta['GUI'] not in {'required', 'not-required'}:
        raise ValueError('GUI must be required or not-required')
    product = any(p.startswith('src/') or p.endswith('.vlt') for p in paths)
    if product and meta['GUI'] != 'required':
        raise ValueError('Skin/artifact changes require GUI verification')
    if target == 'develop':
        if integration != 'implementation':
            raise ValueError('develop accepts implementation PRs')
        if re.search(r'(?i)\b(close[sd]?|fix(?:es|ed)?|resolve[sd]?)\s+#\d+', pr.get('body') or ''):
            raise ValueError('Use Refs in develop PRs; transfer QA before closing the implementation Issue')
    elif target == 'main' and integration == 'tooling':
        if meta['GUI'] != 'not-required' or not paths or any(p not in TOOLING_FILES and not p.startswith(TOOLING_DIRS) for p in paths):
            raise ValueError('main tooling must contain only tooling paths and an explicit GUI-not-required reason')
    elif target == 'main' and integration == 'promotion':
        if meta['GUI'] != 'required' or promotion_check is None:
            raise ValueError('Promotion requires a fixed-candidate check and GUI acceptance')
        promotion_check()
    else:
        raise ValueError('Invalid target/integration combination')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event', type=Path, required=True)
    args = parser.parse_args()
    event = json.loads(args.event.read_text(encoding='utf-8'))
    pr = event['pull_request']
    base, head = pr['base']['sha'], pr['head']['sha']
    for sha in (base, head):
        if not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError('Invalid revision')
    paths = subprocess.check_output(['git', 'diff', '--name-only', '--no-renames', '-z', base + '...' + head]).decode('utf-8').split('\0')
    cases = json.loads(subprocess.check_output(['git', 'show', head + ':docs/verification/cases.json']).decode('utf-8'))
    def check_promotion():
        record = promotion.read_json(Path.cwd(), head, promotion.MANIFEST_PATH)
        live_base = subprocess.check_output(['git', 'rev-parse', 'origin/main']).decode().strip()
        if base != live_base:
            raise ValueError('main advanced; refresh the base and independent review')
        develop = subprocess.check_output(['git', 'rev-parse', 'origin/develop']).decode().strip()
        promotion.verify(Path.cwd(), head=head, base=base, cases=cases,
                         candidate_record=record, develop=develop)
    validate_pr(pr, list(filter(None, paths)), cases, check_promotion)
    print('PR routing and case structure passed. Live Issue ownership and independent review require readback.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
