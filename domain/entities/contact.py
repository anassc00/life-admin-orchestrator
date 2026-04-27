from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Contact(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str = ""
    phone: str = ""
    company: str = ""
    tags: list[str] = Field(default_factory=list)
    notes: str = ""


class Interaction(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    contact_id: UUID
    channel: str  # email | phone | meeting | message
    summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
