"""Exercise installed hooks in disposable repositories, including partial staging."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class HookTest(unittest.TestCase):
    def test_real_commit_guard_packaging_partial_staging_and_push_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
            env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
            def run(*args, ok=True, input=None):
                result = subprocess.run(args, cwd=root, env=env, input=input, capture_output=True, text=True)
                if ok:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                return result
            run('git', 'init', '-q', '-b', 'main')
            run('git', 'config', 'user.name', 'Harness test')
            run('git', 'config', 'user.email', 'test@example.invalid')
            run('git', 'config', 'core.autocrlf', 'false')
            for directory in ['scripts', '.githooks']:
                shutil.copytree(ROOT / directory, root / directory, ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copyfile(ROOT / 'build-vlt.py', root / 'build-vlt.py')
            (root / '.gitignore').write_text('__pycache__/\n')
            (root / 'src').mkdir()
            xml = root / 'src/theme.xml'
            xml.write_text('<Theme version="2.0"/>')
            run(sys.executable, 'scripts/bootstrap.py')
            run('git', 'add', '.')
            denied = run('git', 'commit', '-qm', 'must reject main', ok=False)
            self.assertIn('Issue branch', denied.stderr)
            run('git', 'switch', '-c', 'codex/12-sample')
            run('git', 'commit', '-qm', 'package')
            self.assertTrue((root / 'My-MinimalX-JPMod.vlt').is_file())
            self.assertIn('My-MinimalX-JPMod.vlt', run('git', 'ls-files').stdout)
            self.assertEqual(run('git', 'status', '--porcelain').stdout, '')
            package = root / 'My-MinimalX-JPMod.vlt'
            good = package.read_bytes()
            for damage in ['corrupt', 'stale', 'extra', 'missing']:
                with self.subTest(package=damage):
                    if damage == 'corrupt':
                        package.write_bytes(b'not a ZIP')
                    elif damage == 'missing':
                        package.unlink()
                    else:
                        with zipfile.ZipFile(package, 'w') as archive:
                            archive.writestr('theme.xml', b'stale' if damage == 'stale' else xml.read_bytes())
                            if damage == 'extra':
                                archive.writestr('extra.txt', b'tampered')
                    run('git', 'add', '--', package.name)
                    # Even a good working file must not hide the broken index blob.
                    package.write_bytes(good)
                    denied = run('git', 'commit', '-qm', 'reject broken package only', ok=False)
                    self.assertTrue(any(message in denied.stderr for message in
                                        ['Cannot read package', 'Archive content mismatch',
                                         'Archive entries do not match', 'Candidate must track']), denied.stderr)
                    run('git', 'restore', '--staged', '--', package.name)
            with zipfile.ZipFile(package, 'a') as archive:
                archive.comment = b'content-equivalent package'
            shipped = package.read_bytes()
            run('git', 'add', '--', package.name)
            run('git', 'commit', '-qm', 'accept content-equivalent package only')
            self.assertEqual(package.read_bytes(), shipped)
            xml.write_text('<Theme version="2.0"><ThemeInfo name="staged"/></Theme>')
            run('git', 'add', 'src')
            xml.write_text('<Theme version="2.0"><ThemeInfo name="unstaged"/></Theme>')
            denied = run('git', 'commit', '-qm', 'reject mixed source', ok=False)
            self.assertIn('Unstaged skin/build', denied.stderr)
            remote = root / 'remote.git'
            run('git', 'init', '--bare', '-q', str(remote))
            denied = run('git', 'push', str(remote), 'HEAD:refs/heads/main', ok=False)
            self.assertIn('Direct push/deletion', denied.stderr)


if __name__ == '__main__':
    unittest.main()
