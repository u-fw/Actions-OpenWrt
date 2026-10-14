import pathlib
import subprocess
import sys
import tempfile
import unittest


class ConfigValidation(unittest.TestCase):
    def check_config(self, content, require_target=False):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / '.config'
            path.write_text(content)
            command = [sys.executable, str(pathlib.Path(__file__).with_name('validate-config.py')), str(path)]
            if require_target:
                command.append('--require-target')
            return subprocess.run(command, capture_output=True, text=True)

    def test_template_is_only_source_validation(self):
        result = self.check_config('# empty template\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('0 settings, 0 enabled target entries', result.stdout)
        self.assertIn('firmware build readiness is not verified', result.stdout)

    def test_build_rejects_template(self):
        result = self.check_config('# empty template\n', True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('no selected target', result.stderr)

    def test_build_accepts_selected_target(self):
        result = self.check_config('CONFIG_TARGET_x86=y\nCONFIG_PACKAGE_test=m\nCONFIG_NAME="test value"\n', True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('3 settings, 1 enabled target entries', result.stdout)

    def test_rejects_invalid_and_duplicate_settings(self):
        for content in ['invalid\n', 'CONFIG_TARGET_x86=y\nCONFIG_TARGET_x86=n\n']:
            with self.subTest(content=content):
                result = self.check_config(content)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('invalid or duplicate setting', result.stderr)


if __name__ == '__main__':
    unittest.main()
