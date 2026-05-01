from datetime import UTC, datetime

import pytest

from application.dtos.calendar import ScheduleAppointmentCommand
from application.use_cases.calendar.schedule_appointment import ScheduleAppointmentUseCase
from domain.exceptions.calendar import AppointmentConflictError
from tests.fakes.repositories import InMemoryAppointmentRepository


@pytest.fixture
def repo() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()


class TestScheduleAppointmentUseCase:
    def test_schedules_appointment(self, repo: InMemoryAppointmentRepository):
        uc = ScheduleAppointmentUseCase(appointment_repo=repo)
        command = ScheduleAppointmentCommand(
            title="Team sync",
            start_time=datetime(2026, 5, 2, 9, 0, tzinfo=UTC),
            end_time=datetime(2026, 5, 2, 10, 0, tzinfo=UTC),
        )
        response = uc.execute(command)

        assert response.title == "Team sync"
        assert repo.get_by_id(response.appointment_id) is not None

    def test_raises_on_conflict(self, repo: InMemoryAppointmentRepository):
        uc = ScheduleAppointmentUseCase(appointment_repo=repo)
        base = ScheduleAppointmentCommand(
            title="First meeting",
            start_time=datetime(2026, 5, 2, 10, 0, tzinfo=UTC),
            end_time=datetime(2026, 5, 2, 11, 0, tzinfo=UTC),
        )
        uc.execute(base)

        overlapping = ScheduleAppointmentCommand(
            title="Overlapping meeting",
            start_time=datetime(2026, 5, 2, 10, 30, tzinfo=UTC),
            end_time=datetime(2026, 5, 2, 11, 30, tzinfo=UTC),
        )
        with pytest.raises(AppointmentConflictError):
            uc.execute(overlapping)
