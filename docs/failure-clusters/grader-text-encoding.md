# Text representation and explicit category ranking

Two cases from grader-natural-language-matching, base d943e75. No task, agent or original measurement changes. The other six cases in the parent cluster remain open.

## Reproduced defects

- fetch-insales-market-analysis-excel-ppt-email: the CEO keyword check accepts `high priority` but rejects ordinary `high-priority` and `High_Priority_Categories`. The fix accepts separators at word boundaries; high-prioritization, priorityless, missing/low priority and wrong prefixes remain rejected.
- terminal-insales-yf-ppt-notion-email: the grader parses JSON then serializes with default ASCII escaping and searches for a Cyrillic category in that encoded string. Correct Unicode category values fail. It also searches anywhere, which accepts an ASCII expected category at rank 2 or in commentary.

A simple ensure_ascii=False patch would turn the historical wrong ranking into a false PASS. It was tested and rejected: three negative controls failed. The final checker reads explicit category/ranking values instead of searching serialized text. It accepts explicit rank 1 regardless of row order, ordered rankings without explicit ranks, top3/top_categories, and top_category/best_category. Conflicting declarations, duplicate identities/ranks, partial ranks, malformed rankings and prose-only mentions fail. Unknown JSON layouts remain unsupported; task text does not prescribe these field names, so review must assess this boundary before publication.

## Historical evidence correction

The unchanged archived category_market_analysis.json ranks TV & Home Theater first and Electronics second. The expected Electronics value is present but is not identified as the winner. Fixture and source SHA256 are recorded in tests/graders/fixtures/text_encoding/provenance.json. The fixed checker still rejects this real output. Thus Unicode is a proven grader bug, but fixing it does not repair the historical case or establish that the agent's ranking is correct. Source revenue/category interpretation remains separate.

## RED → GREEN

`tests/graders/test_text_encoding.py` calls actual grader functions, with only DB IO replaced by explicit fixture responses. Twelve methods include the original archived JSON and negative controls. No generated script execution or live provider call occurs.

- Original d943e75 graders: 11 failing assertions/subtests across nine methods; evidence/grader-text-encoding/baseline-red.txt.
- Rejected Unicode-only intermediate: three failing negative controls; unicode-only-counterexample-red.txt.
- Final candidate: twelve methods pass; fixed-green.txt.

Reproduce:

```sh
python -m unittest discover -s tests/graders -p test_text_encoding.py
COWORK_GRADER_ROOT=/path/to/clean/d943e75 python -m unittest discover -s tests/graders -p test_text_encoding.py
```

Python needs openpyxl, python-docx and pptx as used by the original graders; psycopg2 is stubbed and no DB is contacted. Ruff F on tests, compile checks on changed Python, and git diff --check pass. Independent review initially found two P2 boundaries (top-list rank/duplicate bypass and category-keyed JSON rejection). Six RED subtests reproduced them before correction. The same shared parser now validates all ranking collections and accepts explicit category-keyed/root mappings. All twelve methods pass; independent re-review is clean. Review evidence: /private/tmp/cowork-text-encoding-independent-review.md. Full two-task PASS is not claimed and baseline 381/496 remains immutable. Publication, if accepted, only inside glebmachine/cowork_bench.

Final review controls: evidence/grader-text-encoding/review-red.txt (six failing subtests across twelve methods), fixed-green.txt (twelve passing methods). The earlier baseline-red.txt records the nine-method version; later actual archived email control and review controls extend it without changing its original evidence.
