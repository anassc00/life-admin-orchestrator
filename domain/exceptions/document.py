from uuid import UUID


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: UUID) -> None:
        super().__init__(f"Document {document_id} not found")
        self.document_id = document_id


class DocumentAlreadyArchivedError(Exception):
    def __init__(self, document_id: UUID) -> None:
        super().__init__(f"Document {document_id} is already archived")
        self.document_id = document_id
