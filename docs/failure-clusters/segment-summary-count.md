# Bind the segment count to the target-achievement statement

Base d943e75; branch `fix/segment-summary-count` in the user's fork. No task.md,
source data, agent prompt or original result changes; no live model/DB calls.

The saved DOCX explicitly says “Количество сегментов, выполнивших или
перевыполнивших свои планы: 0.” The old checker only recognized a zero before
“segments”, rejecting this correct reversed order. Its unbounded English zero
pattern also accepted “10 segments met their targets”, and did not distinguish
“0 segments missed their targets” from the requested achievement count.

The replacement reads explicit RU/EN target-achievement count statements with
numbers before or after the description, plus the Russian “ни один ... не
выполнил” form. Wrong counts, opposite predicates, unrelated zeroes and conflicting
recognized achievement counts fail. Existing table checks, total-target/actual
checks and DB-derived `n_meeting == 0` requirement remain unchanged.

## Evidence and TDD

The original `Q4_Segment_Report.docx` is copied byte-for-byte from immutable
raw-runs.zip. `tests/regression/fixtures/segment_summary/provenance.json` records
its original member and SHA256, checked by a test.

4 test methods: **7 baseline assertion failures → 4 methods GREEN**, including
seven accepted layouts and eight negative summaries. Actual `check_word_doc`
reads the real DOCX; check-recording and the DB aggregate argument are injected.
The test's injected aggregates come from the saved table to isolate text parsing,
so their agreement with the table is not independent source-data verification.
The original complete Word check now passes on this diagnostic input; no fresh
whole-task PASS or changed benchmark score is claimed.

```sh
python -m unittest discover -s tests/regression -p test_segment_summary.py
COWORK_GRADER_ROOT=/path/to/clean/d943e75/checkout \
  python -m unittest discover -s tests/regression -p test_segment_summary.py
```

Dependencies: Python3.12 and python-docx. Actual verified local Python is
`/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python`.
Logs: `evidence/segment-summary/{baseline-red,fixed-green}.txt`.
Changed grader compiles; new tests pass Ruff F; git diff --check passes.

## Limits / proposed PR text

A valid count after the Russian target-achievement description was rejected;
unrelated zeroes and a suffix of10 could also pass. Bind numeric counts to the
recognized achievement predicate in either ordering. Archived DOCX and paired
negative controls cover the change. This is a bounded multilingual parser, not a
general proof of arbitrary prose semantics; unrecognized paraphrases still fail.
Independent review pending. No optional cleanup or publication performed.
