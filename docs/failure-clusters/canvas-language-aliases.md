# Canvas course, module and summary label aliases

Base `d943e75`; branch `fix/canvas-language-aliases`, user's fork only. No task.md,
source dataset, groundtruth, initial workspace or baseline result was changed.
Offline grader regressions; no model calls, live DB updates or full native run.

## Three confirmed boundaries

| Original FAIL | Cause and correction | Independent failures / limits |
|---|---|---|
| canvas-grade-equity-excel-word-gcal | Calendar title contains original Russian «Биохимия и биоинформатика», but the grader recognizes only English aliases. Calendar matching now accepts bounded Russian/English course terms. | Existing week and duration predicates unchanged; wrong course, wrong date, wrong duration and missing review phrase still fail. Noncritical course mention uses the same aliases. |
| canvas-module-completion-teamly-gcal | Source Canvas names are Russian; archived Teamly table uses names explicitly provided in the task. Alias dictionary was indexed by English keys only. Normalize both source/output names to the same alias identity. | Counts must come from the named Item_Count cell of a unique module row. The previous same-line regex would let “2 Files” rescue Item_Count=999 once aliases work. Markdown and HTML table rows are supported; duplicate/missing module rows and wrong cells fail. Calendar timezone is not changed. |
| canvas-scholarly-curriculum-review | Task requires Metric/Value headers but not English row labels; archived “Общее количество курсов”=23 was ignored. Match explicit normalized RU/EN total-course labels. | Existing total range, sum and rate tolerances are unchanged. Faculty totals cannot masquerade as course totals; ambiguous duplicate total-course metrics fail. Other summary-language heuristics are outside this fix. |

Fixtures contain exact archived calendar/page/write arguments and an unmodified
saved Curriculum_Review.xlsx. Module comparison inputs come from the recorded
`canvas_list_modules` response (actual item-array lengths 15,2,1,1,1), not an
invented fixed expected count in production. Provenance records source trace,
line SHA256 and fixture hashes. The regression tests verify fixture hashes.

The module case has a separate timezone caveat: recorded canvas_get_course at
trace4 gives `time_zone=Europe/London`. It is not established that calendar
scheduling must use that course setting; the task itself does not say which
zone governs. Recorded calendar events use Europe/Moscow while grader checks raw
DB hours. This branch does not settle that contract or claim full case PASS.

## RED → GREEN

9 unittest methods, **11 baseline assertion failures**; same9 methods GREEN with
these three graders. Logs are tracked under `evidence/canvas-language/`.
Tests invoke actual `check_calendar`, `check_teamly` and `check_excel` functions;
only DB reads and check recording are injected. XLSX is read by openpyxl.

Controls include RU/EN in both directions, original archived outputs, wrong
course/date/duration/review, course-term suffix collisions, missing/duplicate
modules, Week10 vs Week1, unrelated count numbers, reordered named columns,
HTML tables, wrong total/sum/rate, faculty decoy and duplicate total metrics.

```sh
python -m unittest discover -s tests/regression -p test_canvas_language.py
COWORK_GRADER_ROOT=/path/to/clean/d943e75/checkout \
  python -m unittest discover -s tests/regression -p test_canvas_language.py
```

Dependencies: Python3.12, openpyxl. No psycopg2/DB needed because the connection
seam is injected. Local verified interpreter:
`/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python`.
New tests pass Ruff F checks; changed graders compile; `git diff --check` passes.
No complete native task evaluation or updated benchmark pass rate is claimed.

## Proposed PR description

Three graders rejected valid Russian/English labels in saved Canvas outputs.
Normalize the supported course/module/metric aliases without changing task text.
Read module counts from their actual table cells so unrelated numbers cannot
produce false positives. Archived output regressions and paired negative controls
pass; original benchmark results remain unchanged. Independent review pending.

## Independent review follow-up

Review found that any HTML table suppressed a valid Markdown tracker. Two new actual-grader subtests failed before changing `parser.rows or markdown_rows` to combine both representations. Eleven methods now pass, including a contradictory HTML count alongside Markdown, which remains FAIL. Independent re-review is clean; report /private/tmp/cowork-canvas-language-independent-review.md. Historical source artifacts remain unchanged.
