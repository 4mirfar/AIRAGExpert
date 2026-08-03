from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Chunk(BaseModel):
    """
    Represents a single document chunk.

    This model is shared across:
        - Chunking
        - Embedding
        - Qdrant
        - Retrieval
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    chunk_id: str

    document_id: str

    chunk_index: int

    text: str

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    embedding: list[float] | None = None

    token_count: int | None = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    @property
    def has_embedding(self) -> bool:
        return self.embedding is not None

    @property
    def embedding_dimension(self) -> int:
        if self.embedding is None:
            return 0

        return len(self.embedding)