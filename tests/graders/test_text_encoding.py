import contextlib


import importlib.util

import io

import json
import os

from pathlib import Path

import sys

import tempfile

import types

import unittest

from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def grader(case):
    grader_root = Path(os.environ.get("COWORK_GRADER_ROOT", ROOT))
    spec = importlib.util.spec_from_file_location(
        case, grader_root / "tasks/finalpool" / case / "evaluation/main.py"
    )
    module = importlib.util.module_from_spec(spec)
    stub = types.ModuleType("psycopg2")
    stub.connect = lambda **kwargs: (_ for _ in ()).throw(
        RuntimeError("No live DB in offline tests")
    )
    with patch.dict(sys.modules, {"psycopg2": stub}):
        spec.loader.exec_module(module)
    return module


class Database:
    def __init__(self, *responses):
        self.responses = iter(responses)

    def cursor(self):
        return self

    def execute(self, *args):
        pass

    def fetchall(self):
        return next(self.responses)

    def close(self):
        pass


def capture(g, name="check"):
    seen = {}
    setattr(
        g, name, lambda label, ok, detail="", **kw: seen.__setitem__(label, bool(ok))
    )
    return seen


class MarketEmailTests(unittest.TestCase):
    def verdict(self, priority, body=None):
        g = grader("fetch-insales-market-analysis-excel-ppt-email")
        g.get_conn = lambda: Database(
            [
                (
                    "Executive summary",
                    "ceo@company.com",
                    body
                    if body is not None
                    else f"Overall market share 1.4%. {priority}. Growth opportunities: 4.",
                )
            ],
            [
                (
                    "Detailed findings",
                    "product_team@company.com",
                    "price leader share priority",
                )
            ],
        )
        seen = capture(g)
        with (
            tempfile.TemporaryDirectory() as tmp,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            g.run_evaluation(tmp, tmp, None, None)
        return seen[
            "CEO email body covers overall share + high-priority + growth opportunities (RU/EN)"
        ]

    def test_archived_ceo_email(self):
        email = json.loads(
            (ROOT / "tests/graders/fixtures/text_encoding/ceo_email.json").read_text()
        )
        self.assertTrue(self.verdict(None, body=email["body"]))

    def test_equivalent_priority_separators(self):
        for label in [
            "2 high-priority categories",
            "High_Priority_Categories: 2",
            "2 high priority categories",
            "HIGH  PRIORITY: 2",
        ]:
            with self.subTest(label=label):
                self.assertTrue(self.verdict(label))

    def test_missing_or_similar_priority_not_accepted(self):
        self.assertFalse(self.verdict("Categories: 2"))
        for label in [
            "high-prioritization",
            "high priorityless",
            "shigh-priority",
            "low priority categories",
        ]:
            with self.subTest(label=label):
                self.assertFalse(self.verdict(label))


class UnicodeCategoryTests(unittest.TestCase):
    def verdict(self, data, expected="электроника"):
        g = grader("terminal-insales-yf-ppt-notion-email")
        g.EXPECTED = {"top_category": expected}
        seen = capture(g)
        with (
            tempfile.TemporaryDirectory() as tmp,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            (Path(tmp) / "category_market_analysis.json").write_text(json.dumps(data))
            g.check_scripts(tmp)
        return seen[
            "category_market_analysis.json top category == DB-computed top category"
        ]

    def test_unicode_top_category(self):
        self.assertTrue(
            self.verdict({"ranking": [{"category": "Электроника", "rank": 1}]})
        )

    def test_explicit_category_keyed_rankings(self):
        for data in [
            {"ranking": {"Электроника": {"rank": 1}, "Камеры": {"rank": 2}}},
            {"Электроника": {"rank": 1}, "Камеры": {"rank": 2}, "notes": "strategy"},
        ]:
            with self.subTest(data=data):
                self.assertTrue(self.verdict(data))

    def test_top_list_cannot_override_ranks_or_duplicate_names(self):
        for data in [
            {
                "top3": [
                    {"category": "Электроника", "rank": 2},
                    {"category": "Камеры", "rank": 1},
                ]
            },
            {"top3": ["Электроника", "Электроника"]},
            {
                "top_categories": [
                    {"category": "Электроника", "rank": 2},
                    {"category": "Камеры", "rank": 1},
                ]
            },
            {
                "top_categories": [
                    {"category": "Электроника"},
                    {"category": "Электроника"},
                ]
            },
        ]:
            with self.subTest(data=data):
                self.assertFalse(self.verdict(data))

    def test_ascii_mention_is_not_top_rank(self):
        self.assertFalse(
            self.verdict(
                {
                    "ranking": [
                        {"category": "cameras", "rank": 1},
                        {"category": "electronics", "rank": 2},
                    ]
                },
                expected="electronics",
            )
        )

    def test_explicit_top_representations(self):
        for data in [
            {
                "ranking": [
                    {"category": "Камеры", "rank": 2},
                    {"category": "Электроника", "rank": 1},
                ]
            },
            {"ranking": [{"category": "Электроника"}, {"category": "Камеры"}]},
            {"top3": ["Электроника", "Камеры"]},
            {"top_categories": [{"category": "Электроника"}]},
            {"top_category": "Электроника"},
        ]:
            with self.subTest(data=data):
                self.assertTrue(self.verdict(data))

    def test_archived_output_is_wrong_rank_not_only_encoding(self):
        path = (
            ROOT / "tests/graders/fixtures/text_encoding/category_market_analysis.json"
        )
        self.assertFalse(self.verdict(json.loads(path.read_text())))

    def test_invalid_rank_evidence_is_not_rescued(self):
        for data in [
            {"ranking": [{"category": "Электроника", "rank": 2}]},
            {
                "ranking": [
                    {"category": "Электроника", "rank": 1},
                    {"category": "Камеры", "rank": 1},
                ]
            },
            {
                "ranking": [
                    {"category": "Электроника", "rank": 1},
                    {"category": "Электроника", "rank": 2},
                ]
            },
            {
                "ranking": [
                    {"category": "Электроника", "rank": 1},
                    {"category": "Камеры"},
                ]
            },
            {"ranking": [], "top_category": "Электроника"},
            {"ranking": [{"category": "Электроника", "rank": True}]},
        ]:
            with self.subTest(data=data):
                self.assertFalse(self.verdict(data))

    def test_category_mention_does_not_prove_top_rank(self):
        for data in [
            {
                "ranking": [
                    {"category": "Камеры", "rank": 1},
                    {"category": "Электроника", "rank": 2},
                ]
            },
            {"notes": "Электроника is not the top category"},
            {
                "ranking": [{"category": "Камеры", "rank": 1}],
                "top_category": "Электроника",
            },
        ]:
            with self.subTest(data=data):
                self.assertFalse(self.verdict(data))

    def test_wrong_category_is_rejected(self):
        self.assertFalse(self.verdict({"ranking": [{"category": "Камеры", "rank": 1}]}))


if __name__ == "__main__":
    unittest.main()
