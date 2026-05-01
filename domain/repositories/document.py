from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.document import Document, DocumentStatus


class DocumentRepository(ABC):
    @abstractmethod
    def get_by_id(self, document_id: UUID) -> Document | None: ...

    @abstractmethod
    def save(self, document: Document) -> None: ...

    @abstractmethod
    def list_by_status(self, status: DocumentStatus) -> list[Document]: ...

    @abstractmethod
    def list_by_category(self, category: str) -> list[Document]: ...
