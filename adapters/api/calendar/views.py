from datetime import datetime
from uuid import UUID

from ninja import Router

from adapters.api.calendar.schemas import (
    AppointmentScheduledResponseSchema,
    ConflictDetectionResponseSchema,
    ReminderSentResponseSchema,
    ScheduleAppointmentRequest,
)
from application.dtos.calendar import DetectConflictQuery, SendReminderCommand
from infrastructure.di import (
    get_detect_conflict_use_case,
    get_schedule_appointment_use_case,
    get_send_reminder_use_case,
)

router = Router(tags=["Calendar"])


@router.post("/appointments", response=AppointmentScheduledResponseSchema)
def schedule_appointment(request, payload: ScheduleAppointmentRequest):
    uc = get_schedule_appointment_use_case()
    return uc.execute(payload.to_command()).model_dump()


@router.get("/conflicts", response=ConflictDetectionResponseSchema)
def detect_conflict(request, start_time: datetime, end_time: datetime):
    uc = get_detect_conflict_use_case()
    return uc.execute(DetectConflictQuery(start_time=start_time, end_time=end_time)).model_dump()


@router.post("/appointments/{appointment_id}/remind", response=ReminderSentResponseSchema)
def send_reminder(request, appointment_id: UUID):
    uc = get_send_reminder_use_case()
    return uc.execute(SendReminderCommand(appointment_id=appointment_id)).model_dump()
