from application.dtos.document import ExtractMetadataCommand, MetadataExtractedResponse
from domain.exceptions.document import DocumentNotFoundError
from domain.repositories.document import DocumentRepository


class ExtractMetadataUseCase:
    def __init__(self, document_repo: DocumentRepository) -> None:
        self._repo = document_repo

    def execute(self, command: ExtractMetadataCommand) -> MetadataExtractedResponse:
        document = self._repo.get_by_id(command.document_id)
        if document is None:
            raise DocumentNotFoundError(command.document_id)

        merged_metadata = {**document.metadata, **command.metadata}
        updated = document.model_copy(update={"metadata": merged_metadata})
        self._repo.save(updated)
        return MetadataExtractedResponse(
            document_id=updated.id,
            metadata=updated.metadata,
        )
