# Secondary Teamly count grader correction

Component status: **ожидает проверки**. The actual agent case remains **анализ / исправление**: no agent behavior fix or full scenario rerun was performed.

Independent rereview is clean: 16/16 native-checker tests passed. Full scenario validation remains pending. The earlier nine-test result below is retained as historical proof, not the final test count.

Worktree: `/private/tmp/cowork-fix-teamly-count`; branch: `fix/teamly-count-validation`; pristine Cowork base: `d943e75bc0fc8e3b27141979300cd8cbcd1e890d`.

The original native `check_teamly` used `\b10\b` anywhere in the page, accepting the archived page that says **11 assignments** twice because its assignment date contains `2014-10-19`. The only regex match in that body is the month, not an assignment count. A successful page creation is archived at original trace line 13, selected-line SHA256 `884097def7794a792d25788e86d19433734f49cea0f9466a5c52cf5113597225`.

The candidate checks common explicit Russian/English assignment total labels and standalone count clauses, stripping Markdown emphasis. It rejects conflicting parsed totals and avoids interpreting a dated month or a qualified subset such as “5 assignments due next week” as the overall count. Page boundaries retain newlines so a count at the beginning of the body remains a standalone clause.

Validation directly invokes the existing native `check_teamly` with its database rows stubbed. The test does not duplicate the check condition. Nine unittest methods contain positive and negative cases, including the literal archived body, a corrected copy, dates with and without a count, other counts, Markdown, Russian and English totals, contradictory totals, legitimate subsets, decimals and negative numbers. No database, model calls or workspace services are needed.

- Pristine source plus candidate tests: exit 1, nine tests, twelve assertion/subtest failures; `/private/tmp/cowork-teamly-count-red.log`.
- Candidate source plus same tests: exit 0, nine tests; `/private/tmp/cowork-teamly-count-green.log`.
- `git diff --check`: exit 0.
- Independent review: pending at time of handoff.
- Full task rerun: not performed. Historical result and score unchanged; new checker would expose an additional genuine failure rather than turn the case GREEN.

Scope is three files beneath this case's `evaluation/`: `main.py`, `test_main.py`, and `fixtures/teamly-count-witness.json`. Task text and groundtruth remain unchanged. No runtime code, benchmark score, or model output changed.

This is a bounded lexical parser, not general natural-language understanding. Spelled-out totals, arbitrary paraphrases, table-based summaries, and implicit counts may need a separate contract and tests. Existing page aggregation, course-name matching and points matching are unchanged in purpose and remain outside this narrow fix. The secondary checker correction must not close the parent agent failure.

## Independent review correction

The first candidate passed nine tests but review found that unanchored labels could accept negated or qualified statements, ignore a contradictory course-wide count, and reject ordinary English course-total wording. New tests directly exercise the native checker with those counterexamples before changing the parser. Their RED log is `cowork-teamly-count-review-red.log`.

The revised parser matches whole clauses. It recognizes the course `has`, `contains`, or `includes` a numeric assignment count, `There are N assignments in <course>`, explicit count labels, and `N assignments overall` / `in total`. Qualified suffixes such as `completed` or `due next week` and negated label clauses do not contribute a total. Separate recognized total clauses must agree. Decimal separators remain intact so `10.5` and `10,5` cannot be parsed as integer ten.

The final fourteen unittest methods retain all original archive/date/subset controls and add the review counterexamples plus controls where a subset or negated label accompanies a valid total:

- Final tests against pristine d943: exit 1, `cowork-teamly-count-final-baseline-red.log`.
- Final tests against candidate: exit 0, fourteen tests, `cowork-teamly-count-review-green.log`.
- Initial baseline/candidate logs remain as `cowork-teamly-count-red.log` and `cowork-teamly-count-green.log`.
- `provenance.json` records the original trace line, selected-line SHA256, full-trace SHA256 and the committed fixture SHA256.

Reproduce from repository root with `python3 -m unittest discover -s tasks/finalpool/canvas-assignment-word-teamly/evaluation -p test_main.py`. The fixture is a literal body extracted from the historical successful page write. The corrected positive fixture is synthesized only in a test; it is not an agent output or proof that the agent error was fixed.

## Course-scope rereview correction

The fourteen-test candidate still rejected `Всего в курсе 10 заданий` and accepted `There are 10 assignments in draft`. These were reproduced as native RED tests before editing, recorded in `cowork-teamly-count-scope-red.log`. The reviewer's prior independent observations are retained in `cowork-teamly-count-independent-review-final.log` (that filename predates this correction).

The Russian course clause now accepts the optional `всего` prefix. The English `in` suffix is restricted to `total`, `the/this course`, course code `CCC-2014J`, the course's English name (including the fall label), or its existing expected Russian name. Arbitrary locators such as draft, review and module one cannot establish the whole-course count. This replaces the earlier unrestricted `<course>` suffix described above.

The final sixteen unittest methods include correct/wrong counts for supported scopes and negative subset locators. `cowork-teamly-count-scope-baseline-red.log` records exit 1 against pristine d943; `cowork-teamly-count-scope-green.log` records exit 0 against the latest candidate. Source is frozen for independent rereview. Component still awaits review and full task validation; the actual agent output remains wrong and its historical FAIL stays open.

## Final independent review

The final frozen 16-test suite passed independently. Initial P2 findings and follow-up boundaries were reproduced and fixed with negative/positive controls; all initial and final review records are preserved alongside this journal. See `cowork-teamly-count-independent-review.md`. The archived wrong total11 remains FAIL. This is a secondary grader correction, not a fix for the agent’s erroneous count.
