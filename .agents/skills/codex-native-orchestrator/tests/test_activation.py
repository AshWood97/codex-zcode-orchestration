import importlib.util
from pathlib import Path
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('native_activation', SKILL / 'scripts/install_activation.py')
activation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(activation)


class ActivationTests(unittest.TestCase):
    def make_home(self, root):
        home = root / 'custom codex home'
        skill = home / 'skills/codex-native-orchestrator'
        (skill / 'references').mkdir(parents=True)
        (skill / 'SKILL.md').write_text('Installed fixture', encoding='utf-8')
        (skill / 'references/activation.md').write_bytes((SKILL / 'references/activation.md').read_bytes())
        return home

    def test_check_does_not_write_and_apply_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            home = self.make_home(Path(temp))
            before = b'Personal guidance\r\nKeep this exact prefix.\r\n'
            (home / 'AGENTS.md').write_bytes(before)
            report = activation.configure(home)
            self.assertFalse(report['ultra_ready'])
            self.assertEqual((home / 'AGENTS.md').read_bytes(), before)
            report = activation.configure(home, apply=True)
            self.assertTrue(report['ultra_ready'])
            installed = (home / 'AGENTS.md').read_bytes()
            self.assertIn(str((home / 'skills/codex-native-orchestrator/SKILL.md').resolve()).replace('\\', '/').encode(), installed)
            self.assertEqual(installed.count(activation.START.encode()), 1)
            self.assertFalse(activation.configure(home, apply=True)['changed'])
            self.assertEqual((home / 'AGENTS.md').read_bytes(), installed)

    def test_marked_upgrade_preserves_unrelated_prefix_suffix_and_bom(self):
        prefix, suffix = b'\xef\xbb\xbfPersonal rule\r\n', b'\r\nKeep trailing guidance\r\n'
        old = prefix + activation.START.encode() + b'\nold entry\n' + activation.END.encode() + suffix
        block = activation.START + '\nnew entry\n' + activation.END
        updated = activation.merge_block(old, block)
        self.assertTrue(updated.startswith(prefix))
        self.assertTrue(updated.endswith(suffix))
        self.assertNotIn(b'old entry', updated)

    def test_malformed_or_duplicate_markers_stop_without_writing(self):
        for text in [activation.START, activation.END, activation.END + activation.START,
                     activation.START + activation.END + activation.START + activation.END]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                activation.merge_block(text.encode(), 'replacement')

    def test_missing_skill_cannot_install_a_dead_entrypoint(self):
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(ValueError):
            activation.configure(Path(temp), apply=True)


if __name__ == '__main__':
    unittest.main()
