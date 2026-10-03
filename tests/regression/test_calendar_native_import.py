import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(os.environ.get('COWORK_GRADER_ROOT', Path(__file__).resolve().parents[2]))


class NativeEvaluationImportTests(unittest.TestCase):
    def test_native_module_entrypoint_imports_shared_helper_from_repository_cwd(self):
        env = dict(os.environ)
        env['PYTHONPATH'] = os.environ.get('COWORK_TEST_DEPENDENCY_PATH', '')
        result = subprocess.run([sys.executable, '-m', 'tasks.finalpool.canvas-late-submission-word-gcal.evaluation.main', '--help'], cwd=ROOT, env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--agent_workspace', result.stdout)
