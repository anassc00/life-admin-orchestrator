from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class DocumentStatus(str, Enum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    ARCHIVED = "archived"


class Document(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    filename: str
    content_type: str
    category: str = ""
    metadata: dict = Field(default_factory=dict)
    status: DocumentStatus = DocumentStatus.PENDING
    storage_path: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def classify(self, category: str, metadata: dict) -> "Document":
        return self.model_copy(
            update={
                "category": category,
                "metadata": metadata,
                "status": DocumentStatus.CLASSIFIED,
            }
        )

    def archive(self, storage_path: str) -> "Document":
        return self.model_copy(
            update={
                "storage_path": storage_path,
                "status": DocumentStatus.ARCHIVED,
            }
        )
