"""Eleven additional native-checker controls; never modifies candidate source."""
import importlib.util
import os
from pathlib import Path

root = Path(os.environ.get('GRADER_REPO_ROOT', '/private/tmp/cowork-fix-identifier-normalization'))
spec = importlib.util.spec_from_file_location('native_tests', root / 'tests/identifier_normalization/test_native_checkers.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
checker = t.NativeCheckers()
for value in ['arXiv:2402.10003v2', 'arXiv:２４０２.１０００３', 'prefix arXiv:2402.10003', 'arXiv:2402.10001']:
    result = checker.evaluate('arxiv', lambda wb, v=value: setattr(wb['Paper Comparison'].cell(2, 1), 'value', v))
    assert not checker.relevant('arxiv', result), value
    print('reject distinct paper', value)
for value in ['job satisfaction score', 'dissatisfaction', 'Job-Satisfaction', 'satisfactiоn']:
    def mutate(wb):
        for row in wb['Top Risk Factors'].iter_rows(min_row=2):
            row[1].value = value
    assert not checker.relevant('hr', checker.evaluate('hr', mutate)), value
    print('reject distinct factor', value)
for value in ['median_score', 'meaning_score', 'mean_score_wrong']:
    def mutate(wb):
        wb['Course_Summary'].cell(1, 4).value = value
    assert not checker.relevant('canvas', checker.evaluate('canvas', mutate)), value
    print('reject distinct header', value)
print('11 additional adversarial native-checker controls passed')
