from uuid import UUID

from ninja import Router

from adapters.api.document.schemas import (
    ArchiveDocumentRequest,
    ClassifyDocumentRequest,
    DocumentArchivedResponseSchema,
    DocumentClassifiedResponseSchema,
    DocumentRegisteredResponseSchema,
    RegisterDocumentRequest,
)
from infrastructure.di import (
    get_archive_document_use_case,
    get_classify_document_use_case,
    get_register_document_use_case,
)

router = Router(tags=["Documents"])


@router.post("/", response=DocumentRegisteredResponseSchema)
def register_document(request, payload: RegisterDocumentRequest):
    uc = get_register_document_use_case()
    return uc.execute(payload.to_command()).model_dump()


@router.post("/{document_id}/classify", response=DocumentClassifiedResponseSchema)
def classify_document(request, document_id: UUID, payload: ClassifyDocumentRequest):
    uc = get_classify_document_use_case()
    return uc.execute(payload.to_command(document_id)).model_dump()


@router.post("/{document_id}/archive", response=DocumentArchivedResponseSchema)
def archive_document(request, document_id: UUID, payload: ArchiveDocumentRequest):
    uc = get_archive_document_use_case()
    return uc.execute(payload.to_command(document_id)).model_dump()
