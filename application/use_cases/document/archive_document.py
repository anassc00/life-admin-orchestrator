from domain.entities.document import DocumentStatus
from domain.exceptions.document import DocumentAlreadyArchivedError, DocumentNotFoundError
from domain.repositories.document import DocumentRepository
from application.dtos.document import ArchiveDocumentCommand, DocumentArchivedResponse


class ArchiveDocumentUseCase:

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._repo = document_repo

    def execute(self, command: ArchiveDocumentCommand) -> DocumentArchivedResponse:
        document = self._repo.get_by_id(command.document_id)
        if document is None:
            raise DocumentNotFoundError(command.document_id)
        if document.status == DocumentStatus.ARCHIVED:
            raise DocumentAlreadyArchivedError(command.document_id)

        archived = document.archive(storage_path=command.storage_path)
        self._repo.save(archived)
        return DocumentArchivedResponse(
            document_id=archived.id,
            storage_path=archived.storage_path,
            status=archived.status,
        )
