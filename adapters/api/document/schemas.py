from uuid import UUID

from ninja import Schema

from application.dtos.document import (
    ArchiveDocumentCommand,
    ClassifyDocumentCommand,
    RegisterDocumentCommand,
)
from domain.entities.document import DocumentStatus


class RegisterDocumentRequest(Schema):
    filename: str
    content_type: str

    def to_command(self) -> RegisterDocumentCommand:
        return RegisterDocumentCommand(**self.model_dump())


class DocumentRegisteredResponseSchema(Schema):
    document_id: UUID
    filename: str
    status: DocumentStatus


class ClassifyDocumentRequest(Schema):
    category: str
    metadata: dict = {}

    def to_command(self, document_id: UUID) -> ClassifyDocumentCommand:
        return ClassifyDocumentCommand(document_id=document_id, **self.model_dump())


class DocumentClassifiedResponseSchema(Schema):
    document_id: UUID
    category: str
    metadata: dict


class ArchiveDocumentRequest(Schema):
    storage_path: str

    def to_command(self, document_id: UUID) -> ArchiveDocumentCommand:
        return ArchiveDocumentCommand(document_id=document_id, storage_path=self.storage_path)


class DocumentArchivedResponseSchema(Schema):
    document_id: UUID
    storage_path: str
    status: DocumentStatus
