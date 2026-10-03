# grader-sheet-structure — optional headers and column identity

MR proposal, **not published**. Target: user's fork `glebmachine/cowork_bench`,
branch `fix/grader-sheet-structure`, base `d943e75bc0fc8e3b27141979300cd8cbcd1e890d`.

Eight baseline FAILs belong to this primary cluster. A format assumption caused
critical grading failures even when the requested metric or table was present.
The fix reads optional Summary headers, maps Equity Metrics by semantic column
names, uses the documented Review Schedule column positions, and locates the
Curriculum_Coverage header after an optional title. Numerical checks remain;
missing fields, duplicate metric/course/group keys and contradictory values fail.

## Hypotheses and tests, in order

1. **First Summary row is data, not a mandatory header.** Confirmed in six task
   instructions: they specify metric rows but do not require `Metric/Value`.
   Actual six XLSX files start with a required metric. Existing `[1:]` loses it.
   Test headered/headerless workbooks against each real evaluator loader; then
   invoke four complete DB-free `main()` functions. All four original saved
   workbooks changed from exit 1 to exit 0 under the corrected evaluator.
2. **An additional salary column changes the meaning of fixed offsets.** Confirmed
   in compensation equity: agent columns `Highest Avg Salary` and `Lowest Avg Salary`
   precede `Pay Gap %`, `Equity Ratio`, `Equity Status`. Task fixes semantics, not
   column order. Test actual `check_excel` with frozen GT-derived fixture and inserted
   columns, reordered required fields, and explicit semantic header aliases.
   Original saved workbook passes every Excel critical check after the patch.
3. **A title line is mistaken for Curriculum_Coverage's table header.** Confirmed:
   title, blank line, real header, four course rows. Test real `critical_checks`
   and assert C3 independently, because other checks need DB/PPT files. Require
   exact course IDs 1–4 and `total = assignments + quizzes`; don't accept an
   arbitrary pair of numbers summing to a third. Original saved C3 now passes.
4. **Review Schedule reads columns one position too far right.** Confirmed against
   task's Course/Topic/Date/Time/Room and actual XLSX. Test real `check_excel` with
   synthetic query results, weekday versus weekend/date/time negative controls.
   Only Date/Time offsets change, not expected dates or tolerances.

## Case index and remaining scope

| Case | Confirmed defect | Verification / remaining issue |
|---|---|---|
| canvas-exam-prep-scheduler | Summary header; Date/Time offsets | Real loader + check_excel regression; independent calendar score textual rounding issue remains outside this patch |
| canvas-grade-summary | Summary header | Saved workbook full grader FAIL → PASS |
| canvas-quiz-report | Summary header | Saved workbook full grader FAIL → PASS |
| canvas-ta-workload-excel-email | Summary header | Real loader, first Total_Courses preserved; Teamly/email unchanged |
| sf-hr-compensation-equity-excel-word-forms | Positional equity columns | Saved workbook full check_excel critical checks pass |
| sf-hr-manager-report | Summary header | Saved workbook full grader FAIL → PASS |
| sf-hr-salary-growth | Summary header | Saved workbook full grader FAIL → PASS |
| terminal-canvas-sf-excel-ppt-gcal | Title mistaken for header | Saved workbook C3 passes; timezone belongs to separate branch; actual quiz count discrepancy not adjudicated here |

## Reproduction

Python with `openpyxl` and `python-pptx` installed:

```sh
python -m unittest discover -s tests/graders -p test_sheet_structure.py
```

11 unittest methods, multiple parameterized subcases; no model, network or database.
The test-only psycopg2 import substitute rejects every connection attempt. It does
not fabricate successful DB evidence. Existing repository GT files seed fixtures;
no observed answer constants were introduced in the graders.

Before fix: 32 failing subcases and six IndexErrors (a one-metric Summary was
entirely discarded). After fix: all 11 methods pass. Logs in
`evidence/grader-sheet-structure/{baseline-red,fixed-green}.txt`.
Negative controls cover incorrect metric values, absent metrics/required columns,
duplicate metric/group/course keys, duplicate required headers, wrong totals and
wrong schedule dates/times. Four complete grader entrypoints check verdicts, not
just parser outputs.

Baseline evidence: immutable full496 artifact package `cowork-full496-20261003`,
analysis SHA256 `dc190ddcb5b75a96e5dcdd2fe77c0f8245b03b78d9a96283c07187f125ef02b5`.
Source case attempts are indexed in the parent failure-cluster index and the
package's `analysis.json`/`raw-runs.zip`. Local evidence replay logs:
`/private/tmp/sheet-artifact-replay.log`, `/private/tmp/sheet-full-artifact-replay.log`.

**Original 381/496 score, all verdicts and artifacts remain unchanged.** These
are corrected-grader regressions, not a newly measured full benchmark or a claim
that all eight tasks now pass every independent check. Task text, groundtruth,
agent/runtime and data seeds are unchanged. Evaluators remain standalone because
execution packages individual task directories; Summary normalization is local to
those six evaluators rather than a new cross-task runtime dependency.
