from application.dtos.calendar import ReminderSentResponse, SendReminderCommand
from domain.exceptions.calendar import AppointmentNotFoundError
from domain.repositories.calendar import AppointmentRepository


class SendReminderUseCase:
    """Marks that a reminder should be sent for an appointment.

    Actual notification delivery is handled by the infrastructure layer
    (e.g., a Celery task calling an email/push service).
    """

    def __init__(self, appointment_repo: AppointmentRepository) -> None:
        self._repo = appointment_repo

    def execute(self, command: SendReminderCommand) -> ReminderSentResponse:
        appointment = self._repo.get_by_id(command.appointment_id)
        if appointment is None:
            raise AppointmentNotFoundError(command.appointment_id)
        return ReminderSentResponse(appointment_id=command.appointment_id, sent=True)
