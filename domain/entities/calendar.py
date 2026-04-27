from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Appointment(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    location: str = ""
    attendees: list[str] = Field(default_factory=list)
    is_confirmed: bool = False

    @model_validator(mode="after")
    def validate_time_range(self) -> "Appointment":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self

    def confirm(self) -> "Appointment":
        return self.model_copy(update={"is_confirmed": True})

    def overlaps_with(self, other: "Appointment") -> bool:
        return self.start_time < other.end_time and self.end_time > other.start_time
