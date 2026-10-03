# grader-artifact-extraction — seven original FAILs

Branch `fix/grader-artifact-extraction`, baseline `d943e75bc0fc8e3b27141979300cd8cbcd1e890d`.
Prepared for independent review; not published. Any eventual PR targets only
`glebmachine/cowork_bench`. Original **381/496** score, artifacts and verdicts stay
unchanged. This is an offline corrected-grader experiment, not a new agent run.

## Evidence and scope

The source is `cowork-full496-20261003/analysis.json`, SHA256
`dc190ddcb5b75a96e5dcdd2fe77c0f8245b03b78d9a96283c07187f125ef02b5`, with artifacts
from its `raw-runs.zip`. The original trial is `20261003T125520Z-489ea28e` for
course enrollment and `20261003T135408Z-f7c9cc18` for the other six cases.
Fixture provenance and SHA256 values are in
`tests/regression/fixtures/artifact_extraction/provenance.json`.

| Case | Reproduced defect / minimal boundary corrected | Remaining scope |
|---|---|---|
| course-enrollment-analytics-dashboard | Full course names retain semesters for sheet, Teamly and email matching; different semesters no longer overwrite each other. Parameterized noise-email query no longer treats literal percentages as binding placeholders. | Existing numeric tolerances and coverage thresholds are unchanged. Archived performance rows are used as comparison inputs only to reproduce the identity defect; not a fresh authoritative LMS measurement. |
| insales-refund-root-cause-excel-word-email | Word extraction walks paragraphs in document XML, including table and nested-table paragraphs, preserving adjacent text runs. | Existing section/product predicates unchanged; no requirement to repeat tables as prose. |
| playwright-canvas-curriculum-word-teamly | Read Markdown/HTML table rows and named Overall_Status/Follow_Up_Date cells; the final row no longer absorbs the following summary, and unrelated compliance columns cannot replace Overall_Status. | Department-source conflict and email grouping remain independent failures. No department rule changed. |
| pw-teamly-forms-survey-excel-word | Match exact metric names/explicit aliases so Avg_Gap_Pct cannot overwrite Avg_Gap. | Arithmetic direction of recommendations is a separate agent-content problem. |
| terminal-arxiv-scholarly-teamly-word-excel | Explicit Paper_ID is authoritative; otherwise match bounded title anchors or an unambiguous ID. Adam Roberts no longer makes a T5 page match BERT. | Frozen output still fails the six Source=Both requirement; search overlap and BERT category contracts are not changed. |
| terminal-kulinar-scholarly-excel-word-forms | Resolve a named menus list before interpreting a day-keyed object; share the extraction between structural and semantic checks. Require five entries; empty lunches do not pass the unresolved-category fallback. | Dietary compliance/calorie claims remain outside this extraction repair. |
| terminal-moex-sf-gsheet-word-gcal | Prefer employee-record collections over market_rows; match exact normalized money fields instead of bonus_percentage; retain source EMPLOYEE_ID and salary. | Full native calendar/Word/sheet grading was not rerun. Existing market-factor and budget tolerances are retained. |

## Identity decision

The bonus task specifies name-sorted round-robin assignment but no tie-break for
equal names. Imposing ID order would invent a new requirement. Instead, the
source calculation retains unique employee IDs and the multiset of region slots
occupied by each equal-name group. The checker accepts permutations within that
group, consumes each slot once, and computes the bonus from the matched source
salary and region tier. An ID-less output is accepted only when name plus salary
identifies one source employee. Duplicate/unknown identities, missing employees,
wrong salaries, regions and bonus amounts fail. The old three-match spot check
could conceal name collisions; the corrected identity check covers all source
employees. Current JSON field spellings with spaces or underscores remain valid.

## RED → fix → GREEN

`tests/regression/test_artifact_extraction.py` executes the actual evaluator
functions (and the survey evaluator entrypoint), replacing only database IO with
captured/synthetic rows. XLSX/DOCX fixtures are unmodified saved artifacts;
Teamly bodies and course sheet rows are extracted verbatim from tool calls.
Original grader imports are loaded via AST with only `import psycopg2` replaced
by the injected connection seam. It is not a reimplementation of the predicates.
The SQL-placeholder regression validates binding syntax at that seam, not a live
psycopg2/PostgreSQL integration test.

- Baseline: **11 methods, 13 failures, one SQL binding error** with the original
  seven grader files restored under a separate `COWORK_GRADER_ROOT`.
- Fixed: **11 methods pass**, no skips. Logs are in
  `evidence/grader-artifact-extraction/{baseline-red,fixed-green}.txt`.
- Controls include wrong/missing DOCX products; nested tables; wrong/missing
  semester identities; wrong Overall_Status despite other correct cells;
  missing course and wrong follow-up date; Markdown and HTML tables; reordered,
  absent and wrong Avg_Gap; missing T5 and contradictory Paper_ID; wrapper/list/
  day-map menus, duplicate lunch categories and missing days/lunches; bonus
  list/key collisions, wrong/missing/duplicate/unknown employee identities,
  wrong salary/region/bonus, equivalent tied-name permutations, individual cap
  violations and total-cap violations.

The separate archived-bonus replay injects `sales_employees.csv` and
`region_revenue.csv` captured in the original workspace as source-query rows.
The unchanged current/adjusted JSON files contain 7232 employees; real
`check_json_outputs` and `critical_checks` now pass, with matched 7232/7232 and
adjusted total 29,999,997.57 under cap 30,000,000. Its log is
`evidence/grader-artifact-extraction/archived-bonus-replay.txt`. This diagnostic
establishes extraction and arithmetic consistency against captured inputs; it
is not a fresh live source query or a full task PASS.

## Reproduce

Python 3.12 with `openpyxl` and `python-docx` is sufficient; no database, model,
network, agent mutation or fixture rewriting is required:

```sh
python -m unittest discover -s tests/regression -p test_artifact_extraction.py
```

To reproduce RED, extract the seven `evaluation/main.py` files from `d943e75`
into a separate tree retaining `tasks/finalpool/<case>/evaluation/main.py`, then:

```sh
COWORK_GRADER_ROOT=/path/to/baseline-tree python -m unittest discover -s tests/regression -p test_artifact_extraction.py
```

`git diff --check`, Python compilation of touched files, and Ruff F checks on the
new test module also pass. No claim is made that all seven entire tasks now pass;
independent content/contract failures remain visible. No prompts, groundtruth,
preprocess fixtures or source data are changed. Independent review is pending.

## Independent review follow-up

Review of 65a3ab6 found two incomplete negative boundaries: bold markup around
Paper_ID could bypass explicit-field authority, and menu lists checked record
count without proving distinct weekday identities. Neither finding changes task
text or the immutable baseline score.

Added two actual-grader regression methods before changing production graders.
The suite then produced 16 failing subtests across 13 methods against 65a3ab6;
`evidence/grader-artifact-extraction/review-controls-red.txt` preserves that RED.
Paper controls pair four ordinary label spellings with correct, contradictory,
malformed and empty IDs. Menu controls exercise wrapped/list/map shapes with
valid/shuffled order, duplicate/missing weekdays, and shuffled rows whose actual
consecutive weekdays share a lunch category.

The paper parser removes ordinary bold/code label markup and treats an explicit
malformed/empty ID as invalid instead of falling back to title inference. Menu
extraction validates exactly Monday-Friday with unique identities and returns
weekday order before adjacency checks; weekday-keyed maps also reject a
contradictory embedded day label. Correct shuffled rows remain accepted.

The unchanged 13-method suite passes after the fix, including earlier wrong,
missing-content and duplicate-identity controls. GREEN is preserved in
`evidence/grader-artifact-extraction/review-controls-green.txt`. This follow-up
still requires independent re-review and has not been published. It establishes
component boundaries only, not seven full native task PASS results.
