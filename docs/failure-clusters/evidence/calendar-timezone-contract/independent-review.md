# Independent calendar expectation review

Reviewed local checkout `/private/tmp/cowork-upstream-timezone` against upstream `d943e75bc0fc8e3b27141979300cd8cbcd1e890d`. Independent reviewer did not author or edit implementation/tests. No publication performed.

Verdict: no blocking implementation findings in the scoped twenty-grader timezone fix. Independent final run: **503 tests passed**, including **496 actual PostgreSQL scenarios**, in 5.107 seconds. Disposable database: `cowork_timezone_independent_review` on local port 5434. Log: `/private/tmp/cowork-timezone-independent-review-tests.log`. Matrix: `/private/tmp/cowork-timezone-independent-review-matrix.json`. `git diff --check` passed.

## Findings and checks

- `utils/evaluation/calendar_time.py:9` converts aware values with `astimezone(UTC)`, preserving instants, rejecting naive timestamps, and never trusting stored event-zone labels as expectation authority. All twenty main calendar fetch paths call the helper. No agent, storage, task text, source fixture, groundtruth or runtime changes were present in the reviewed implementation diff.
- SQL dates and range boundaries use explicit UTC: e.g. `tasks/finalpool/insales-product-review-analysis-gform-gcal/evaluation/main.py:273`, `tasks/finalpool/kulinar-weekly-gsheet-gcal/evaluation/main.py:247`. Reverse checks also use UTC: pricing cutoff at `tasks/finalpool/terminal-insales-pw-pricing-excel-word-gcal/evaluation/main.py:453`, weekday at `tasks/finalpool/terminal-sf-scholarly-excel-ppt-gcal/evaluation/main.py:357`.
- Conflict paths preserve instant comparisons: injected rows normalize at `tasks/finalpool/terminal-moex-canvas-excel-gcal-email/evaluation/main.py:163`; SQL overlap parameters stay aware at `tasks/finalpool/terminal-sf-scholarly-excel-ppt-gcal/evaluation/main.py:328`. Offset-equivalent conflicts remain failures and clear slots remain passes.
- Thresholds, required clock values, day/minute tolerances and duration predicates are unchanged. Existing permissive time/day controls remain passing. Review caught a new negative fixture using a still-allowed three-hour duration; author changed only the fixture to four hours. The original canvas criterion is `0 < duration <= 3 hours`, not the one-hour wording of its label.
- PostgreSQL tests exercise each real affected calendar checker in UTC, Europe/Moscow and America/New_York sessions. Equivalent UTC/+03/east/west spellings pass; identical clock text with +03 genuinely shifts the instant and fails the existing expectation. Scholarly additionally uses Pacific/Kiritimati to expose its date-only representation defect while preserving its already-explicit UTC hour SQL.
- Native subprocess tests invoke the actual module CLI from repository cwd with isolated PostgreSQL routing; only dependency path is supplied through PYTHONPATH, not a repository import crutch. Equivalent +03 calendar output passes; shifted output fails. Whole-task exit remains failure because unrelated document fixtures are intentionally absent.
- Archived Moscow negative tests preserve source arguments and explicitly assert the time cause: options starts at 06:00 UTC versus expected 09:00; portfolio detail is `(summary,time,location)=(True,False,True)`. Synthetic fixtures and archived tool-call projections are clearly separate. These are calendar-check results, not model reruns or whole-task success claims.

## Coverage limits / deferred work

The original design proposal was superseded: implementation normalizes fetched datetime values and explicit SQL expressions, not session timezone. It makes no global task-zone or agent prompt change. UTC is the scoped benchmark expectation; arbitrary configured task zones are not added.

Real-checker DST coverage includes launch-derived dates across transitions; exact repeated New York 01:30 fold instants and spring-gap conversion are helper-level tests. Do not describe those particular fold instants as a full real-checker PostgreSQL replay. The implementation's UTC normalization avoids local-wall-clock fold ambiguity, and no new issue was found, but the broader proposed fold replay is not established by this suite.

The repository under review is the external Cowork checkout, not the Ouroboros runtime. No Ouroboros runtime invariants or engineering-rule artifacts were modified. Existing permissive grader predicates and unrelated unclosed-file ResourceWarnings are unchanged and outside this timezone fix.
