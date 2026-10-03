# Calendar comparisons: local UTC expectation fix

Status: locally implemented and independently reviewed; root handles any subsequent user-authorized fork commit/push. No upstream push or PR publication was performed by this implementation.
Base upstream `0717376/cowork_bench` main/HEAD: `d943e75bc0fc8e3b27141979300cd8cbcd1e890d`,
confirmed read-only on 2026-10-03. Branch: `fix/calendar-grader-timezone-contract`.
This fixes the calendar component of twenty graders, not twenty complete tasks or model runs.

## Root cause and comparison authority

PostgreSQL stores `timestamptz` as an instant. Its session timezone changes the aware datetime
returned by psycopg2, SQL `DATE`/`EXTRACT`, and implicit conversion of unzoned SQL literals.
The affected graders compared returned hours or date strings directly with their existing
UTC clock/date expectations. The same stored instant could incorrectly fail, while a wrong
instant could incorrectly pass, depending on the DB session zone.

The user selected UTC as the comparison authority for this scoped benchmark fix. The event's
submitted `start_timezone`/`end_timezone` is descriptive data, not authority for what the
expected clock means. Example: Canvas expects 10:00Z. An event at 13:00+03:00 is the same instant
and passes; an event at 10:00+03:00 is 07:00Z and fails. Tests cover all three required Canvas
events together, not just a standalone conversion function.

Shared `utils/evaluation/calendar_time.py` explicitly converts aware datetime cells with
`astimezone(UTC)` before the existing grader compares dates, hours and durations. Naive cells
raise rather than inheriting the host timezone. Remaining SQL date/weekday operations use
`AT TIME ZONE 'UTC'`, and range cutoffs use explicitly zoned `TIMESTAMPTZ` literals. Sessions
are not changed by the implementation. Other cells and stored original zones are preserved.

All twenty existing predicates, thresholds, tolerances and required dates/hours are unchanged.
Positive controls preserve the existing +/-1-hour and +/-1-day tolerances where present.
The Canvas duration predicate permits up to three hours despite its '(1h each)' label. An
initial new three-hour negative test was wrong; independent review caught it. The negative
fixture now uses four hours, without tightening that pre-existing grader criterion.

## Bounded scope and separate defects

The twenty case IDs are pinned in `tests/regression/calendar_timezone_cases.json` and listed
in the per-case evidence table below. Static inventory found 150 graders reading gcal.events,
101 wall-time/date-pattern candidates, and 17 with some explicit conversion. This change does
not claim to repair all calendar tasks. An explicit America/New_York task and existing
Moscow-specific graders remain untouched. The helper is UTC-only; it is not a general
local-zone duration API (same-zone DST subtraction has different semantics).

The event store already retains `timestamptz` plus start/end zone names. The calendar adapter
returns UTC ISO instants plus original zones. Root separately identified invalid/missing-zone
naive fallback and patch-without-zone behavior in the adapter. Those storage/ingress issues
are not changed here. No task.md, source dataset, groundtruth, agent prompt or adapter file
is modified. Earlier prototypes that rewrote twenty task statements or tightened tolerances
were rejected and are not part of this candidate.

## Synthetic and archived evidence

The bulk matrix uses minimal synthetic task-compatible calendar events, inserted through real
PostgreSQL with `+03:00` spellings and original Europe/Moscow zone columns. Actual checker
functions read them using psycopg2 under UTC, Europe/Moscow and America/New_York sessions.
Equivalent +14/-12 spellings, shifted instants, wrong dates, durations and overlaps provide
controls. Scholarly's valid 15:00Z events additionally run under Pacific/Kiritimati, exposing
its date failure without inventing a different required event time.

DST fold/spring boundaries are conversion controls. An actual launch-relative arxiv checker
runs a fall-DST date pair, while reverse-validation SQL checks exercise UTC-midnight versus
New York's prior date. Those reverse checks are component checks, not complete valid tasks.

Two archived diagnostic runs contribute exact event arguments for moex-options-expiry-monitor
and moex-portfolio-ppt-gcal. Their original trace/member-line SHA256 and task SHA256 are retained
in `calendar_archived_moscow_events.json`; projection identity is pinned separately in
`calendar_archived_moscow_provenance.json`. All seven selected event argument objects and line
hashes were checked against the original trace files, and both full trace hashes matched.
These source runs used the UTC benchmark profile configuration. Both recorded task SHA256
values were independently compared with pristine upstream d943e75 and match exactly; their
task text was not edited. They remain diagnostic run observations, not whole-case success claims.

Both archived wrong-agent outputs remain FAIL under UTC/Moscow/New York. Tests assert the
specific reason: options start at 06:00Z instead of 09:00Z; portfolio reports
`parts(summary,time,loc)=(True, False, True)`. Their failure cannot be credited to unrelated
content or location checks. No shifted instant is accepted merely because its timezone is Moscow.

## Native execution and reproducibility

Native `Evaluation.build` launches `python -m tasks.finalpool.<case>.evaluation.main` from
repository cwd. A subprocess smoke test verifies helper import without a repository PYTHONPATH.
More substantially, six native Canvas subprocess executions run the actual full evaluator,
with real PostgreSQL and equivalent/shifted Moscow events under all three session zones.
Calendar verdict text must match. Overall child exit remains 1 because the deliberately
calendar-only fixture has no Word/email artifacts; this is explicitly not a whole-case PASS.

Dependencies: Python 3.10+, psycopg, psycopg2-binary, openpyxl, python-pptx, python-docx.
Use an empty disposable DB owned by the test user. The native Canvas evaluator hardcodes
benchmark fixture role `eigent` / `camel`; provision that role with CONNECT on this isolated DB.
The suite creates gcal.events exclusively (refuses an existing table), grants that role only
schema usage/table SELECT, and drops its owned table after the run. No source DB is used.

```sh
# Pristine checkout d943e75 for the RED replay; same tests, unchanged real graders.
COWORK_GRADER_ROOT=/path/to/pristine-d943e75 \
COWORK_TEST_PG_DSN=postgresql://testuser:testpassword@127.0.0.1:5434/isolated_tests \
COWORK_TIMEZONE_MATRIX=/private/tmp/calendar-red-matrix.json \
python -m unittest discover -s tests/regression -p test_calendar_real_graders.py

# Candidate GREEN, including helper and native subprocess checks.
COWORK_TEST_PG_DSN=postgresql://testuser:testpassword@127.0.0.1:5434/isolated_tests \
COWORK_TIMEZONE_MATRIX=/private/tmp/calendar-green-matrix.json \
python -m unittest discover -s tests/regression -p 'test_calendar*.py'
```

Verified local interpreter: `/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python`.
Its missing psycopg2 dependency is supplied from `/private/tmp/cowork-timezone-test-deps` via
PYTHONPATH and COWORK_TEST_DEPENDENCY_PATH (for child processes), never a repository path.
Original environment packages were not edited. Author DB: cowork_upstream_timezone_tests;
independent reviewer uses a separate DB to avoid overlapping fixture ownership.

## Verification record

Detailed original logs remain `/private/tmp/cowork-upstream-timezone-final-{red,green}.log`;
matrices use the same prefix with `-matrix.json`. Durable copies, per-case/per-zone counts,
and before/after source/task hashes are under `evidence/calendar-timezone-contract/` below.
No model calls, full-agent reruns or benchmark score update are claimed. Independent review completed before publication. The user subsequently authorized committing
and pushing this branch to their fork, glebmachine/cowork_bench; no upstream publication is included in this step.


Final author result: **503 tests pass** (496 actual PostgreSQL scenarios plus seven helper,
fixture-integrity and import checks), 5.070 seconds. Independent reviewer: **503 pass**,
5.107 seconds, with no blocking findings. Baseline actual-checker suite: **198 assertion
failures out of 496 scenarios**. The outcome matrix contains **197 verdict mismatches**:
171 false rejections and 26 false acceptances. The additional failed assertion checks
the exact normalized 06:00 timestamp in an archived negative whose boolean verdict was
already FAIL. Do not report all 198 as changed verdicts. Every one of the twenty graders has
at least one original RED. Candidate and independent matrices contain zero verdict mismatches.

- [Baseline log](evidence/calendar-timezone-contract/baseline-red.log)
- [Candidate log](evidence/calendar-timezone-contract/candidate-green.log)
- [Per-case/per-zone numerical matrix](evidence/calendar-timezone-contract/case-zone-summary.json)
- [Full baseline matrix](evidence/calendar-timezone-contract/baseline-matrix.json)
- [Full candidate matrix](evidence/calendar-timezone-contract/candidate-matrix.json)
- [Independent review](evidence/calendar-timezone-contract/independent-review.md)
- [Independent replay log](evidence/calendar-timezone-contract/independent-green.log)
- [Before/after source hashes and unchanged task hashes](evidence/calendar-timezone-contract/source-hashes.json)

| Case | Scenarios | Baseline false rejects | Baseline false accepts | Candidate mismatches |
|---|---:|---:|---:|---:|
| canvas-late-submission-word-gcal | 30 | 10 | 2 | 0 |
| canvas-quiz-remediation-forms-gcal | 21 | 8 | 1 | 0 |
| fetch-arxiv-conference-schedule-gcal-teamly | 21 | 8 | 1 | 0 |
| fetch-kulinar-catering-excel-gcal-email | 21 | 8 | 1 | 0 |
| fetch-sf-sales-forecast-ppt-gcal | 21 | 8 | 1 | 0 |
| insales-order-monthly-ppt-gcal | 21 | 8 | 1 | 0 |
| insales-product-bundle-excel-ppt-gcal | 21 | 8 | 1 | 0 |
| insales-product-review-analysis-gform-gcal | 30 | 12 | 2 | 0 |
| kulinar-weekly-gsheet-gcal | 21 | 8 | 1 | 0 |
| moex-options-expiry-monitor | 24 | 8 | 2 | 0 |
| moex-portfolio-ppt-gcal | 24 | 8 | 2 | 0 |
| scholarly-reading-group-gcal-gsheet-word | 28 | 4 | 0 | 0 |
| sf-sales-quarterly-review-gcal | 21 | 8 | 1 | 0 |
| sf-support-priority-gcal-excel | 21 | 8 | 1 | 0 |
| sf-support-resolution-word-gcal | 21 | 8 | 1 | 0 |
| teamly-forms-gcal-onboarding | 21 | 8 | 1 | 0 |
| terminal-arxiv-canvas-gsheet-word-gcal | 36 | 16 | 3 | 0 |
| terminal-insales-pw-pricing-excel-word-gcal | 27 | 9 | 1 | 0 |
| terminal-moex-canvas-excel-gcal-email | 30 | 10 | 1 | 0 |
| terminal-sf-scholarly-excel-ppt-gcal | 36 | 6 | 2 | 0 |
