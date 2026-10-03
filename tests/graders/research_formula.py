"""Intentionally RED research; no production formula fix is proposed as complete."""
from noise_formula_support import Harness, unittest


class FormulaResearchTests(Harness):
    def test_archived_formula_does_not_require_specific_local_variable_names(self):
        self.assertTrue(self.formula())

    def test_comments_strings_and_wrong_sign_or_coefficient_do_not_prove_formula(self):
        for source in [
            "# avg_rating and 2 * pct_below_3stars\npass",
            'text="(avg_rating/5)*100 - 2*pct_below_3stars"',
            "qscore=(avg_rating/5)*100 + 2*pct_below_3stars",
            "qscore=(avg_rating/5)*100 - 3*pct_below_3stars",
        ]:
            with self.subTest(source=source):
                self.assertFalse(self.formula(source))


    def test_metric_roles_dead_code_and_unused_formula_are_not_computation(self):
        for source in [
            'qscore=(pct_below_3stars/5)*100 - 2*avg_rating',
            'if False:\n    qscore=(avg_rating/5)*100 - 2*pct_below_3stars',
            'unused=(avg_rating/5)*100 - 2*pct_below_3stars\nqscore=0',
        ]:
            with self.subTest(source=source):
                self.assertFalse(self.formula(source))


if __name__ == "__main__":
    unittest.main()
