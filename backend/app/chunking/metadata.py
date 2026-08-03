from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class MetadataBuilder:
    """
    Builds metadata for every chunk.

    This metadata will later be stored inside Qdrant payload.
    """

    def build(
        self,
        *,
        document_metadata: dict,
        chunk_index: int,
        page: int | None = None,
        section: str | None = None,
    ) -> dict:

        metadata = deepcopy(document_metadata)

        metadata.update(
            {
                "chunk_id": str(uuid4()),
                "chunk_index": chunk_index,
                "page": page,
                "section": section,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

        return metadata