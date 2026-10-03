"""Expected-zone conversion never takes authority from the submitted event."""
import unittest
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from utils.evaluation.calendar_time import calendar_datetime, calendar_rows


class CalendarTimeTests(unittest.TestCase):
    def test_moscow_spelling_preserves_instant_not_wall_clock(self):
        expected = datetime.fromisoformat('2026-04-01T10:00:00+00:00')
        self.assertEqual(calendar_datetime(datetime.fromisoformat('2026-04-01T13:00:00+03:00')), expected)
        self.assertNotEqual(calendar_datetime(datetime.fromisoformat('2026-04-01T10:00:00+03:00')), expected)

    def test_naive_timestamp_is_rejected_instead_of_assuming_host_zone(self):
        with self.assertRaises(ValueError):
            calendar_datetime(datetime(2026, 4, 1, 10))

    def test_dst_fold_instants_remain_distinct_in_utc(self):
        zone = ZoneInfo('America/New_York')
        first = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
        second = first.replace(fold=1)
        self.assertEqual(calendar_datetime(first).hour, 5)
        self.assertEqual(calendar_datetime(second).hour, 6)
        self.assertEqual((calendar_datetime(second)-calendar_datetime(first)).total_seconds(), 3600)

    def test_spring_dst_and_utc_date_boundary(self):
        for stamp, expected in [('2026-03-08T01:30:00-05:00', '2026-03-08T06:30:00+00:00'), ('2026-03-08T03:30:00-04:00', '2026-03-08T07:30:00+00:00'), ('2026-03-31T20:30:00-04:00', '2026-04-01T00:30:00+00:00')]:
            self.assertEqual(calendar_datetime(datetime.fromisoformat(stamp)).isoformat(), expected)

    def test_rows_keep_other_cells_and_do_not_mutate_input(self):
        stamp = datetime.fromisoformat('2026-04-01T13:00:00+03:00')
        rows = [('Europe/Moscow', stamp, None, 1)]
        self.assertEqual(calendar_rows(rows), [('Europe/Moscow', stamp.astimezone(timezone.utc), None, 1)])
        self.assertEqual(rows[0][1].hour, 13)

    def test_archived_moscow_fixture_matches_pinned_projection(self):
        directory = Path(__file__).parent
        expected = json.loads((directory / 'calendar_archived_moscow_provenance.json').read_text())
        self.assertEqual(hashlib.sha256((directory / 'calendar_archived_moscow_events.json').read_bytes()).hexdigest(), expected['fixture_sha256'])
