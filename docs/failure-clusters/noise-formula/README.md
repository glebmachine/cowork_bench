# Two remaining grader-language errors: separate RCA and disposition

Base `d943e75bc0fc8e3b27141979300cd8cbcd1e890d`, branch
`fix/noise-formula-grading`, worktree `/private/tmp/cowork-fix-noise-formula`.
Only the arxiv noise grader is patched. Formula grader, tasks, groundtruth, agent
runtime and original outputs are unchanged. No model calls, DB access, execution
of the archived agent script, commit, or publication occurred.

Source fixtures were copied from the earlier RED-only research checkout, then
independently byte-compared with the original immutable `raw-runs.zip` members.
`provenance.json` records each original artifact and baseline evaluation SHA256.
The `*-baseline.json` files are exact archived reports. Fixture hashes also have
an automated regression. No full-case PASS is inferred from these component tests.

## arxiv-latex-review-teamly-word — ожидает проверки

**Symptom and layer.** Baseline reports robotics noise inclusion despite an
explicit exclusion notice in the saved Word introduction. Grader text semantics,
not demonstrated agent inclusion of a robotics research section.

**Original mechanism.** `evaluation/main.py:130-131` collected all Word paragraph
text. `:253-256` joined Word, Teamly and Sheet text and rejected every occurrence
of `affordance`, `robot learning`, or `2309.16349`. Thus this original sentence
necessarily failed: “Работа Robot Learning with Affordances, относящаяся к
робототехнике, в обзор не включена.” Its artifact SHA256 is
`c980291ce0f144fb4fb574d557267231c586e0b73f36fe9f1d3f7c925b6f97d6`.

**Contract.** Task paragraph 1 asks to skip unrelated robotics/physical-systems
papers rather than include them in the research knowledge base. It does not forbid
stating what was excluded. The remaining task asks for sections and registry rows
for relevant papers only. An exclusion notice is not such a research section/row.

**Controlled proof.** Original DOCX against native `check_word` and
`check_noise_exclusion`: RED. Removing the entire noise-bearing introduction
paragraph is a valid no-mention control and passes pristine grading. Adding a
positive robotics section remains rejected. Expanded tests reject positive
mentions in Teamly or Sheets despite a Word exclusion; explicit double negation;
a negated assertion (“Неверно, что…”); conflicting clauses; a positive sentence
followed by an exclusion; and a positive Word table record. The last test also
revealed the original grader ignored table content entirely.

**Change.** Patched `evaluation/main.py:113-123,144` computes a separate Word noise
evidence string. It recognizes only a complete final sentence using the explicit
Russian `работа/статья ... в обзор не включена` construction, optionally carrying
the observed robotics-relative clause. It removes that sentence only, not other
mentions of the title. It includes raw table cells as positive evidence. The
original document text remains intact for all other checks. Teamly/Sheet text is
not exempted; an exclusion in one deliverable never clears another's inclusion.

This is deliberately a narrow grammar, not general negation inference: unrecognized
paraphrases, quoted/embedded claims, other languages and unresolved constructions
still fail conservatively. It is not a blanket title whitelist or a claim to solve
arbitrary discourse, irony, or cross-sentence contradictions.

**Result and alternatives.** `noise-red.log`: 7 test methods, 2 failures (the valid
exclusion and ignored table record). Exactly the same tests against the candidate:
7/7 pass (`noise-green.log`). Thus the mechanism is isolated from missing papers,
authors, or registry data. Other document checks still execute, but live Teamly /
Sheets and the complete task decision were not replayed. Existing baseline
successes are historical evidence only. Independent review passed: seven main tests and twenty additional native controls,
with exact scripts and logs preserved here. Case status remains **ожидает проверки**.

## terminal-insales-pdf-excel-word-gform — confirmed mechanism, NOT FIXED

**Symptom and layer.** Native script check rejects the saved, arithmetically correct
formula because its local average variable is named `avg`. Grader lexical contract.
Artifact SHA256:
`bb3d06aee25a567fb1e02a403180936b5908ffaf4c10a151b2c97c5c1f3689a0`.

**Precise cause.** `evaluation/main.py:354-358` lowercases source and requires the
substring `avg_rating` or `avg rating`, plus another substring for the low-rating
penalty. Archived `quality_audit.py:65-70` derives average/low-review percentage
from category review statistics, then assigns
`qscore = round((avg / 5.0) * 100 - 2 * pct, 2)` and appends it to the scorecard.
The task specifies the mathematical metrics/formula, not mandatory local names.
The saved calculation contains neither mandatory average substring, so it fails
before any semantic examination of arithmetic or output use.

**RED and controls.** The inherited five methods reproduced six failed assertions
(`inherited-red.log`). Formula research now separately retains the correct archived
script's false rejection and seven negative witnesses: comment-only; string-only;
addition instead of subtraction; penalty coefficient 3; metric roles reversed;
formula inside `if False`; unused formula followed by zero output. (The first
positive plus seven negative witnesses produce eight failed assertions.) No
archived script is run: the native checker reads a temporary text copy only.
`formula-unresolved-red.log` intentionally stays RED. This research file is named
`research_formula.py`, separate from the passing noise regression discovery.

`formula-numeric-counterexamples.json` provides independent arithmetic witnesses,
computed directly from fixed numbers, not by executing script text: average 3 and
low-review percentage 10 gives the required score 40, versus 80 for addition, 30
for coefficient 3, 194 for reversed metric roles, and 0 for constant output. Extra
points distinguish coincidental equality. These demonstrate why simply allowing
arbitrary variable names or finding a similar-shaped expression is not enough.

**Rejected implementation direction.** A nonexecuting linear AST matcher could
ignore comments and literals and enforce coefficients 20 and -2, but without
semantic role binding it also accepts `(pct / 5) * 100 - 2 * avg`. Scanning any AST
subtree also accepts dead code or an unused decoy. Existing workbook arithmetic
checks compare row-internal values; they do not establish which source expression
produced them or whether the script actually ran. That is an unresolved boundary,
not permission to weaken the critical check.

**Future proposal, not an implemented fix.** A constrained dataflow proof must bind
rating and low-review-percentage inputs to semantic roles, follow aliases and
assignments into the emitted scorecard, and reject unsupported/ambiguous control
flow. Alternatively, use an explicitly sandboxed replay with controlled inputs
and an output oracle after defining acceptable dependencies and isolation; never
execute arbitrary submitted code on the grader host. Either approach needs tests
for role reversal, dead/unused expressions and overwritten outputs before adoption.
No safe complete implementation is claimed here, and this case is **not fixed**.

## Exact commands and logs

From the candidate worktree:

```sh
# Native noise RED on pristine graders (exit 1, two failures).
GRADER_REPO_ROOT=/private/tmp/cowork_bench-inspect \
 /Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python \
 -m unittest discover -s tests/graders -p test_noise_exclusion.py -v

# Candidate noise GREEN (exit 0, seven methods).
/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python \
 -m unittest discover -s tests/graders -p test_noise_exclusion.py -v

# Intentionally unresolved formula research (exit 1).
/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python \
 tests/graders/research_formula.py -v

git diff --check
```

All outputs are retained beside this file. Initial combined inherited/expanded
logs predate the separation of passing regressions and unresolved research, and
are historical evidence only. psycopg2 import is stubbed by the harness; no service
is contacted, and no dependencies were installed or synchronized.

## Independent review completed

See `cowork-noise-formula-independent-review.md` and the executable probe script. Source artifacts and baseline reports were independently verified byte-for-byte against the immutable archive. Noise candidate: 7/7 main tests and20 additional controls pass. Formula research: 3 methods/8 expected assertions still fail and no formula production change is included. No full-case PASS is claimed.
