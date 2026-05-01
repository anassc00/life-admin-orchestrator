from datetime import datetime
from uuid import UUID

from domain.entities.calendar import Appointment
from domain.repositories.calendar import AppointmentRepository
from infrastructure.django_app.models.calendar import AppointmentModel


class DjangoAppointmentRepository(AppointmentRepository):
    def get_by_id(self, appointment_id: UUID) -> Appointment | None:
        try:
            record = AppointmentModel.objects.get(pk=appointment_id)
            return self._to_entity(record)
        except AppointmentModel.DoesNotExist:
            return None

    def save(self, appointment: Appointment) -> None:
        AppointmentModel.objects.update_or_create(
            pk=appointment.id,
            defaults=self._to_record(appointment),
        )

    def list_by_range(self, start: datetime, end: datetime) -> list[Appointment]:
        return [
            self._to_entity(r)
            for r in AppointmentModel.objects.filter(
                start_time__lt=end,
                end_time__gt=start,
            )
        ]

    def delete(self, appointment_id: UUID) -> None:
        AppointmentModel.objects.filter(pk=appointment_id).delete()

    @staticmethod
    def _to_entity(record: AppointmentModel) -> Appointment:
        return Appointment(
            id=record.id,
            title=record.title,
            description=record.description,
            start_time=record.start_time,
            end_time=record.end_time,
            location=record.location,
            attendees=record.attendees,
            is_confirmed=record.is_confirmed,
        )

    @staticmethod
    def _to_record(appointment: Appointment) -> dict:
        return {
            "title": appointment.title,
            "description": appointment.description,
            "start_time": appointment.start_time,
            "end_time": appointment.end_time,
            "location": appointment.location,
            "attendees": list(appointment.attendees),
            "is_confirmed": appointment.is_confirmed,
        }
