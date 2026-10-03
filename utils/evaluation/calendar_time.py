"""Compare the scoped UTC expectations without trusting an event-selected zone."""

from datetime import datetime, timezone
from typing import Iterable

BENCHMARK_TIMEZONE = timezone.utc


def calendar_datetime(value: datetime) -> datetime:
    """Preserve an aware instant in the benchmark UTC comparison zone."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Calendar timestamps must be timezone-aware")
    return value.astimezone(BENCHMARK_TIMEZONE)


def calendar_rows(rows: Iterable[tuple]) -> list[tuple]:
    """Normalize datetime cells before existing date, clock and duration checks."""
    return [
        tuple(calendar_datetime(value) if isinstance(value, datetime) else value for value in row)
        for row in rows
    ]
