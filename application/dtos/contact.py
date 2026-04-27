from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UpdateContactRecordCommand(BaseModel):
    contact_id: UUID | None = None  # None → create new
    name: str
    email: str = ""
    phone: str = ""
    company: str = ""
    tags: list[str] = []
    notes: str = ""


class ContactUpdatedResponse(BaseModel):
    contact_id: UUID
    name: str


class LogInteractionCommand(BaseModel):
    contact_id: UUID
    channel: str
    summary: str
    timestamp: datetime | None = None


class InteractionLoggedResponse(BaseModel):
    interaction_id: UUID
    contact_id: UUID
