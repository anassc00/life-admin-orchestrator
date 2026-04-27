from datetime import datetime
from uuid import UUID


class AppointmentNotFoundError(Exception):
    def __init__(self, appointment_id: UUID) -> None:
        super().__init__(f"Appointment {appointment_id} not found")
        self.appointment_id = appointment_id


class AppointmentConflictError(Exception):
    def __init__(self, start_time: datetime, end_time: datetime) -> None:
        super().__init__(f"Schedule conflict between {start_time} and {end_time}")
        self.start_time = start_time
        self.end_time = end_time
