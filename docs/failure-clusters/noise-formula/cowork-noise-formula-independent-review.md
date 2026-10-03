# Independent review: noise exclusion, unresolved formula research

2026-10-03. Candidate `/private/tmp/cowork-fix-noise-formula`, branch `fix/noise-formula-grading`, baseline `d943e75`. Reviewer did not author or edit candidate files. **No actionable finding in the scoped production diff.** This is component-level validation, not a whole-case PASS.

## Noise exclusion assessment

`tasks/finalpool/arxiv-latex-review-teamly-word/evaluation/main.py:113-123,144` replaces raw paragraph noise scanning with a separate evidence corpus. The narrowly anchored grammar removes only an explicit final sentence stating that the named robotics paper was excluded. The original document still feeds the other document checks. Other mentions in the same paragraph, another paragraph, table cells, Teamly and Sheets remain evidence against exclusion.

Task paragraph 1 requires omitting irrelevant robotics papers, and the document/registry instructions require sections and rows for relevant papers. It does not forbid explaining what was excluded. Therefore accepting the archived explicit notice is consistent with the task, while retaining positive content as a failure is necessary. The additional table scan closes a pre-existing blind spot. It does not excuse table records based on a nearby notice.

Independently executed original DOCX/native check_word/check_noise_exclusion regressions: candidate **7/7 PASS**, pristine **7 methods / 2 failures** (valid exclusion false rejection; table inclusion previously missed). Added 20 independent native controls, all passed: plain notices with работа/статья, punctuation and preceding unrelated sentence variants; mixed positive/negative mentions before and after the notice; multiline and semicolon clauses; explicit negation/double negation; quoted and embedded claims; distinct title suffix; separately retained arxiv ID; positive table cells; and IDs in other deliverables. These confirm occurrence-local removal rather than a global title whitelist.

Boundary: this intentionally recognizes a limited Russian sentence grammar. It is not a general natural-language exclusion classifier, nor proof against arbitrary pronoun references, cross-sentence contradictions or irony. Unknown forms may still false-reject conservatively. The journal explicitly identifies this limitation. No relaxation outside the observed class is asserted.

## Formula research assessment

`tasks/finalpool/terminal-insales-pdf-excel-word-gform/evaluation/main.py` is byte-unchanged relative to baseline. The separate `tests/graders/research_formula.py` is deliberately excluded from normal test discovery. Independently reran it: **3 methods / 8 failed assertions**, matching the unresolved false rejection plus lexical false-positive witnesses. The harness imports the native grader and lets it read temporary source text; it never executes the archived agent script.

The journal correctly says NOT FIXED and rejects a superficial AST-only solution without role binding, control-flow and output-use proof. No safe AST implementation or arithmetic/runtime correctness claim is present in the candidate. Research RED must remain distinguished from the passing noise suite.

## Source and scope verification

The independent probe opened original `raw-runs.zip` members and verified exact bytes and SHA256 for both archived source artifacts (DOCX and quality_audit.py), their copied fixtures, both baseline evaluation artifacts and the corresponding saved baseline JSON files. All matched. This strengthens the fixture-only hash test with direct original-archive comparison.

Tracked production diff contains exactly the one arxiv evaluation/main.py file. Task text, groundtruth, initial workspace, formula grader and agent/runtime are unchanged. `git diff --check` passes. This separate benchmark checkout does not change Ouroboros runtime invariants or governance files; no Ouroboros full gate is implied.

No live services, DB calls, model calls, commits or publication were performed. Full Teamly/Sheets/task grading was not rerun. Historical baseline component successes are not fresh end-to-end evidence.

## Exact reproducible commands and artifacts

Run from `/private/tmp/cowork-fix-noise-formula`:

```sh
/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python -m unittest discover -s tests/graders -p test_noise_exclusion.py -v
GRADER_REPO_ROOT=/private/tmp/cowork_bench-inspect /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python -m unittest discover -s tests/graders -p test_noise_exclusion.py -v
/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python tests/graders/research_formula.py -v
/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python /private/tmp/cowork-noise-formula-review-probes.py
```

The second and third commands intentionally exit 1. The first and fourth exit 0. The saved probe supports GRADER_REPO_ROOT and COWORK_SOURCE_ARCHIVE overrides and contains the exact 20 controls and archive verification actually executed.

Evidence files:

- `/private/tmp/cowork-noise-formula-independent-tests.log` — seven candidate tests.
- `/private/tmp/cowork-noise-formula-independent-baseline.log` — two expected pristine failures.
- `/private/tmp/cowork-noise-formula-independent-formula.log` — eight unresolved formula assertions.
- `/private/tmp/cowork-noise-formula-independent-probes.log` — twenty controls plus immutable provenance checks.
- `/private/tmp/cowork-noise-formula-review-probes.py` — executable proof, not just a test summary.
- `/private/tmp/cowork-noise-formula-independent-hashes.json` — SHA256 of 18 candidate source/test/evidence files and the independent probe script; pycache excluded.
