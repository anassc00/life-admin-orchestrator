from domain.entities.document import Document
from domain.repositories.document import DocumentRepository
from application.dtos.document import DocumentRegisteredResponse, RegisterDocumentCommand


class RegisterDocumentUseCase:

    def __init__(self, document_repo: DocumentRepository) -> None:
        self._repo = document_repo

    def execute(self, command: RegisterDocumentCommand) -> DocumentRegisteredResponse:
        document = Document(
            filename=command.filename,
            content_type=command.content_type,
        )
        self._repo.save(document)
        return DocumentRegisteredResponse(
            document_id=document.id,
            filename=document.filename,
            status=document.status,
        )
