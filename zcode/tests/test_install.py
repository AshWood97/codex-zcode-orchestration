import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('zcode_install', Path(__file__).resolve().parents[1] / 'scripts/install.py')
install = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install)
MODEL = 'example-provider/gemini-3.8-flash-high'


class InstallTests(unittest.TestCase):
    def test_dry_run_does_not_create_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve() / 'new-home'
            result = install.configure(home, MODEL)
            self.assertEqual(len(result['changed_files']), 8)
            self.assertFalse(home.exists())

    def test_install_preserves_guidance_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            original = b'\xef\xbb\xbfPersonal rule\r\n'
            (home / 'AGENTS.md').write_bytes(original)
            install.configure(home, MODEL, apply=True)
            self.assertTrue((home / 'AGENTS.md').read_bytes().startswith(original))
            self.assertEqual(len(list((home / 'agents').glob('*.md'))), 7)
            for p in (home / 'agents').glob('*.md'):
                text = p.read_text(encoding='utf-8')
                self.assertIn('model: "' + MODEL + '"', text)
                self.assertIn('thoughtLevel: high', text)
                self.assertNotIn('__ZCODE_MODEL_ID__', text)
            self.assertEqual(install.configure(home, MODEL, apply=True)['changed_files'], [])

    def test_modified_role_requires_explicit_replacement_and_is_backed_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            install.configure(home, MODEL, apply=True)
            role = home / 'agents/code-reviewer.md'
            role.write_bytes(b'My customized reviewer\n')
            result = install.configure(home, MODEL)
            self.assertEqual(result['conflicting_roles'], [str(role)])
            with self.assertRaises(ValueError):
                install.configure(home, MODEL, apply=True)
            self.assertEqual(role.read_bytes(), b'My customized reviewer\n')
            result = install.configure(home, MODEL, apply=True, replace_existing=True)
            backup = Path(result['backup'])
            records = json.loads((backup / 'manifest.json').read_text())
            record = next(r for r in records if r['path'] == str(role))
            self.assertEqual((backup / record['backup']).read_bytes(), b'My customized reviewer\n')

    def test_marked_update_preserves_prefix_and_suffix(self):
        old = b'prefix\r\n' + install.START + b'\nold\n' + install.END + b'\r\nsuffix'
        updated = install.merge_guidance(old, b'new guidance')
        self.assertTrue(updated.startswith(b'prefix\r\n'))
        self.assertTrue(updated.endswith(b'\r\nsuffix'))
        self.assertEqual(updated.count(install.START), 1)
        self.assertNotIn(b'\nold\n', updated)

    def test_malformed_markers_fail_before_role_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            (home / 'AGENTS.md').write_bytes(install.START)
            with self.assertRaises(ValueError):
                install.configure(home, MODEL, apply=True)
            self.assertFalse((home / 'agents').exists())

    def test_invalid_model_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve() / 'home'
            for value in ('', 'model-only', 'provider/model\ninject: true', 'provider/"model'):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    install.configure(home, value, apply=True)
            self.assertFalse(home.exists())

    def test_partial_write_failure_restores_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            (home / 'agents').mkdir()
            first = home / 'agents/code-reviewer.md'
            first.write_bytes(b'original')
            real_write = install.atomic_write
            def write(path, data, mode=0o600):
                if path == home / 'agents/test-verifier.md':
                    raise OSError('simulated write failure')
                return real_write(path, data, mode)
            with patch.object(install, 'atomic_write', side_effect=write), self.assertRaises(OSError):
                install.configure(home, MODEL, apply=True, replace_existing=True)
            self.assertEqual(first.read_bytes(), b'original')
            self.assertFalse((home / 'AGENTS.md').exists())


if __name__ == '__main__':
    unittest.main()
