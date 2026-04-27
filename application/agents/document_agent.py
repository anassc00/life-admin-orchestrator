"""DocumentAgentOrchestrator — classifies, enriches, and archives documents.

Node flow:
  register → classify → extract_metadata → archive → END
"""
from typing import Any, TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph

from application.dtos.document import (
    ArchiveDocumentCommand,
    ClassifyDocumentCommand,
    ExtractMetadataCommand,
    RegisterDocumentCommand,
)
from application.use_cases.document.archive_document import ArchiveDocumentUseCase
from application.use_cases.document.classify_document import ClassifyDocumentUseCase
from application.use_cases.document.extract_metadata import ExtractMetadataUseCase
from application.use_cases.document.register_document import RegisterDocumentUseCase


class DocumentAgentState(TypedDict):
    filename: str
    content_type: str
    raw_content: str
    document_id: UUID | None
    category: str | None
    metadata: dict[str, Any]
    storage_path: str | None
    error: str | None


class DocumentAgentOrchestrator:

    def __init__(
        self,
        register_uc: RegisterDocumentUseCase,
        classify_uc: ClassifyDocumentUseCase,
        extract_metadata_uc: ExtractMetadataUseCase,
        archive_uc: ArchiveDocumentUseCase,
    ) -> None:
        self._register_uc = register_uc
        self._classify_uc = classify_uc
        self._extract_metadata_uc = extract_metadata_uc
        self._archive_uc = archive_uc
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph: StateGraph = StateGraph(DocumentAgentState)
        graph.add_node("register", self._register)
        graph.add_node("classify", self._classify)
        graph.add_node("extract_metadata", self._extract_metadata)
        graph.add_node("archive", self._archive)

        graph.set_entry_point("register")
        graph.add_edge("register", "classify")
        graph.add_edge("classify", "extract_metadata")
        graph.add_edge("extract_metadata", "archive")
        graph.add_edge("archive", END)

        return graph.compile()

    def _register(self, state: DocumentAgentState) -> DocumentAgentState:
        result = self._register_uc.execute(
            RegisterDocumentCommand(
                filename=state["filename"],
                content_type=state["content_type"],
            )
        )
        return {**state, "document_id": result.document_id}

    def _classify(self, state: DocumentAgentState) -> DocumentAgentState:
        # Placeholder: LLM determines category from raw_content
        if state.get("document_id"):
            result = self._classify_uc.execute(
                ClassifyDocumentCommand(
                    document_id=state["document_id"],  # type: ignore[arg-type]
                    category=state.get("category") or "uncategorized",
                    metadata=state.get("metadata", {}),
                )
            )
            return {**state, "category": result.category}
        return state

    def _extract_metadata(self, state: DocumentAgentState) -> DocumentAgentState:
        # Placeholder: LLM extracts key-value metadata pairs
        if state.get("document_id"):
            result = self._extract_metadata_uc.execute(
                ExtractMetadataCommand(
                    document_id=state["document_id"],  # type: ignore[arg-type]
                    metadata=state.get("metadata", {}),
                )
            )
            return {**state, "metadata": result.metadata}
        return state

    def _archive(self, state: DocumentAgentState) -> DocumentAgentState:
        if state.get("document_id") and state.get("storage_path"):
            self._archive_uc.execute(
                ArchiveDocumentCommand(
                    document_id=state["document_id"],  # type: ignore[arg-type]
                    storage_path=state["storage_path"],
                )
            )
        return state

    def run(
        self,
        filename: str,
        content_type: str,
        raw_content: str,
        storage_path: str = "",
    ) -> DocumentAgentState:
        initial: DocumentAgentState = {
            "filename": filename,
            "content_type": content_type,
            "raw_content": raw_content,
            "document_id": None,
            "category": None,
            "metadata": {},
            "storage_path": storage_path or None,
            "error": None,
        }
        return self._graph.invoke(initial)  # type: ignore[return-value]
