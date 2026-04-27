from domain.exceptions.document import DocumentNotFoundError
from domain.repositories.document import DocumentRepository
from application.dtos.document import ClassifyDocumentCommand, DocumentClassifiedResponse


class ClassifyDocumentUseCase:

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._repo = document_repo

    def execute(self, command: ClassifyDocumentCommand) -> DocumentClassifiedResponse:
        document = self._repo.get_by_id(command.document_id)
        if document is None:
            raise DocumentNotFoundError(command.document_id)

        classified = document.classify(
            category=command.category,
            metadata=command.metadata,
        )
        self._repo.save(classified)
        return DocumentClassifiedResponse(
            document_id=classified.id,
            category=classified.category,
            metadata=classified.metadata,
        )
