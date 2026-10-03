"""Small synthetic calendar fixtures derived from the twenty public task contracts.

Noncalendar values are intentionally minimal: these fixtures prove calendar
judgements, not Excel/Word/agent end-to-end success or baseline rescoring.
"""
from datetime import date, datetime, timedelta, timezone


def event(summary, day, start, minutes=60, description='Review action plan', **extra):
    stamp = datetime.fromisoformat(f'{day}T{start}:00').replace(tzinfo=timezone.utc)
    return dict(summary=summary, description=description, start_datetime=stamp,
                end_datetime=stamp + timedelta(minutes=minutes), location='', attendees='[]', start_timezone='Europe/Moscow', end_timezone='Europe/Moscow', **extra)


def fixture(case, module, workspace):
    """Return (rows, callable, selected-verdict predicate). No calendar logic mocked."""
    accept = lambda name: True
    if case == 'canvas-late-submission-word-gcal':
        rows = [event('Late Submission Review', '2026-04-01', f'{h}:00',
                      description=course) for h, course in zip([10, 11, 14], module.TOP3_SUBSTR)]
        run = module.check_calendar
    elif case == 'canvas-quiz-remediation-forms-gcal':
        rows = [event('Remediation Session: Quiz A', '2026-03-16', '15:00'),
                event('Remediation Session: Quiz B', '2026-03-17', '15:00')]
        run = lambda: module.check_gcal(['Quiz A', 'Quiz B'], date(2026, 3, 16))
    elif case == 'fetch-arxiv-conference-schedule-gcal-teamly':
        rows = [event(f'Reading Group: {topic}', f'2026-03-{d}', '14:00', 90,
                      description=module.SOURCE_PAPER_TITLES[0])
                for d, topic in [(18, 'transformer'), (19, 'attention'), (20, 'optimization')]]
        run = lambda: module.check_calendar((1, 'Conference Reading List', module.SOURCE_PAPER_TITLES[0]))
    elif case == 'fetch-kulinar-catering-excel-gcal-email':
        rows = [event(f'Wellness Week Meal Prep - {day}', f'2026-03-{16+i}', '07:00')
                for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
        # Monolithic evaluator runs with absent workbook/email fixtures. Only its
        # real calendar verdicts are selected; unrelated failures are expected.
        run = lambda: module.run_evaluation(workspace, workspace, '2026-03-07 10:00:00', None)
        accept = lambda name: 'calendar' in name.lower()
    elif case == 'fetch-sf-sales-forecast-ppt-gcal':
        rows = [event('Board Forecast Presentation', '2026-03-28', '10:00', 90,
                      description='Revenue forecast 100000 for region North')]
        run = lambda: module.check_calendar(dict(total_q2=100000, top_region='North'))
    elif case == 'insales-order-monthly-ppt-gcal':
        rows = [event('Monthly Sales Review', '2026-04-15', '14:00')]
        run = module.check_calendar
    elif case == 'insales-product-bundle-excel-ppt-gcal':
        rows = [event('Bundle launch', f'2026-03-{day}', '10:00') for day in [16, 18, 20]]
        run = module.check_calendar
    elif case == 'insales-product-review-analysis-gform-gcal':
        rows = [event('Product Quality Review', '2026-03-20', '14:00')]
        run = module.check_gcal_event
    elif case == 'kulinar-weekly-gsheet-gcal':
        rows = [event(f'Dinner Prep - Day {i}', f'2026-04-{6+i:02}', '18:00', description='Dinner')
                for i in range(1, 8)]
        run = lambda: module.check_gcal({i: 'Dinner' for i in range(1, 8)})
    elif case == 'moex-options-expiry-monitor':
        rows = []
        for symbol in module.EXP_SUMMARY['stocks_with_near_expiry']:
            day = next(exp for sym, exp, kind in module.EXP_NEAR_GROUPS if sym == symbol)
            rows.append(event(f'Options Expiry Alert: {symbol}', day, '09:00', 30))
        run = lambda: module.critical_gcal(module._gcal_events())
    elif case == 'moex-portfolio-ppt-gcal':
        row = event('Portfolio Review', '2026-06-15', '14:00')
        row['location'] = 'Conference Room A'
        rows = [row]
        run = module.check_gcal
    elif case == 'scholarly-reading-group-gcal-gsheet-word':
        rows = [event('Reading Group', f'2026-03-{day}', '15:00', 90) for day in [16, 23, 30]]
        run = module.check_gcal
    elif case == 'sf-sales-quarterly-review-gcal':
        rows = [event('Sales planning', day, '10:00', 120)
                for day in ['2026-04-01', '2026-07-01', '2026-10-01', '2027-01-04']]
        run = module.check_gcal
    elif case == 'sf-support-priority-gcal-excel':
        rows = [event('SLA Review', day, '09:00') for day in ['2026-04-06', '2026-05-04', '2026-06-01']]
        run = module.check_gcal
    elif case == 'sf-support-resolution-word-gcal':
        rows = [event('Resolution review', '2026-03-12', '14:00')]
        run = module.check_gcal
    elif case == 'teamly-forms-gcal-onboarding':
        row = event('Orientation Session', '2026-03-16', '09:00', 180)
        row['attendees'] = str(module.HIRE_EMAILS)
        rows = [row, event('Team Lunch', '2026-03-16', '12:00')]
        run = module.check_gcal
    elif case == 'terminal-arxiv-canvas-gsheet-word-gcal':
        rows = [event('Curriculum Review Meeting', '2026-03-21', '10:00', 120),
                event('Faculty Workshop on New Topics', '2026-03-28', '13:00', 180)]
        run = lambda: module.check_gcal('2026-03-07 10:00:00')
    elif case == 'terminal-insales-pw-pricing-excel-word-gcal':
        rows = [event(f'Price Review: {category}', f'2026-03-{10+i}', '14:00', description=f'Gap {gap}%')
                for i, (category, gap) in enumerate(module.EXPECTED_GAPS.items())]
        # Only workbook input is stubbed so the monolithic function reaches its
        # calendar section. Calendar queries and checks remain original code.
        module.read_gap_rows = lambda _: [(category, 100+gap, 100, gap, 'monitor pricing')
                                         for category, gap in module.EXPECTED_GAPS.items()]
        run = lambda: module.critical_checks(workspace)
        accept = lambda name: any(word in name.lower() for word in ['calendar', 'meeting', 'price-review'])
    elif case == 'terminal-moex-canvas-excel-gcal-email':
        rows = [event(topic, f'2026-03-{day}', '14:00', 90)
                for topic, day in [('Intro to Markets', 16), ('Portfolio Basics', 17), ('Risk Management', 18)]]
        run = module.check_calendar
    elif case == 'terminal-sf-scholarly-excel-ppt-gcal':
        rows = [event('Q1 Sales Strategy Review', '2026-03-16', '09:00', 90)]
        run = module.check_gcal
    else:
        raise AssertionError(f'Uncovered case: {case}')
    return rows, run, accept


def mutate(rows, case, variant):
    result = [dict(row) for row in rows]
    for row in result:
        for key in ['start_datetime', 'end_datetime']:
            value = row[key]
            if variant == 'equivalent-moscow':
                value = value.astimezone(timezone(timedelta(hours=3)))
            elif variant == 'same-clock-moscow':
                value = value.replace(tzinfo=timezone(timedelta(hours=3)))
            elif variant == 'equivalent-east':
                value = value.astimezone(timezone(timedelta(hours=14)))
            elif variant == 'equivalent-west':
                value = value.astimezone(timezone(timedelta(hours=-12)))
            elif variant == 'wrong-duration':
                if key == 'end_datetime':
                    value += timedelta(hours=3)
            elif variant == 'wrong-hour':
                # Business hours are a range, so choose 08:00 rather than a
                # different valid slot. All fixed-clock tasks shift by +1 hour.
                value += timedelta(hours=-1 if case == 'terminal-sf-scholarly-excel-ppt-gcal' else 3)
            elif variant == 'wrong-hour-earlier':
                value -= timedelta(hours=1)
            elif variant == 'wrong-date-earlier':
                value -= timedelta(days=1)
            elif variant == 'wrong-minute':
                value += timedelta(minutes=15)
            elif variant == 'wrong-date':
                if case == 'terminal-insales-pw-pricing-excel-word-gcal':
                    value -= timedelta(days=30)  # before the public lower bound
                elif case in ['terminal-moex-canvas-excel-gcal-email', 'terminal-sf-scholarly-excel-ppt-gcal']:
                    value += timedelta(days=(5-value.weekday()) % 7)  # Saturday
                else:
                    value += timedelta(days=3)
            elif variant != 'utc':
                raise AssertionError(variant)
            row[key] = value
    return result
