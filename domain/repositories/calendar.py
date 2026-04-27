from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from domain.entities.calendar import Appointment


class AppointmentRepository(ABC):

    @abstractmethod
    def get_by_id(self, appointment_id: UUID) -> Appointment | None: ...

    @abstractmethod
    def save(self, appointment: Appointment) -> None: ...

    @abstractmethod
    def list_by_range(self, start: datetime, end: datetime) -> list[Appointment]: ...

    @abstractmethod
    def delete(self, appointment_id: UUID) -> None: ...
