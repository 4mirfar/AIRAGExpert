from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    """
    Represents a source document inside the RAG pipeline.

    Lifecycle:
        Upload
            ↓
        Parse
            ↓
        Chunk
            ↓
        Embed
            ↓
        Store
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    document_id: str

    filename: str

    stored_name: str

    path: str

    extension: str

    mime_type: str

    size: int

    category: str

    text: str = ""

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def has_text(self) -> bool:
        return bool(self.text.strip())

    @property
    def text_length(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return len(self.text.split())

    def update_text(self, text: str) -> None:
        self.text = text
        self.updated_at = datetime.utcnow()

    def add_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value