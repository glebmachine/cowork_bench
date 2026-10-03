"""Exercise the native Teamly checker without a database or document service."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


HERE = Path(__file__).parent
CRITICAL = "Teamly 'CCC-2014J Assignment Overview' page mentions course, count 10, points 300"


class TeamlyAssignmentCountTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("canvas_evaluation", HERE / "main.py")
        self.grader = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"psycopg2": types.ModuleType("psycopg2")}):
            spec.loader.exec_module(self.grader)

    def accepted(self, body):
        cursor = Mock()
        cursor.fetchall.return_value = [("CCC-2014J Assignment Overview", body)]
        connection = Mock()
        connection.cursor.return_value = cursor
        self.grader.PASS_COUNT = 0
        self.grader.FAIL_COUNT = 0
        self.grader.FAILED_NAMES = []
        with patch.object(self.grader.psycopg2, "connect", return_value=connection, create=True):
            with contextlib.redirect_stdout(io.StringIO()):
                self.grader.check_teamly()
        return CRITICAL not in self.grader.FAILED_NAMES

    def test_archived_wrong_count_does_not_pass_due_to_date_month(self):
        body = json.loads((HERE / "fixtures" / "teamly-count-witness.json").read_text())["body"]
        self.assertIn("2014-10-19", body)
        self.assertIn("11 заданий", body)
        self.assertFalse(self.accepted(body))

    def test_corrected_archived_count_passes(self):
        body = json.loads((HERE / "fixtures" / "teamly-count-witness.json").read_text())["body"]
        self.assertTrue(self.accepted(body.replace("11 заданий", "10 заданий")))

    def test_date_without_assignment_count_fails(self):
        self.assertFalse(self.accepted("Total points: 300.0. Due date: 2014-10-19."))

    def test_other_counts_do_not_borrow_ten_from_date(self):
        for count in (0, 1, 9, 11, 100, 110):
            with self.subTest(count=count):
                self.assertFalse(self.accepted(f"{count} assignments. Points: 300. Date: 2014-10-19."))

    def test_count_wording_and_markdown(self):
        for text in ("10 assignments", "**10 заданий**", "Total Assignments: 10", "Total Assignments: 10.",
                     "Всего заданий: 10", "Количество заданий — 10", "**Total Assignments:** **10**"):
            with self.subTest(text=text):
                self.assertTrue(self.accepted(text + "\nTotal points: 300.0"))

    def test_conflicting_explicit_counts_fail(self):
        self.assertFalse(self.accepted("10 assignments. Итого: 11 заданий. Total points: 300."))

    def test_subset_count_does_not_contradict_total(self):
        self.assertTrue(self.accepted("10 assignments, 5 assignments due next week. Total points: 300."))
        self.assertTrue(self.accepted("В курсе 10 заданий. 5 заданий сдаются завтра. Всего баллов: 300."))

    def test_correct_total_with_different_date_month_passes(self):
        self.assertTrue(self.accepted("Total Assignments: 10\nTotal points: 300. Date: 2014-11-19."))

    def test_fraction_negative_and_subset_are_not_total(self):
        for text in ("Total Assignments: 10.5", "Total Assignments: 10,5",
                     "Total Assignments: -10", "10 graded assignments"):
            with self.subTest(text=text):
                self.assertFalse(self.accepted(text + "\nTotal points: 300. Date: 2014-10-19."))

    def test_review_contradictory_course_total_fails(self):
        self.assertFalse(self.accepted(
            "Total assignments: 10. There are 11 assignments in the course. Total points: 300."))

    def test_review_subset_label_cannot_hide_overall_count(self):
        self.assertFalse(self.accepted(
            "Total assignments: 10 completed; 11 assignments overall. Total points: 300."))

    def test_review_negated_label_is_not_positive_total(self):
        self.assertFalse(self.accepted("Not total assignments: 10. Total points: 300."))

    def test_review_course_total_variants_pass(self):
        for text in ("There are 10 assignments in Creative Computing & Culture",
                     "The course includes 10 assignments", "10 assignments overall", "10 assignments in total"):
            with self.subTest(text=text):
                self.assertTrue(self.accepted(text + ". Total points: 300."))

    def test_subset_and_negated_labels_do_not_override_real_total(self):
        for text in ("Total assignments: 5 completed; 10 assignments overall",
                     "Not total assignments: 11; The course includes 10 assignments",
                     "Total assignments: 10; there are 5 assignments due next week"):
            with self.subTest(text=text):
                self.assertTrue(self.accepted(text + ". Total points: 300."))

    def test_russian_total_course_prefix(self):
        self.assertTrue(self.accepted("Всего в курсе 10 заданий. Общая сумма баллов: 300."))
        self.assertFalse(self.accepted("Всего в курсе 11 заданий. Общая сумма баллов: 300."))

    def test_there_are_locator_must_identify_the_course(self):
        for scope in ("draft", "review", "module one"):
            with self.subTest(scope=scope):
                self.assertFalse(self.accepted(f"There are 10 assignments in {scope}. Total points: 300."))
        for scope in ("the course", "this course", "Creative Computing & Culture", "CCC-2014J", "total"):
            for count in (10, 11):
                with self.subTest(scope=scope, count=count):
                    self.assertEqual(count == 10, self.accepted(
                        f"There are {count} assignments in {scope}. Total points: 300."))


if __name__ == "__main__":
    unittest.main()
