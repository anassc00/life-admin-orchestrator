import pytest
from datetime import datetime, timezone

from domain.entities.calendar import Appointment


def _make_appointment(
    start: datetime,
    end: datetime,
    title: str = "Meeting",
) -> Appointment:
    return Appointment(title=title, start_time=start, end_time=end)


class TestAppointment:
    def test_creation_defaults(self):
        start = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2026, 5, 1, 11, 0, tzinfo=timezone.utc)
        appt = _make_appointment(start, end)

        assert appt.is_confirmed is False
        assert appt.attendees == []

    def test_confirm_returns_new_instance(self):
        start = datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc)
        end = datetime(2026, 5, 1, 11, 0, tzinfo=timezone.utc)
        appt = _make_appointment(start, end)
        confirmed = appt.confirm()

        assert confirmed.is_confirmed is True
        assert appt.is_confirmed is False

    def test_invalid_time_range_raises(self):
        with pytest.raises(ValueError):
            Appointment(
                title="Bad",
                start_time=datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
                end_time=datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
            )

    def test_overlaps_with(self):
        a = _make_appointment(
            datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
        )
        b = _make_appointment(
            datetime(2026, 5, 1, 11, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 1, 13, 0, tzinfo=timezone.utc),
        )
        c = _make_appointment(
            datetime(2026, 5, 1, 13, 0, tzinfo=timezone.utc),
            datetime(2026, 5, 1, 14, 0, tzinfo=timezone.utc),
        )

        assert a.overlaps_with(b) is True
        assert a.overlaps_with(c) is False
