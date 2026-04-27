from celery import shared_task

from infrastructure.di import (
    get_detect_conflict_use_case,
    get_schedule_appointment_use_case,
    get_send_reminder_use_case,
)


@shared_task(name="tasks.calendar.process_event_request", bind=True, max_retries=3)
def process_event_request_task(self, raw_request: str) -> dict:
    """Parse a natural-language event request and schedule via CalendarAgent."""
    from application.agents.calendar_agent import CalendarAgentOrchestrator

    agent = CalendarAgentOrchestrator(
        detect_conflict_uc=get_detect_conflict_use_case(),
        schedule_appointment_uc=get_schedule_appointment_use_case(),
    )
    result = agent.run(raw_request)
    return {"has_conflict": result.get("has_conflict"), "error": result.get("error")}


@shared_task(name="tasks.calendar.send_reminders")
def send_appointment_reminders_task() -> None:
    """Periodic task: find upcoming appointments and dispatch reminder notifications."""
    from datetime import datetime, timedelta, timezone

    from application.dtos.calendar import SendReminderCommand
    from infrastructure.repositories.calendar import DjangoAppointmentRepository

    now = datetime.now(timezone.utc)
    upcoming_window = now + timedelta(hours=24)
    repo = DjangoAppointmentRepository()
    appointments = repo.list_by_range(start=now, end=upcoming_window)

    uc = get_send_reminder_use_case()
    for appointment in appointments:
        uc.execute(SendReminderCommand(appointment_id=appointment.id))
