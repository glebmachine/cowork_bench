"""Exercise actual calendar checks in every affected evaluator against PostgreSQL.

Dependencies: psycopg, psycopg2-binary, openpyxl, python-pptx, python-docx.
Use a dedicated empty database via COWORK_TEST_PG_DSN. No model calls.
"""
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from calendar_timezone_fixtures import fixture, mutate
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = Path(os.environ.get('COWORK_GRADER_ROOT', Path(__file__).resolve().parents[2]))
MATRIX = []
SESSIONS = ['UTC', 'Europe/Moscow', 'America/New_York']
CASES = json.loads(Path(__file__).with_name('calendar_timezone_cases.json').read_text())


@unittest.skipUnless(os.environ.get('COWORK_TEST_PG_DSN'), 'Set COWORK_TEST_PG_DSN for PostgreSQL integration')
class RealCalendarGraders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import psycopg
        import psycopg2
        cls.dsn = os.environ['COWORK_TEST_PG_DSN']
        cls.original_connect = staticmethod(psycopg2.connect)
        cls.admin = psycopg.connect(cls.dsn, autocommit=True)
        cls.admin.execute('CREATE SCHEMA IF NOT EXISTS gcal')
        # No IF NOT EXISTS: refuse to overwrite an existing source table.
        cls.admin.execute('CREATE TABLE gcal.events (id serial PRIMARY KEY, summary text, description text, '
                          'start_datetime timestamptz, end_datetime timestamptz, location text, attendees text, start_timezone text, end_timezone text)')

        cls.admin.execute('GRANT USAGE ON SCHEMA gcal TO eigent')
        cls.admin.execute('GRANT SELECT ON gcal.events TO eigent')

    @classmethod
    def tearDownClass(cls):
        cls.admin.execute('DROP TABLE gcal.events')
        cls.admin.close()
        if os.environ.get('COWORK_TIMEZONE_MATRIX'):
            Path(os.environ['COWORK_TIMEZONE_MATRIX']).write_text(json.dumps(MATRIX, indent=2, ensure_ascii=False) + '\n')

    def run_variant(self, case, variant, session_zone):
        import psycopg2
        def connect(**kwargs):
            return self.original_connect(self.dsn, options='-c timezone=' + session_zone)
        path = ROOT/'tasks/finalpool'/case/'evaluation/main.py'
        spec = importlib.util.spec_from_file_location('calendar_evaluator', path)
        module = importlib.util.module_from_spec(spec)
        # Some evaluators query noncalendar seed tables during import. Redirect
        # those too, so no original localhost/production database is contacted.
        with patch.object(psycopg2, 'connect', side_effect=connect), contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as workspace:
            rows, run, accept = fixture(case, module, workspace)
            if variant == 'archived-moscow':
                witness = next(item for item in json.loads(Path(__file__).with_name('calendar_archived_moscow_events.json').read_text()) if item['case'] == case)
                rows = []
                for observation in witness['calendar_creates']:
                    args = observation['arguments']
                    row = dict(summary=args['summary'], description=args.get('description', ''), location=args.get('location', ''), attendees='[]')
                    for key in ['start', 'end']:
                        clock = args[key]
                        stamp = datetime.fromisoformat(clock['dateTime'].replace('Z', '+00:00'))
                        if stamp.tzinfo is None:
                            stamp = stamp.replace(tzinfo=ZoneInfo(clock['timeZone']))
                        row[key + '_datetime'] = stamp
                        row[key + '_timezone'] = clock['timeZone']
                    rows.append(row)
            elif variant in ['dst-autumn', 'dst-autumn-wrong']:
                for row, day in zip(rows, ['2026-11-01', '2026-11-08']):
                    for key in ['start_datetime', 'end_datetime']:
                        row[key] = row[key].replace(year=2026, month=11, day=int(day[-2:]))
                run = lambda: module.check_gcal('2026-10-18 10:00:00')
            elif variant in ['reverse-midnight', 'reverse-wrong-date']:
                day = '2026-03-16' if case == 'terminal-sf-scholarly-excel-ppt-gcal' else '2026-03-10'
                rows = [rows[0]]
                rows[0]['start_datetime'] = datetime.fromisoformat(day + 'T00:30:00+00:00')
                rows[0]['end_datetime'] = rows[0]['start_datetime'] + timedelta(minutes=90)
                if variant == 'reverse-wrong-date':
                    for key in ['start_datetime', 'end_datetime']:
                        rows[0][key] -= timedelta(days=1)
                run = lambda: module.check_reverse_validation(workspace)
                accept = lambda name: name in ['No strategy review events on weekends', 'No price review events before March 10']
            self.admin.execute('TRUNCATE gcal.events RESTART IDENTITY')
            if variant in ['overlap-offset', 'clear-offset']:
                # Existing events retain their own zone. 12:00+03 equals 09:00Z,
                # and 17:00+03 equals 14:00Z; neither is a free slot.
                target = rows[0]['start_datetime']
                if variant == 'clear-offset':
                    target += timedelta(hours=4)
                existing = dict(rows[0], summary='Заседание учёного совета',
                                start_datetime=target.astimezone(timezone(timedelta(hours=3))),
                                end_datetime=(target + timedelta(minutes=90)).astimezone(timezone(timedelta(hours=3))))
                seeded = rows + [existing]
            else:
                mutation = {'archived-moscow': 'utc', 'dst-autumn': 'equivalent-moscow', 'dst-autumn-wrong': 'same-clock-moscow', 'reverse-midnight': 'equivalent-moscow', 'reverse-wrong-date': 'equivalent-moscow', 'allowed-hour-earlier': 'wrong-hour-earlier', 'allowed-minute': 'wrong-minute', 'allowed-date-earlier': 'wrong-date-earlier', 'native-equivalent': 'equivalent-moscow', 'native-shifted': 'same-clock-moscow'}.get(variant, variant)
                seeded = mutate(rows, case, mutation)
            for row in seeded:
                keys = list(row)
                self.admin.execute(f'INSERT INTO gcal.events ({", ".join(keys)}) VALUES ({", ".join(["%s"]*len(keys))})',
                                   [row[key].isoformat() if key.endswith('_datetime') else row[key] for key in keys])
            stored_zones = self.admin.execute('SELECT start_timezone, end_timezone FROM gcal.events').fetchall()
            self.assertEqual(stored_zones, [(row['start_timezone'], row['end_timezone']) for row in seeded])
            checks = {}
            details = {}
            def capture(name, passed, detail='', **kwargs):
                checks[name] = bool(passed)
                details[name] = str(detail)
            for name in ['record', 'check', 'record_critical', 'check_critical', 'critical']:
                if hasattr(module, name):
                    setattr(module, name, capture)
            # Select an isolated database/session; real psycopg2 returns the stored instants.
            returned = None
            if variant.startswith('native-'):
                from psycopg.conninfo import conninfo_to_dict
                connection = conninfo_to_dict(self.dsn)
                environment = dict(os.environ, PGHOST=connection['host'], PGPORT=connection['port'], PGDATABASE=connection['dbname'], PGOPTIONS='-c timezone=' + session_zone)
                environment['PYTHONPATH'] = os.environ.get('COWORK_TEST_DEPENDENCY_PATH', '')
                command = [sys.executable, '-m', 'tasks.finalpool.' + case + '.evaluation.main', '--agent_workspace', workspace]
                child = subprocess.run(command, cwd=ROOT, env=environment, text=True, capture_output=True, timeout=30)
                self.assertEqual(child.returncode, 1, 'Unrelated document/email checks must fail in this calendar-only fixture')
                self.assertNotIn('ModuleNotFoundError', child.stderr)
                name = next(label for label in module.CRITICAL_CHECKS if '(1h each)' in label)
                verdict = [line for line in child.stdout.splitlines() if name in line and line.strip().startswith(('[PASS]', '[FAIL]'))]
                self.assertEqual(len(verdict), 1, child.stdout + child.stderr)
                checks[name] = verdict[0].strip().startswith('[PASS]')
            else:
                with patch.object(psycopg2, 'connect', side_effect=connect), contextlib.redirect_stdout(io.StringIO()):
                    returned = run()
            selected = {name: value for name, value in checks.items() if accept(name)}
            if case in ['moex-options-expiry-monitor', 'sf-support-priority-gcal-excel']:
                selected['calendar errors empty'] = returned == []
            elif case == 'sf-sales-quarterly-review-gcal':
                errors, critical = returned
                selected['calendar errors empty'] = errors == []
                selected.update({name: passed for passed, name in critical})
            self.assertTrue(selected, f'No calendar verdict captured for {case}')
            expected = variant in ['utc', 'equivalent-moscow', 'equivalent-east', 'equivalent-west', 'clear-offset', 'dst-autumn', 'reverse-midnight', 'allowed-hour-earlier', 'allowed-minute', 'allowed-date-earlier', 'native-equivalent']
            MATRIX.append(dict(case=case, session_zone=session_zone, variant=variant, expected=expected, passed=all(selected.values()), checks=selected, input_start=seeded[0]['start_datetime'].isoformat(), input_zone=seeded[0]['start_timezone'], archived_details=details if variant == 'archived-moscow' else {}, archived_errors=returned if variant == 'archived-moscow' else None))
            self.assertEqual(all(selected.values()), expected, selected)
            if variant == 'archived-moscow':
                if case == 'moex-options-expiry-monitor':
                    self.assertTrue(any('starts at 06:00, expected 09:00' in error for error in returned), returned)
                else:
                    self.assertTrue(any('parts(summary,time,loc)=(True, False, True)' in detail for detail in details.values()), details)


# Each scenario invokes the actual checker and real PostgreSQL in all three sessions.
for case in CASES:
    variants = ['utc', 'equivalent-moscow', 'equivalent-east', 'equivalent-west', 'same-clock-moscow', 'wrong-hour', 'wrong-date']
    if case == 'canvas-late-submission-word-gcal':
        variants += ['native-equivalent', 'native-shifted']
    if case in ['insales-product-review-analysis-gform-gcal', 'terminal-arxiv-canvas-gsheet-word-gcal']:
        variants += ['allowed-hour-earlier', 'allowed-minute']
    if case == 'terminal-arxiv-canvas-gsheet-word-gcal':
        variants += ['allowed-date-earlier']
    if case in ['canvas-late-submission-word-gcal', 'insales-product-review-analysis-gform-gcal', 'terminal-moex-canvas-excel-gcal-email', 'terminal-sf-scholarly-excel-ppt-gcal']:
        variants += ['wrong-duration']
    if case in ['moex-options-expiry-monitor', 'moex-portfolio-ppt-gcal']:
        variants += ['archived-moscow']
    if case == 'terminal-arxiv-canvas-gsheet-word-gcal':
        variants += ['dst-autumn', 'dst-autumn-wrong']
    if case in ['terminal-sf-scholarly-excel-ppt-gcal', 'terminal-insales-pw-pricing-excel-word-gcal']:
        variants += ['reverse-midnight', 'reverse-wrong-date']
    if case in ['terminal-moex-canvas-excel-gcal-email', 'terminal-sf-scholarly-excel-ppt-gcal']:
        variants += ['overlap-offset', 'clear-offset']
    for variant in variants:
        for session_zone in SESSIONS + (['Pacific/Kiritimati'] if case == 'scholarly-reading-group-gcal-gsheet-word' else []):
            def test(self, case=case, variant=variant, session_zone=session_zone):
                self.run_variant(case, variant, session_zone)
            setattr(RealCalendarGraders, f'test_{case.replace("-", "_")}__{variant.replace("-", "_")}__{session_zone.replace("/", "_")}', test)

if __name__ == '__main__':
    unittest.main()
