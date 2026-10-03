# Independent review: Teamly assignment total

Verdict: **changes requested**. Reviewed local uncommitted diff against d943e75 in `/private/tmp/cowork-fix-teamly-count`; no implementation edits, commit or publication by reviewer.

## P2: valid ordinary overview prose becomes a false FAIL

Location: `tasks/finalpool/canvas-assignment-word-teamly/evaluation/main.py:189` (patterns through line191).
The Teamly task requires mentioning course/count/points, without requiring a label or sentence template. The new restricted patterns reject valid “There are 10 assignments in Creative Computing & Culture. Total points: 300.” and “The course includes 10 assignments. Total points: 300.” through the actual `check_teamly`. Both contain the explicit whole-course count and satisfied the old count check. Support common whole-course count clauses, with paired wrong-count controls, rather than imposing an undeclared label format.

## P2: contradictory totals and subset counts still produce false PASS

Location: `tasks/finalpool/canvas-assignment-word-teamly/evaluation/main.py:187` (recognition) and line194 (all-recognized-counts decision).
The checker accepts “Total assignments: 10. There are 11 assignments in the course. Total points: 300.” because it recognizes only10 and silently ignores the contradictory11. It also accepts “Total assignments: 10 completed; 11 assignments overall. Total points: 300.”, treating a qualified subset as the total. “Not total assignments: 10. Total points: 300.” passes despite negation. Restrict extracted counts to affirmative whole-course assertions and inspect conflicting recognized total clauses; add these actual-checker negative controls. Arbitrary NLP need not be solved, but currently claimed total/subset/contradiction behavior is not reliable for these ordinary forms.

## Verified evidence

- Independently ran nine supplied tests: PASS, 0.006s. Command: `/Users/glebmikheev/prj/ouroboros-bank-backend/.venv/bin/python -m unittest discover -s tasks/finalpool/canvas-assignment-word-teamly/evaluation -p test_main.py`.
- Additional probes use the supplied harness calling actual `check_teamly`; only DB rows are mocked. Results preserved in `/private/tmp/cowork-teamly-count-independent-review.log`.
- Original wrong11 archived page is now correctly rejected; corrected10 witness passes. Baseline bug mechanism is valid: old `\b10\b` borrowed month10 from2014-10-19.
- Witness source trace line13 SHA matches `884097def7794a792d25788e86d19433734f49cea0f9466a5c52cf5113597225`; fixture body equals exact `teamly__create_page.arguments.body`. No whole-case/model rerun; original agent's wrong11 remains wrong.
- `git diff --check` passed. Task text, other predicates and source data are unchanged. Review applies only to this candidate, not the separate Canvas language aliases fix.

## SHA256 of reviewed files

- `/private/tmp/cowork-fix-teamly-count/tasks/finalpool/canvas-assignment-word-teamly/evaluation/main.py`: `1df493d1fb8b76df69aa8230efe5f647554598664356b276e8bec8b5d1206b24`
- `/private/tmp/cowork-fix-teamly-count/tasks/finalpool/canvas-assignment-word-teamly/evaluation/test_main.py`: `e00831bb130e3cfbb63d2abc1b086e06e3517a1682d384f03bec422eb681e968`
- `/private/tmp/cowork-fix-teamly-count/tasks/finalpool/canvas-assignment-word-teamly/evaluation/fixtures/teamly-count-witness.json`: `f034afb62654a2b5ec5a4255b60de36228d7d4367ae6c6713d187a193ae34e5a`
- `/private/tmp/cowork-fix-teamly-count/tasks/finalpool/canvas-assignment-word-teamly/docs/task.md`: `403c029b837e4f492d980821fda927d7698a17e5017aa02b30b4bbb31f1aff81`
- `/private/tmp/cowork-teamly-count-independent-review.log`: `4600daf740453a0bd2317ecd5c612a8e886b33fc8275da1000533aa450421d4a`
