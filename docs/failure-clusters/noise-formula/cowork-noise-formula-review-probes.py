"""Independent native noise checks and immutable source verification; no script execution."""
from pathlib import Path
import hashlib
import json
import os
import sys
import zipfile

ROOT = Path(os.environ.get('GRADER_REPO_ROOT', '/private/tmp/cowork-fix-noise-formula'))
sys.path.insert(0, str(ROOT / 'tests/graders'))
from noise_formula_support import Harness

h = Harness()
notice = 'Работа Robot Learning with Affordances в обзор не включена.'
checks = [
 ('plain notice', notice, True),
 ('article notice', notice.replace('Работа', 'Статья'), True),
 ('notice without fullstop', notice.rstrip('.'), True),
 ('prior unrelated sentence', 'Обзор посвящён LLM. ' + notice, True),
 ('prior unrelated multiline sentence', 'Обзор посвящён LLM.\n' + notice, True),
 ('trailing newline', notice + '\n', True),
 ('same paragraph positive first', 'Robot Learning with Affordances: результаты. ' + notice, False),
 ('multiline positive first', 'Robot Learning with Affordances: результаты.\n' + notice, False),
 ('multiline positive after', notice + '\nRobot Learning with Affordances: результаты.', False),
 ('semicolon positive clause', notice.rstrip('.') + '; Robot Learning with Affordances: результаты.', False),
 ('negated exclusion', 'Нельзя сказать, что ' + notice.lower(), False),
 ('double negative', notice.replace('не включена', 'не может быть не включена'), False),
 ('quoted notice', '«' + notice + '»', False),
 ('embedded assertion', 'Автор заявил: ' + notice, False),
 ('different paper name', notice.replace('Affordances', 'Affordances II'), False),
 ('ID separately retained', '2309.16349: метод. ' + notice, False),
 ('multiline clause contradiction', notice.rstrip('.') + '\nно её результаты включены.', False),
]
for label, text, expected in checks:
 actual = h.noise(replace=text)
 assert actual == expected, (label, expected, actual)
 print('PASS', label, 'accepted' if actual else 'rejected')
assert not h.noise(replace=notice, table=True)
print('PASS notice plus positive table rejected')
for other in ('teamly', 'gsheet'):
 assert not h.noise(replace=notice, other={other:'2309.16349'})
 print('PASS notice plus', other, 'ID rejected')
print('20 independent native controls passed')
provenance = json.loads((ROOT / 'docs/failure-clusters/noise-formula/provenance.json').read_text())
archive = Path(os.environ.get('COWORK_SOURCE_ARCHIVE','/Users/glebmikheev/prj/ouroboros-bank-backend/artifacts/evals/cowork-full496-20261003/raw-runs.zip'))
with zipfile.ZipFile(archive) as z:
 for case, item in provenance.items():
  source = item['source']; raw = z.read(source['member'])
  fixture = ROOT / 'tests/graders/fixtures/remaining-language' / source['fixture']
  assert hashlib.sha256(raw).hexdigest() == source['sha256']
  assert raw == fixture.read_bytes()
  baseline = z.read(item['baseline_eval_member'])
  assert hashlib.sha256(baseline).hexdigest() == item['baseline_eval_sha256']
  assert baseline == (ROOT / 'docs/failure-clusters/noise-formula' / (case+'-baseline.json')).read_bytes()
  print('verified original source, fixture, baseline bytes and SHA256:', case)
