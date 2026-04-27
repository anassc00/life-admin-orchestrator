from uuid import UUID

from pydantic import BaseModel

from domain.entities.document import DocumentStatus


class RegisterDocumentCommand(BaseModel):
    filename: str
    content_type: str


class DocumentRegisteredResponse(BaseModel):
    document_id: UUID
    filename: str
    status: DocumentStatus


class ClassifyDocumentCommand(BaseModel):
    document_id: UUID
    category: str
    metadata: dict = {}


class DocumentClassifiedResponse(BaseModel):
    document_id: UUID
    category: str
    metadata: dict


class ExtractMetadataCommand(BaseModel):
    document_id: UUID
    metadata: dict


class MetadataExtractedResponse(BaseModel):
    document_id: UUID
    metadata: dict


class ArchiveDocumentCommand(BaseModel):
    document_id: UUID
    storage_path: str


class DocumentArchivedResponse(BaseModel):
    document_id: UUID
    storage_path: str
    status: DocumentStatus
