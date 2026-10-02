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
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import validate_skin
from validate_skin import builder, validate_source, validate_package
from verification import validate
from pr_policy import validate_pr

ROOT = Path(__file__).resolve().parents[1]


class ProjectTest(unittest.TestCase):
    def test_package_name_content_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source'
            source.mkdir()
            xml = source / 'theme.xml'
            xml.write_text('<Theme version="2.0"/>', encoding='utf-8')
            (source / 'files').mkdir()
            for name in ['Z.txt', 'a.txt', 'Étiquette.txt', '音.txt']:
                (source / 'files' / name).write_text(name, encoding='utf-8')
            module = builder()
            first = module.build_vlt(source_dir=source, output_dir=Path(tmp) / 'issue-1')
            os.utime(xml, (1800000000, 1800000000))
            second = module.build_vlt(source_dir=source, output_dir=Path(tmp) / 'issue-2')
            self.assertEqual(first.name, 'VLC-WMP-Video.vlt')
            self.assertEqual(first.name, validate_skin.ARTIFACT_NAME)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertEqual(archive.namelist(),
                                 ['files/Z.txt', 'files/a.txt', 'files/Étiquette.txt', 'files/音.txt', 'theme.xml'])
            validate_package(source, first)
            with self.assertRaises(ValueError):
                module.build_vlt('../escape', source_dir=source, output_dir=tmp)
            with self.assertRaises(ValueError):
                module.build_vlt(source_dir=source, output_dir=source)

    def test_validation_checks_tracked_distribution_not_only_fresh_build(self):
        module = builder()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '-q', tmp], check=True)
            source = root / 'src'
            source.mkdir()
            (source / 'theme.xml').write_text('<Theme version="2.0"/>')
            package = module.build_vlt(source_dir=source, output_dir=root)
            good = package.read_bytes()
            subprocess.run(['git', '-C', tmp, 'add', package.name], check=True)
            with patch.object(validate_skin, 'ROOT', root), patch.object(validate_skin, 'builder', return_value=module):
                validate_skin.main()
                package.write_bytes(b'not a zip')
                with self.assertRaisesRegex(ValueError, 'Cannot read package'):
                    validate_skin.main()
                package.unlink()
                with self.assertRaisesRegex(ValueError, 'Cannot read package'):
                    validate_skin.main()
                package.write_bytes(good)
                (source / 'theme.xml').write_text('<Theme version="2.0"><ThemeInfo name="new"/></Theme>')
                with self.assertRaisesRegex(ValueError, 'Archive content mismatch'):
                    validate_skin.main()

    def test_missing_external_assets_and_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / 'theme.xml').write_text('<Theme version="2.0"><Font id="a" file="../font.ttf"/><Font id="a" file="missing.ttf"/></Theme>')
            errors = validate_source(source)
            self.assertEqual(len(errors), 3)

    def test_pending_cases_are_valid_but_never_accepted(self):
        data = json.loads((ROOT / 'docs/verification/cases.json').read_text(encoding='utf-8'))
        self.assertEqual(validate(data), [])
        self.assertTrue(validate(data, candidate='a' * 40, artifact_hash='b' * 64))
        fake = copy.deepcopy(data)
        fake['cases'][0]['result']['status'] = 'pass'
        self.assertTrue(validate(fake))

    def test_fixed_build_and_evidence_required(self):
        data = json.loads((ROOT / 'docs/verification/cases.json').read_text(encoding='utf-8'))
        data['cases'] = data['cases'][:1]
        data['cases'][0]['result'] = dict(status='pass', owner='test-session', next_action='review',
            observed_at='2026-10-02T00:00:00+09:00', reference_version='test', vlc_version='test',
            environment='test only', fixture_sha256='c' * 64, source_sha='a' * 40,
            artifact_sha256='b' * 64, evidence=['test-fixture-evidence'], differences=[])
        self.assertEqual(validate(data, candidate='a' * 40, artifact_hash='b' * 64), [])
        self.assertTrue(validate(data, candidate='d' * 40, artifact_hash='b' * 64))
        data['cases'][0]['result']['differences'] = ['wrong button']
        self.assertTrue(validate(data))

    def test_pr_routing_product_changes_and_early_issue_closure(self):
        data = json.loads((ROOT / 'docs/verification/cases.json').read_text(encoding='utf-8'))
        body = 'Issue: #12\nIntegration: implementation\nVerification: docs/verification/cases.json\nGUI: required\nGUI reason: playback\nRefs #12'
        pr = {'body': body, 'head': {'ref': 'codex/12-player'}, 'base': {'ref': 'develop'}}
        validate_pr(pr, ['src/theme.xml'], data)
        for bad in [dict(pr, body=body.replace('Refs', 'Closes')), dict(pr, body=body.replace('GUI: required', 'GUI: not-required'))]:
            with self.assertRaises(ValueError):
                validate_pr(bad, ['src/theme.xml'], data)
        pr['base']['ref'] = 'main'
        pr['body'] = body.replace('implementation', 'tooling').replace('GUI: required', 'GUI: not-required')
        validate_pr(pr, ['scripts/check.py'], data)
        with self.assertRaises(ValueError):
            validate_pr(pr, ['src/theme.xml'], data)
        pr['body'] = body.replace('implementation', 'promotion')
        with self.assertRaises(ValueError):
            validate_pr(pr, ['src/theme.xml'], data)


if __name__ == '__main__':
    unittest.main()
