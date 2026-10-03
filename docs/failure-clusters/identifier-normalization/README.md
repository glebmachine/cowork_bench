# Identifier normalization: five independent root-cause analyses

Status for **every case: ожидает проверки**. Local component regressions are green;
independent review passed after resolving the conflicting-column finding; complete case replay has not happened. No task text,
groundtruth, runtime, or acceptance thresholds changed. No model calls, pushes, or upstream writes were performed.

Base: upstream `d943e75`; worktree branch `fix/identifier-normalization`.
Allowed publication target, only after review: `glebmachine/cowork_bench`.
The worktree shares the inspection repository's existing upstream remote; no
remote operation was used. Do not push to its inherited origin.

## Reproduction and evidence boundaries

`provenance.json` records the exact immutable `raw-runs.zip` member and SHA256 of
each original XLSX and `eval_res.json`. The adjacent `*-baseline.json` files are
byte-for-byte baseline grading evidence. Regression fixtures are all sheet cell
values decoded from those original XLSX files using openpyxl `data_only=True`;
they are not edited agent answers or synthesized groundtruth. Dates serialize as
strings; formatting/formula evaluation is outside these cell-comparison tests.

Command from this branch (read-only existing venv, no dependency sync):

```sh
PYTHONPATH=/private/tmp/cowork-timezone-test-deps \
 /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python \
 -m unittest discover -s tests/identifier_normalization -v
```

Set `GRADER_REPO_ROOT=/private/tmp/cowork_bench-inspect` to run exactly the same
fixture/test code against pristine native graders. Initial `red.log`: 15 tests,
5 expected failures (each archived spelling), canonical and wrong-value controls
all successful. After the five minimal fixes, the **same 15 tests** pass
(`green.log`). Expanded suite: pristine 21 tests / 7 failures
(`expanded-red.log`), patched **21/21 pass** (`expanded-green.log`). The extra two
RED tests expose the policy field alias and prefixed-ID citation lookup.
`git diff --check` passes. These are actual native checker calls, not copied
normalization implementations or assertions against source text.

Tests assert individual recorded checks. They do not manufacture full-case PASS:
Teamly/calendar/Word are not replayed. Coupon DB calls explicitly fail offline;
Canvas uses a fixed analytics reference to isolate recognition of a mean header
and its numeric comparison. Canvas's unrelated pass-rate/count failures against
that synthetic reference are test-scope artifacts, not new diagnoses of agent
output. Full recorded component results are in `component-results.json`.

## arxiv-research-tracker-teamly

- **Symptom / layer:** baseline critical paper-set mismatch plus five missing-ID
  reports; grader representation handling, not demonstrated missing research.
- **Mechanism:** pristine `evaluation/main.py:202` reads the raw Paper_ID string
  and compares to bare identifiers; `:257` separately uses the same raw string
  for citation lookup. Actual saved cells are `arXiv:2402.1000x`; bare suffixes
  are precisely the five expected papers. The task requires a Paper_ID column,
  but does not mandate bare IDs or forbid the standard `arXiv:` label.
- **Artifact:** see `provenance.json` entry and `arxiv-...-baseline.json`; fixtures
  preserve the original five IDs, titles, counts and ordering.
- **Controlled proof:** `test_arxiv_archived_alias` RED; changing only the five
  IDs to bare form makes `test_arxiv_canonical` pass. Replacing one with a genuinely
  different `arXiv:2402.99999` remains rejected. This rules out wrong paper identity
  as the explanation for the reproduced set failure.
- **Fix:** patched `evaluation/main.py:142,210,265` strips only a leading standard
  arXiv label and whitespace at both identity lookup sites. No numeric ID rewrite,
  version collapse or fuzzy matching. Prefixed IDs now still trigger per-paper
  citation checks; a deliberately wrong count is rejected.
- **GREEN / residual:** all native workbook checks pass on the archived cells.
  Live Teamly and whole-case decision were not rerun; baseline's page success is
  historical evidence, not a fresh full-case PASS. Status: **ожидает проверки**.

## pw-insales-coupon-effectiveness-gsheet-email

- **Symptom / layer:** baseline critical category join, external benchmark values,
  and computed gap checks all report zero recognized data; grader header lookup.
- **Mechanism:** `evaluation/main.py:38` alias table does not recognize
  `Product_Category`, `Internal_Product_Count`, `Internal_Avg_Price`, or
  `Benchmark_Market_Avg_Price`. Native row dictionaries therefore have no canonical
  category/internal/external keys. All six benchmark category rows are present;
  task.md describes the column meanings and does not prescribe these header names.
- **Artifact:** provenance entry hashes original `Coupon_Effectiveness_Report.xlsx`
  and baseline grader report. All source cell values, including the extra two
  categories without external benchmarks, remain unchanged in the fixture.
- **Controlled proof:** original headers RED; renaming only those four headers
  to existing canonical names GREEN. A wrong category remains rejected; a wildly
  wrong benchmark price with the new aliases intact also remains rejected.
  Thus missing join/output data does not explain the original reproduced failures.
- **Fix:** patched alias entries at `evaluation/main.py:39,47,53,66`; numerical
  tolerances, category identities, gap formula and thresholds are untouched.
- **GREEN / residual:** three critical workbook value checks pass. The workbook
  still lacks `Total_Sales`, a separate noncritical requirement of the grader not
  explicit in task.md; this patch does not remove it or assert its validity.
  Our workbook-only fixture omits the existing agent script, and external email /
  Sheets are deliberately disabled; their test failures cannot be counted as real
  new agent defects. Full live case was not rerun. Status: **ожидает проверки**.

## sf-hr-attrition-forecast-excel-word-gcal

- **Symptom / layer:** seven baseline critical Top_Factor mismatches, one per
  department; grader's unpublished value vocabulary.
- **Mechanism:** pristine `evaluation/main.py:205` compares `Job Satisfaction`
  literally to groundtruth `satisfaction`. Task.md requires English technical
  identifiers but lists no Top_Factor enum. `initial_workspace/guide.md` lists
  no enum either. PDF §2.2 names job satisfaction and explicitly uses the source
  field `JOB_SATISFACTION`; it does not specify the shorter literal `satisfaction`.
- **Artifact:** archived workbook SHA and baseline evaluation SHA in provenance;
  original seven factor cells and scores retained. Groundtruth workbook is loaded
  directly from the unchanged repository by the native checker.
- **Controlled proof:** original labels RED; changing only factor labels to
  `satisfaction` GREEN. `performance` and `Not Job Satisfaction` fail, so this
  does not accept a different factor or generic substring.
- **Fix:** dedicated normalization at patched `evaluation/main.py:60,213` maps
  exactly `job satisfaction` and `job_satisfaction` to `satisfaction`; no global
  string normalization of Department or Risk_Level was introduced.
- **GREEN / residual:** all native workbook checks pass; the policy-field alias
  also has a positive regression. This isolates the literal mismatch and rules
  out scoring/budget discrepancies within this checker. Word and calendar are not
  revalidated; no full-case PASS claim. Status: **ожидает проверки**.

## terminal-canvas-gsheet-word-teamly-gcal

- **Symptom / layer:** baseline's only critical failure says averages differ from
  live Canvas; actual failing layer is grader header recognition.
- **Mechanism:** `evaluation/main.py:157` searches headers only for average / avg /
  сред. The archived report has `mean_score` with 80.26 and 79.08. Missing index
  sets avg_ok=False before any numeric comparison. Task.md asks for the mean
  semantically, without fixing an English header token.
- **Artifact:** original workbook and evaluation hashes in provenance. Existing
  analysis additionally identifies the source agent script's statistics.mean call;
  we do not treat that alone as proof that all live source rows were selected.
- **Controlled proof:** against an explicitly fixed two-course analytics reference,
  the actual mean header fails, a header-only change to `average_score` passes,
  and a numeric zero fails under either spelling. This rules out arithmetic as
  the cause of this isolated rejection, but does **not** independently prove that
  80.26/79.08 match a live database snapshot.
- **Fix:** patched `evaluation/main.py:158-160` accepts exact `mean` / `mean_score`
  only when existing lookup finds no column. No broad substring or tolerance change.
- **GREEN / residual:** target average check passes. Other workbook semantic checks
  are not asserted against the deliberately synthetic counts/pass rates; their
  failures are documented in component-results. Live Canvas and the remaining
  services must be replayed before a full-case conclusion. Status: **ожидает проверки**.

## yt-fireship-scholarly-excel-teamly

- **Symptom / layer:** baseline critical eight-title/order check fails with all
  eight videos present; grader character representation handling.
- **Mechanism:** pristine `evaluation/main.py:101,189-193` lowercases/strips and
  compares static ASCII `Microsoft's` to archived `Microsoft’s` (U+2019), rejecting
  the seventh row before any different-video evidence. User asks for source titles,
  not an ASCII punctuation transformation. Original source trace was already
  identified in the classification as returning U+2019.
- **Artifact:** original workbook and eval SHA in provenance; original title cells
  and row order are preserved in the fixture.
- **Controlled proof:** original titles RED; replacing curly apostrophes only with
  ASCII GREEN. A different Microsoft video is rejected; swapping first two titles
  remains rejected even with the curly-apostrophe spelling otherwise intact.
- **Fix:** dedicated title-only normalizer at patched `evaluation/main.py:105,194,197`
  maps U+2019 to ASCII apostrophe. No arbitrary punctuation removal, fuzzy title
  similarity, order relaxation, or global header/ID normalization.
- **GREEN / residual:** all native workbook checks pass. The existing grader still
  uses title substrings instead of stable video IDs; hardening that independent
  preexisting design is outside this patch. Teamly not replayed, therefore full
  case remains **ожидает проверки**.

## Independent-review finding and correction: coupon alias collision

The first independent review (agent `review_harness_and_graders`) found a real
false positive introduced by alias expansion. A report with canonical
`Market_Avg_Price=999999` followed by an equivalent alias column containing the
correct benchmark value lost the wrong canonical value when the row dictionary
was constructed. The three critical data checks then passed. The reviewer proved
that this same conflicting workbook failed pristine upstream. This is a grader
collision defect, not a newly discovered defect in the original archived answer.

Regression evidence is retained in `review-red.log`: **26 tests, 3 failures**
against the first patch. Those failures cover wrong canonical price before the
correct alias, wrong alias price before the correct canonical column, and a wrong
canonical category before the correct alias. A wrong last price column already
failed; the test retains that control. Equal duplicate columns remain accepted.

The corrected native row reader now accumulates duplicate-key conflicts before
building an accepted data row. Conflicting rows are excluded from downstream
category/value checks and any such conflict triggers a **critical** recorded
failure, even if enough other rows would pass the existing thresholds. Duplicate
columns are allowed only when each row's parsed Excel cell values compare equal;
there is no fuzzy, string-to-number, blank-filling, or precedence rule. For example,
a blank versus a populated value or numeric `74.15` versus string `"74.15"` is a
conflict. This policy applies symmetrically regardless of header order and also
to duplicate canonical headers.

`review-green.log`: the same **26/26 tests pass** after this correction.
`git diff --check` is clean. The initial 15/21-test logs remain historical evidence
of the initial patch, not evidence that the review finding was already covered.
This correction awaits renewed independent review. All original cases remain
**ожидает проверки**, with the whole-case replay limitations above unchanged.

## Final independent review

The frozen final 26-test suite passed independently. All five source workbooks and baseline grading reports were verified against the archive and their full cell projections checked. The initial conflicting-column false PASS was reproduced and corrected; the exact exploit now fails. See `cowork-identifier-normalization-independent-review.md` and adjacent immutable review logs. Whole-case status remains **ожидает проверки**.
