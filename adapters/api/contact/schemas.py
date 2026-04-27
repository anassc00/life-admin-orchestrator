from datetime import datetime
from uuid import UUID

from ninja import Schema

from application.dtos.contact import LogInteractionCommand, UpdateContactRecordCommand


class UpdateContactRecordRequest(Schema):
    name: str
    email: str = ""
    phone: str = ""
    company: str = ""
    tags: list[str] = []
    notes: str = ""

    def to_command(self, contact_id: UUID | None = None) -> UpdateContactRecordCommand:
        return UpdateContactRecordCommand(contact_id=contact_id, **self.model_dump())


class ContactUpdatedResponseSchema(Schema):
    contact_id: UUID
    name: str


class LogInteractionRequest(Schema):
    channel: str
    summary: str
    timestamp: datetime | None = None

    def to_command(self, contact_id: UUID) -> LogInteractionCommand:
        return LogInteractionCommand(contact_id=contact_id, **self.model_dump())


class InteractionLoggedResponseSchema(Schema):
    interaction_id: UUID
    contact_id: UUID
