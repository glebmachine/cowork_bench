"""Word noise-exclusion regressions and immutable fixture provenance."""
from noise_formula_support import Harness, FIXTURES, hashlib, json, unittest


class NoiseExclusionTests(Harness):
    def test_archived_explicit_exclusion_is_not_noise_inclusion(self):
        self.assertTrue(self.noise())

    def test_exclusion_notice_must_not_hide_a_second_positive_noise_section(self):
        self.assertFalse(self.noise("Robot Learning with Affordances: method and results."))

    def test_no_noise_reference_is_valid_control(self):
        self.assertTrue(self.noise(replace='Обзор посвящён только LLM.'))

    def test_noise_in_another_deliverable_is_not_excused(self):
        for source in ('teamly', 'gsheet'):
            with self.subTest(source=source):
                self.assertFalse(self.noise(other={source: 'robot learning with affordances'}))

    def test_positive_table_record_is_not_excused(self):
        self.assertFalse(self.noise(replace='Обзор посвящён только LLM.', table=True))

    def test_double_negation_and_conflicting_clauses_are_not_exclusions(self):
        for text in (
            'Работа Robot Learning with Affordances не исключена из обзора.',
            'Неверно, что работа Robot Learning with Affordances в обзор не включена.',
            'Работа Robot Learning with Affordances в обзор не включена, но её метод приведён ниже.',
            'Работа Robot Learning with Affordances в обзор не включена; результаты: робот обучен.',
            'Работа Robot Learning with Affordances включена в обзор. Работа Robot Learning with Affordances в обзор не включена.',
        ):
            with self.subTest(text=text):
                self.assertFalse(self.noise(replace=text))

    def test_archived_fixture_hashes(self):
        manifest = json.loads((FIXTURES / "provenance.json").read_text())
        for row in manifest["sources"]:
            self.assertEqual(hashlib.sha256((FIXTURES / row["fixture"]).read_bytes()).hexdigest(), row["sha256"])


if __name__ == "__main__":
    unittest.main()
