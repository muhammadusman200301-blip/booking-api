"""Pure booking rules, kept free of FastAPI and the database so they are easy to test."""
from datetime import datetime


class BookingError(ValueError):
    """A booking request that breaks a business rule."""


def validate_window(start: datetime, end: datetime) -> None:
    """A booking needs timezone-aware times and must end after it starts."""
    if start.tzinfo is None or end.tzinfo is None:
        raise BookingError("start and end must include a timezone")
    if end <= start:
        raise BookingError("end must be after start")


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Half-open intervals [start, end): a booking ending at 14:00 does not clash with one starting at 14:00."""
    return a_start < b_end and b_start < a_end
