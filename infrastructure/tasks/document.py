from celery import shared_task

from infrastructure.di import (
    get_archive_document_use_case,
    get_classify_document_use_case,
    get_extract_metadata_use_case,
    get_register_document_use_case,
)


@shared_task(name="tasks.document.process_file", bind=True, max_retries=3)
def process_document_task(
    self,
    filename: str,
    content_type: str,
    raw_content: str,
    storage_path: str = "",
) -> dict:
    """Run a new file through the full DocumentAgent pipeline."""
    from application.agents.document_agent import DocumentAgentOrchestrator

    agent = DocumentAgentOrchestrator(
        register_uc=get_register_document_use_case(),
        classify_uc=get_classify_document_use_case(),
        extract_metadata_uc=get_extract_metadata_use_case(),
        archive_uc=get_archive_document_use_case(),
    )
    result = agent.run(
        filename=filename,
        content_type=content_type,
        raw_content=raw_content,
        storage_path=storage_path,
    )
    return {"document_id": str(result.get("document_id")), "error": result.get("error")}
