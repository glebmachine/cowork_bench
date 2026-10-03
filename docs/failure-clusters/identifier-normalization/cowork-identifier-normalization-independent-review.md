# Independent review: identifier normalization

Reviewed 2026-10-03, baseline `d943e75`, frozen uncommitted branch `fix/identifier-normalization` in `/private/tmp/cowork-fix-identifier-normalization`. Reviewer did not author or edit the candidate. Final outcome: **no unresolved findings in the scoped diff**. This is a component-level review, not a full-case PASS certification.

## Finding discovered and resolved

**P2 — conflicting coupon aliases hid invalid canonical values.** The initial new mapping at `tasks/finalpool/pw-insales-coupon-effectiveness-gsheet-email/evaluation/main.py:66` fed the dictionary comprehension formerly at line 160. A workbook with canonical `Market_Avg_Price=999999` and later `Benchmark_Market_Avg_Price` containing correct values silently overwrote the invalid canonical value. Pristine grader rejected the market and gap checks; initial candidate passed both. This was independently reproduced, not inferred from code.

Author corrected the reader at final `evaluation/main.py:157-180`: conflicting normalized columns are excluded from input rows and cause an explicit critical failure. Five new regressions cover numeric collisions in either column order, category collisions, and equal duplicate values. My exact original adversarial workbook now fails the relevant checks. Finding closed. Original evidence: `/private/tmp/cowork-identifier-normalization-independent-probes.log`; final evidence: `/private/tmp/cowork-identifier-normalization-independent-final-probes.log`; reproducible script: `/private/tmp/cowork-identifier-review-probe.py`.

## Per-case assessment

- **arxiv-research-tracker-teamly** — `evaluation/main.py:142,210,265`: removing only a leading `arXiv:` label is consistent with task.md's Paper_ID contract, which does not require bare strings. Both paper-set and citation lookup paths normalize. Native negatives reject a different target, duplicate identity, version suffix, full-width digits and embedded prefix. Wrong citation values still fail. No version collapse or general Unicode normalization.
- **pw-insales-coupon-effectiveness-gsheet-email** — `evaluation/main.py:39,47,53,66,157`: four exact aliases express the task's semantic category/count/internal-price/market-price columns. Numeric comparisons and gap calculation remain intact. The discovered ambiguity is now rejected critically. Equal duplicate values pass; contradictory values cannot select a favorable representation by ordering columns.
- **sf-hr-attrition-forecast-excel-word-gcal** — `evaluation/main.py:60,213`: task and guide require English factor identifiers but specify no literal enum. Independently extracted PDF §2.2 explicitly uses JOB_SATISFACTION. Mapping precisely Job Satisfaction / JOB_SATISFACTION to satisfaction is justified. Department/Risk_Level and numerical checks are unchanged. Distinct factors, substrings and a Cyrillic homoglyph remain rejected.
- **terminal-canvas-gsheet-word-teamly-gcal** — `evaluation/main.py:158-160`: task requests mean submission scores without prescribing an English header token. Exact mean / mean_score aliases are valid. Native checker rejects zero values, median_score, meaning_score and mean_score_wrong. Tests use a fixed reference, so they establish header recognition and preserved numeric comparison only; they do not establish that archived 80.26/79.08 equal the live source snapshot.
- **yt-fireship-scholarly-excel-teamly** — `evaluation/main.py:105,194,197`: title-only U+2019→ASCII apostrophe normalization preserves the intended identity/order check for the recorded typography. Different titles and wrong order remain rejected. The pre-existing substring comparison remains a documented limitation; this review does not certify exact video identity against IDs or replay the source service.

## Independently executed verification

Command from candidate worktree:

```sh
PYTHONPATH=/private/tmp/cowork-timezone-test-deps \
 /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python \
 -m unittest discover -s tests/identifier_normalization -v
```

- Frozen final candidate: **26/26 PASS**, log `/private/tmp/cowork-identifier-normalization-independent-tests.log`.
- Same final tests against temporary native grader files read by `git show d943e75:...` plus unchanged HR groundtruth: **26 tests / 8 expected failures**, log `/private/tmp/cowork-identifier-normalization-independent-baseline.log`. One additional baseline failure relative to original 21-test suite is equal duplicate canonical/alias positive: original grader lacks other required aliases, so this is not a claim that baseline had collision protection.
- Original initial 21-test candidate suite independently passed before the conflict probe exposed missing coverage.
- Eleven additional adversarial native-checker controls passed, log `/private/tmp/cowork-identifier-normalization-independent-negatives.log`.
- For all five cases, independently opened the pinned archive member, checked XLSX SHA256, checked baseline eval SHA256, and compared **all sheets/all cell values** to the JSON fixtures using openpyxl data_only=True with temporal values serialized as strings. Every comparison passed. These are faithful cell projections, not evidence about preserved formatting/formula execution.
- `git diff --check` passes. Tracked diff contains exactly the five evaluation/main.py files. Task text, initial workspaces, groundtruth and runtime are unchanged.
- Reviewed-file SHA256 manifest: `/private/tmp/cowork-identifier-normalization-independent-hashes.json` (25 source/test/document/evidence files; excludes pycache).

## Evidence boundaries

No model calls, live DB/service replay, commits or publications were made by this reviewer. Coupon external calls intentionally fail offline; Canvas analytics are a fixed reference. Teamly/calendar/Word and full-case verdicts were not replayed. The per-case journal correctly separates these limits from the demonstrated representation bugs. Existing missing Total_Sales and title-substring behavior are outside this change, not silently declared fixed. Ouroboros runtime invariants and Coding Rules are not exercised by this separate benchmark-only checkout; no Ouroboros source or governance files were modified.

## Reproducible supplemental scripts

Saved and actually rerun after review, without candidate edits:

```sh
PYTHONPATH=/private/tmp/cowork-timezone-test-deps /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python /private/tmp/cowork-identifier-review-negatives.py
PYTHONPATH=/private/tmp/cowork-timezone-test-deps /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python /private/tmp/cowork-identifier-review-probe.py
PYTHONPATH=/private/tmp/cowork-timezone-test-deps /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python /private/tmp/cowork-identifier-review-baseline.py
```

`negatives.py` executes the eleven additional native-checker controls (11 passed). `probe.py` executes the exact conflicting-column workbook against candidate and pristine grader, then verifies all five archive XLSX/eval SHA256 pairs and all fixture cell projections (all verified; corrected candidate rejects). `baseline.py` runs the final 26-test suite against temporary pristine native sources (expected exit 1, eight failures). Logs named above were regenerated by these saved scripts. First/third scripts accept GRADER_REPO_ROOT for the candidate location; probe.py pins the reviewed checkout and original archive absolute paths explicitly. Baseline assertions intentionally fail: do not interpret exit 1 as a broken reproduction.
