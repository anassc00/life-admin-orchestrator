from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScheduleAppointmentCommand(BaseModel):
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    location: str = ""
    attendees: list[str] = []


class AppointmentScheduledResponse(BaseModel):
    appointment_id: UUID
    title: str
    start_time: datetime
    end_time: datetime


class DetectConflictQuery(BaseModel):
    start_time: datetime
    end_time: datetime
    exclude_id: UUID | None = None


class ConflictDetectionResponse(BaseModel):
    has_conflict: bool
    conflicting_ids: list[UUID] = []


class SendReminderCommand(BaseModel):
    appointment_id: UUID


class ReminderSentResponse(BaseModel):
    appointment_id: UUID
    sent: bool
