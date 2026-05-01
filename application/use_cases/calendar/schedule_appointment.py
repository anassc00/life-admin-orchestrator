from application.dtos.calendar import AppointmentScheduledResponse, ScheduleAppointmentCommand
from domain.entities.calendar import Appointment
from domain.exceptions.calendar import AppointmentConflictError
from domain.repositories.calendar import AppointmentRepository


class ScheduleAppointmentUseCase:
    def __init__(self, appointment_repo: AppointmentRepository) -> None:
        self._repo = appointment_repo

    def execute(self, command: ScheduleAppointmentCommand) -> AppointmentScheduledResponse:
        appointment = Appointment(
            title=command.title,
            description=command.description,
            start_time=command.start_time,
            end_time=command.end_time,
            location=command.location,
            attendees=command.attendees,
        )

        existing = self._repo.list_by_range(command.start_time, command.end_time)
        conflicts = [a for a in existing if a.overlaps_with(appointment)]
        if conflicts:
            raise AppointmentConflictError(command.start_time, command.end_time)

        self._repo.save(appointment)
        return AppointmentScheduledResponse(
            appointment_id=appointment.id,
            title=appointment.title,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
        )
