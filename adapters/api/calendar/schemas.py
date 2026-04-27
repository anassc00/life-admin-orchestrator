from datetime import datetime
from uuid import UUID

from ninja import Schema

from application.dtos.calendar import ScheduleAppointmentCommand


class ScheduleAppointmentRequest(Schema):
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    location: str = ""
    attendees: list[str] = []

    def to_command(self) -> ScheduleAppointmentCommand:
        return ScheduleAppointmentCommand(**self.model_dump())


class AppointmentScheduledResponseSchema(Schema):
    appointment_id: UUID
    title: str
    start_time: datetime
    end_time: datetime


class ConflictDetectionResponseSchema(Schema):
    has_conflict: bool
    conflicting_ids: list[UUID] = []


class ReminderSentResponseSchema(Schema):
    appointment_id: UUID
    sent: bool
