from datetime import datetime, timedelta, timezone

import pytest

from app.availability import BookingError, overlaps, validate_window

T = datetime(2026, 12, 1, 12, 0, tzinfo=timezone.utc)
H = timedelta(hours=1)


def test_back_to_back_bookings_do_not_overlap():
    assert not overlaps(T, T + 2 * H, T + 2 * H, T + 3 * H)


def test_partial_overlap_is_detected():
    assert overlaps(T, T + 2 * H, T + H, T + 3 * H)


def test_booking_inside_another_is_detected():
    assert overlaps(T, T + 4 * H, T + H, T + 2 * H)


def test_end_before_start_is_rejected():
    with pytest.raises(BookingError):
        validate_window(T + H, T)


def test_naive_datetimes_are_rejected():
    with pytest.raises(BookingError):
        validate_window(T.replace(tzinfo=None), (T + H).replace(tzinfo=None))
