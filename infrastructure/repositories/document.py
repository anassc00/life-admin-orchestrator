from uuid import UUID

from domain.entities.document import Document, DocumentStatus
from domain.repositories.document import DocumentRepository
from infrastructure.django_app.models.document import DocumentModel


class DjangoDocumentRepository(DocumentRepository):
    def get_by_id(self, document_id: UUID) -> Document | None:
        try:
            record = DocumentModel.objects.get(pk=document_id)
            return self._to_entity(record)
        except DocumentModel.DoesNotExist:
            return None

    def save(self, document: Document) -> None:
        DocumentModel.objects.update_or_create(
            pk=document.id,
            defaults=self._to_record(document),
        )

    def list_by_status(self, status: DocumentStatus) -> list[Document]:
        return [self._to_entity(r) for r in DocumentModel.objects.filter(status=status.value)]

    def list_by_category(self, category: str) -> list[Document]:
        return [self._to_entity(r) for r in DocumentModel.objects.filter(category=category)]

    @staticmethod
    def _to_entity(record: DocumentModel) -> Document:
        return Document(
            id=record.id,
            filename=record.filename,
            content_type=record.content_type,
            category=record.category,
            metadata=record.metadata,
            status=DocumentStatus(record.status),
            storage_path=record.storage_path,
            created_at=record.created_at,
        )

    @staticmethod
    def _to_record(document: Document) -> dict:
        return {
            "filename": document.filename,
            "content_type": document.content_type,
            "category": document.category,
            "metadata": document.metadata,
            "status": document.status.value,
            "storage_path": document.storage_path,
        }
