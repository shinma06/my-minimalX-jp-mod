import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import promotion
from validate_skin import builder

ROOT = Path(__file__).resolve().parents[1]


class PromotionTest(unittest.TestCase):
    def test_only_observed_legacy_base_uses_complete_initial_case_set(self):
        self.assertEqual(promotion.base_case_ids('.', promotion.LEGACY_BASE),
                         {f'UI-{i:03}' for i in range(1, 11)})
        with patch.object(promotion, 'read_json', side_effect=ValueError('missing registry')):
            with self.assertRaisesRegex(ValueError, 'missing registry'):
                promotion.base_case_ids('.', 'a' * 40)

    def test_fixed_candidate_all_cases_and_post_freeze_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
            env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
            def git(*args):
                return subprocess.check_output(['git', '-C', str(root), *args], env=env).decode().strip()
            git('init', '-q')
            git('config', 'user.name', 'Harness test')
            git('config', 'user.email', 'test@example.invalid')
            (root / 'src').mkdir()
            (root / 'src/theme.xml').write_text('<Theme version="2.0"/>')
            cases = json.loads((ROOT / promotion.CASE_PATH).read_text(encoding='utf-8'))
            (root / promotion.CASE_PATH).parent.mkdir(parents=True)
            (root / promotion.CASE_PATH).write_text(json.dumps(cases), encoding='utf-8')
            git('add', '.')
            git('commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD')
            (root / 'src/theme.xml').write_text('<Theme version="2.0"><ThemeInfo name="test"/></Theme>')
            git('add', '.')
            git('commit', '-qm', 'candidate')
            candidate = git('rev-parse', 'HEAD')
            record = promotion.manifest(root, candidate, base)
            package = builder().build_vlt(source_dir=root / 'src', output_dir=root / 'dist')
            self.assertEqual(record['artifact_sha256'], hashlib.sha256(package.read_bytes()).hexdigest())
            for case in cases['cases']:
                case['result'] = dict(status='pass', owner='test-only', next_action='review',
                    observed_at='2026-10-02T00:00:00+09:00', reference_version='test', vlc_version='test',
                    environment='test fixture', source_sha=candidate, artifact_sha256=record['artifact_sha256'],
                    fixture_sha256='c' * 64, evidence=['synthetic-test-only'], differences=[])
            (root / promotion.CASE_PATH).write_text(json.dumps(cases), encoding='utf-8')
            (root / promotion.MANIFEST_PATH).write_text(json.dumps(record), encoding='utf-8')
            git('add', 'docs')
            git('commit', '-qm', 'observations')
            head = git('rev-parse', 'HEAD')
            def verify(data=cases, rec=record, revision=head):
                promotion.verify(root, head=revision, base=base, cases=data, candidate_record=rec, develop=candidate)
            verify()
            bad = copy.deepcopy(cases)
            bad['cases'][0]['result']['status'] = 'pending'
            with self.assertRaises(ValueError): verify(bad)
            bad = copy.deepcopy(cases)
            bad['cases'].pop()
            with self.assertRaises(ValueError): verify(bad)
            with self.assertRaises(ValueError): verify(rec=dict(record, artifact_sha256='d' * 64))
            (root / 'src/theme.xml').write_text('<Theme version="2.0"><ThemeInfo name="changed"/></Theme>')
            git('add', 'src')
            git('commit', '-qm', 'changed after freeze')
            with self.assertRaises(ValueError): verify(revision=git('rev-parse', 'HEAD'))


if __name__ == '__main__':
    unittest.main()
