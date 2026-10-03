"""Run the current native test suite against pristine d943e75 grader sources."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

root = Path(os.environ.get('GRADER_REPO_ROOT', '/private/tmp/cowork-fix-identifier-normalization'))
cases = ['arxiv-research-tracker-teamly', 'pw-insales-coupon-effectiveness-gsheet-email', 'sf-hr-attrition-forecast-excel-word-gcal', 'terminal-canvas-gsheet-word-teamly-gcal', 'yt-fireship-scholarly-excel-teamly']
with tempfile.TemporaryDirectory(prefix='identifier-independent-baseline-') as directory:
    for case in cases:
        relative = f'tasks/finalpool/{case}/evaluation/main.py'
        target = Path(directory) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(['git', 'show', 'd943e75:' + relative], cwd=root))
        if case == 'sf-hr-attrition-forecast-excel-word-gcal':
            shutil.copytree(root / f'tasks/finalpool/{case}/groundtruth_workspace', target.parents[1] / 'groundtruth_workspace')
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests/identifier_normalization', '-v'], cwd=root, env={**os.environ, 'GRADER_REPO_ROOT': directory})
    raise SystemExit(result.returncode)
